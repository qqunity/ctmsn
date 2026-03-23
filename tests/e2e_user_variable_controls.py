"""E2E test: user variables show interactive controls (enum dropdown, range input, text input).

Verifies the fix for: user variables showing static "enum" text instead of interactive controls.
Tests all three domain types: enum (select dropdown), range (number input), predicate (text input).
"""
import random
import string
import json
import urllib.request
from playwright.sync_api import sync_playwright

API_BASE = "http://127.0.0.1:8000"
WEB_BASE = "http://localhost:3000"
USERNAME = "test_uvar_" + "".join(random.choices(string.ascii_lowercase, k=5))
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


# Step 1: Setup via API — register, create workspace, add user variables
print("1. Setting up via API...")
auth = api_post("/api/auth/register", {"username": USERNAME, "password": PASSWORD})
token = auth["access_token"]
print(f"   Registered: {USERNAME}")

load_resp = api_post("/api/session/load", {"scenario": "fishing", "derive": True}, token)
session_id = load_resp["session_id"]
print(f"   Workspace: {session_id}")

# Create enum user variable — must have top-level "values" field in response
create_resp = api_post(f"/api/workspaces/{session_id}/variables", {
    "name": "test_enum_var",
    "domain_type": "enum",
    "domain": {"values": ["alpha", "beta", "gamma"]}
}, token)
assert "values" in create_resp, f"API response missing 'values' field! Got: {list(create_resp.keys())}"
assert create_resp["values"] == ["alpha", "beta", "gamma"], f"Wrong values: {create_resp['values']}"
print("   API: enum variable has top-level 'values' - PASS")

# Create range user variable — must have top-level "min"/"max" fields
range_resp = api_post(f"/api/workspaces/{session_id}/variables", {
    "name": "test_range_var",
    "domain_type": "range",
    "domain": {"min": 0, "max": 100}
}, token)
assert "min" in range_resp, f"API response missing 'min' field!"
assert "max" in range_resp, f"API response missing 'max' field!"
print(f"   API: range variable has min={range_resp['min']}, max={range_resp['max']} - PASS")

# Create predicate user variable
api_post(f"/api/workspaces/{session_id}/variables", {
    "name": "test_pred_var",
    "domain_type": "predicate",
    "domain": {"name": "knows"}
}, token)
print("   API: predicate variable created - PASS")

# Step 2: Open workspace in browser and verify interactive controls
print("\n2. Opening workspace in browser...")
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

    # Scroll to variables section
    var_heading = page.locator('text=Переменные')
    if var_heading.count() > 0:
        var_heading.first.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

    # 3. "Пользовательские" section must exist
    print("\n3. Checking user variables section...")
    user_section = page.locator('text=Пользовательские')
    assert user_section.count() > 0, "'Пользовательские' section not found!"
    print("   'Пользовательские' section found")

    # 4. Enum variable must have a <select> dropdown
    print("\n4. Checking enum variable (test_enum_var)...")
    enum_label = page.locator('label:has-text("test_enum_var")')
    assert enum_label.count() > 0, "label 'test_enum_var' not found!"
    enum_select = enum_label.locator('..').locator('select')
    assert enum_select.count() > 0, "No <select> for enum user variable!"
    options = [o.text_content() for o in enum_select.locator('option').all()]
    assert "alpha" in options, f"'alpha' missing from options: {options}"
    assert "beta" in options, f"'beta' missing from options: {options}"
    assert "gamma" in options, f"'gamma' missing from options: {options}"
    print(f"   PASS: dropdown with options {options}")

    # 5. Range variable must have <input type="number">
    print("\n5. Checking range variable (test_range_var)...")
    range_label = page.locator('label:has-text("test_range_var")')
    assert range_label.count() > 0, "label 'test_range_var' not found!"
    range_input = range_label.locator('..').locator('input[type="number"]')
    assert range_input.count() > 0, "No <input type=number> for range user variable!"
    print("   PASS: number input present")

    # 6. Predicate variable must have <input type="text">
    print("\n6. Checking predicate variable (test_pred_var)...")
    pred_label = page.locator('label:has-text("test_pred_var")')
    assert pred_label.count() > 0, "label 'test_pred_var' not found!"
    pred_input = pred_label.locator('..').locator('input[type="text"]')
    assert pred_input.count() > 0, "No <input type=text> for predicate user variable!"
    print("   PASS: text input present")

    # 7. No static domain_type text ("enum", "range", "predicate") shown as labels
    print("\n7. Checking no static domain_type text shown...")
    static_spans = page.locator('.text-gray-400')
    static_texts = [s.text_content().strip() for s in static_spans.all()]
    bad_texts = [t for t in static_texts if t in ("enum", "range", "predicate")]
    assert not bad_texts, f"Found static domain type texts: {bad_texts}"
    print("   PASS: no static domain_type text")

    # 8. Setting enum value should not produce API errors
    print("\n8. Setting enum variable value...")
    enum_select.select_option("beta")
    page.wait_for_timeout(2000)
    errors_after_set = [m for m in console_msgs if m.startswith("[HTTP 4") or m.startswith("[HTTP 5")]
    assert not errors_after_set, f"API errors after setting value: {errors_after_set}"
    print("   PASS: value set without API errors")

    # 9. Delete buttons exist for all user vars
    print("\n9. Checking delete buttons...")
    delete_btns = page.locator('button[title="Удалить"]')
    assert delete_btns.count() >= 3, f"Expected >= 3 delete buttons, found {delete_btns.count()}"
    print(f"   PASS: {delete_btns.count()} delete buttons found")

    print("\n=== ALL TESTS PASSED ===")
    browser.close()
