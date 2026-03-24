"""E2E test: editing scenario variable domain definition."""
import requests
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
API = "http://localhost:8000"


def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            print(f"  Page not ready (attempt {attempt+1}), retrying...")
            page.wait_for_timeout(delay)


# --- Register + get token via API ---
reg_resp = requests.post(f"{API}/api/auth/register", json={"username": "test_scenvar_ed9", "password": "pass1234"})
if reg_resp.status_code == 409:
    reg_resp = requests.post(f"{API}/api/auth/login", json={"username": "test_scenvar_ed9", "password": "pass1234"})
token = reg_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# --- Create workspace with lab5_inheritance ---
ws_resp = requests.post(f"{API}/api/session/load", json={"scenario": "lab5_inheritance", "derive": True}, headers=headers)
ws_data = ws_resp.json()
session_id = ws_data["session_id"]
print(f"Created workspace: {session_id}")
print(f"Variables: {[v['name'] for v in ws_data.get('variables', [])]}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    console_msgs = []

    page = browser.new_page()
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

    # Login in browser
    goto_with_retry(page, f"{BASE}/login")
    page.fill('input[placeholder="Имя пользователя"]', "test_scenvar_ed9")
    page.fill('input[placeholder="Пароль"]', "pass1234")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # Navigate to workspace
    goto_with_retry(page, f"{BASE}/workspace/{session_id}")
    page.wait_for_timeout(3000)

    page.screenshot(path="/tmp/scenvar_before_edit.png", full_page=True)

    # --- Verify scenario variables are shown ---
    scenario_label = page.locator("text=Сценарий")
    assert scenario_label.count() > 0, "Scenario section not found"
    print("OK: Scenario section found")

    # Check edit buttons exist next to scenario variables
    edit_buttons = page.locator('button[title="Редактировать"]')
    assert edit_buttons.count() >= 2, f"Expected at least 2 edit buttons for scenario vars, got {edit_buttons.count()}"
    print(f"OK: Found {edit_buttons.count()} edit buttons")

    # --- Click edit on first scenario variable ---
    edit_buttons.first.click()
    page.wait_for_timeout(500)
    page.screenshot(path="/tmp/scenvar_edit_form.png", full_page=True)

    # Check edit form appeared
    edit_form = page.locator("text=Редактирование:")
    assert edit_form.count() > 0, "Edit form not shown after clicking pencil"
    print("OK: Edit form opened")

    # --- Add a new enum value ---
    add_input = page.locator('input[placeholder="Добавить значение"]')
    assert add_input.count() > 0, "No enum value input found"

    add_input.fill("eagle")
    page.locator("button", has_text="+").first.click()
    page.wait_for_timeout(300)
    print("OK: Added 'eagle' to enum values")

    # Save the edit
    save_btn = page.locator("button", has_text="Сохранить")
    save_btn.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/scenvar_after_edit.png", full_page=True)

    # Verify the new value appears in the dropdown
    selects = page.locator("select")
    found_eagle = False
    for i in range(selects.count()):
        options_text = selects.nth(i).inner_html()
        if "eagle" in options_text:
            found_eagle = True
            break
    assert found_eagle, "New value 'eagle' not found in any dropdown after edit"
    print("OK: 'eagle' value appears in dropdown after edit")

    # --- Click edit again to verify override persists ---
    edit_buttons = page.locator('button[title="Редактировать"]')
    edit_buttons.first.click()
    page.wait_for_timeout(500)

    # Check that eagle is shown as a tag in the edit form
    eagle_tag = page.locator("text=eagle")
    assert eagle_tag.count() > 0, "Override not persisted - 'eagle' not in edit form"
    print("OK: Override persisted - 'eagle' shown in edit form")

    # Cancel
    cancel_btn = page.locator("button", has_text="Отмена")
    cancel_btn.click()
    page.wait_for_timeout(300)

    # Print diagnostics
    errors = [m for m in console_msgs if "[error]" in m.lower() or m.startswith("[4") or m.startswith("[5")]
    if errors:
        print("\nConsole errors:")
        for e in errors:
            print(f"  {e}")

    browser.close()
    print("\nAll tests passed!")
