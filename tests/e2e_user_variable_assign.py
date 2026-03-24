"""E2E test: user variable value assignment works (no 'Unknown variable' error).

Verifies the fix for: selecting a value for a user-created variable produced
"Unknown variable 'X'" because set_variable only checked scenario variables.
"""
import random
import string
import json
import urllib.request
from playwright.sync_api import sync_playwright

API_BASE = "http://127.0.0.1:8000"
WEB_BASE = "http://localhost:3000"
USERNAME = "test_uva_" + "".join(random.choices(string.ascii_lowercase, k=5))
PASSWORD = "testpass123"


def api_post(path, data, token=None):
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{API_BASE}{path}", data=body, headers=headers, method="POST")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            page.wait_for_timeout(delay)


# Step 1: Setup via API
print("1. Setting up via API...")
auth = api_post("/api/auth/register", {"username": USERNAME, "password": PASSWORD})
token = auth["access_token"]
print(f"   Registered: {USERNAME}")

# Load fishing scenario (has concepts like animal, Plants in graph)
load_resp = api_post("/api/session/load", {"scenario": "fishing", "derive": True}, token)
session_id = load_resp["session_id"]
print(f"   Workspace: {session_id}")

# Create user variable with concept-based enum domain (like the user's "Kingdom" example)
create_resp = api_post(f"/api/workspaces/{session_id}/variables", {
    "name": "Kingdom",
    "domain_type": "enum",
    "domain": {"values": ["animal", "Plants"]}
}, token)
print(f"   Created variable 'Kingdom' with domain: {create_resp.get('values')}")

# Step 2: Verify via API that setting the variable works
print("\n2. Testing set_variable API directly...")
try:
    set_resp = api_post("/api/session/set_variable", {
        "session_id": session_id,
        "variable": "Kingdom",
        "value": "animal",
    }, token)
    print("   API set_variable('Kingdom', 'animal') - PASS")
except Exception as e:
    print(f"   FAIL: {e}")
    raise

# Unset to test via UI
api_post("/api/session/set_variable", {
    "session_id": session_id,
    "variable": "Kingdom",
    "value": "",
}, token)

# Step 3: Test via browser
print("\n3. Testing in browser...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("response", lambda res: console_msgs.append(f"[HTTP {res.status}] {res.url}") if res.status >= 400 else None)

    # Login
    goto_with_retry(page, f"{WEB_BASE}/login")
    page.wait_for_selector('input[placeholder="Имя пользователя"]')
    page.fill('input[placeholder="Имя пользователя"]', USERNAME)
    page.fill('input[placeholder="Пароль"]', PASSWORD)
    page.click('button:has-text("Войти")')
    page.wait_for_url("**/workspaces", timeout=10000)
    print("   Logged in")

    # Navigate to workspace
    goto_with_retry(page, f"{WEB_BASE}/workspace/{session_id}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    print("   Workspace loaded")

    # Find Kingdom variable and its dropdown
    kingdom_label = page.locator('label:has-text("Kingdom")')
    assert kingdom_label.count() > 0, "label 'Kingdom' not found!"

    kingdom_select = kingdom_label.locator('..').locator('select')
    assert kingdom_select.count() > 0, "No <select> for Kingdom variable!"

    options = [o.text_content() for o in kingdom_select.locator('option').all()]
    print(f"   Kingdom dropdown options: {options}")
    assert "animal" in options, f"'animal' missing from options: {options}"
    assert "Plants" in options, f"'Plants' missing from options: {options}"

    # Select a value
    print("\n4. Setting Kingdom = animal via UI...")

    kingdom_select.select_option("animal")
    page.wait_for_timeout(3000)

    # Check for HTTP errors
    errors = [m for m in console_msgs if m.startswith("[HTTP 4") or m.startswith("[HTTP 5")]
    assert not errors, f"API errors after setting value: {errors}"

    # Re-locate the select after React re-render
    page.wait_for_timeout(500)
    kingdom_label2 = page.locator('label:has-text("Kingdom")')
    kingdom_select2 = kingdom_label2.locator('..').locator('select')
    selected_value = kingdom_select2.input_value()
    assert selected_value == "animal", f"Expected 'animal', got '{selected_value}'"
    print("   PASS: Kingdom = animal set successfully, no errors")

    # Test switching to another value
    print("\n5. Switching Kingdom = Plants...")
    kingdom_select.select_option("Plants")
    page.wait_for_timeout(2000)
    errors2 = [m for m in console_msgs if m.startswith("[HTTP 4") or m.startswith("[HTTP 5")]
    assert not errors2, f"API errors: {errors2}"
    assert kingdom_select.input_value() == "Plants"
    print("   PASS: Kingdom = Plants set successfully")

    # Test unsetting
    print("\n6. Unsetting Kingdom...")
    kingdom_select.select_option("")
    page.wait_for_timeout(2000)
    errors3 = [m for m in console_msgs if m.startswith("[HTTP 4") or m.startswith("[HTTP 5")]
    assert not errors3, f"API errors: {errors3}"
    print("   PASS: Kingdom unset successfully")

    print("\n=== ALL TESTS PASSED ===")
    browser.close()
