"""E2E test: user variables appear in formula builder TermPicker dropdown."""
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
USERNAME = "test_formula_vars1"
reg_resp = requests.post(f"{API}/api/auth/register", json={"username": USERNAME, "password": "pass1234"})
if reg_resp.status_code == 409:
    reg_resp = requests.post(f"{API}/api/auth/login", json={"username": USERNAME, "password": "pass1234"})
token = reg_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# --- Create workspace with lab5_inheritance ---
ws_resp = requests.post(f"{API}/api/session/load", json={"scenario": "lab5_inheritance", "derive": True}, headers=headers)
ws_data = ws_resp.json()
session_id = ws_data["session_id"]
scenario_var_names = [v["name"] for v in ws_data.get("variables", [])]
print(f"Created workspace: {session_id}")
print(f"Scenario variables: {scenario_var_names}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    console_msgs = []

    page = browser.new_page()
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

    # Login in browser
    goto_with_retry(page, f"{BASE}/login")
    page.fill('input[placeholder="Имя пользователя"]', USERNAME)
    page.fill('input[placeholder="Пароль"]', "pass1234")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # Navigate to workspace
    goto_with_retry(page, f"{BASE}/workspace/{session_id}")
    page.wait_for_timeout(3000)

    # --- Step 1: Open formula builder and check that only scenario vars are present ---
    new_formula_btn = page.locator("text=+ Новая формула")
    assert new_formula_btn.count() > 0, "No '+ Новая формула' button found"
    new_formula_btn.click()
    page.wait_for_timeout(500)

    # Fill formula name
    formula_name_input = page.locator('input[placeholder="Имя формулы"]')
    formula_name_input.fill("test_formula")

    # Switch first arg TermPicker to Variable mode (click "V" button)
    # First select a predicate so args appear
    predicate_select = page.locator("select").filter(has_text="Предикат...")
    if predicate_select.count() > 0:
        # Select the first predicate option
        options = predicate_select.locator("option")
        for i in range(options.count()):
            val = options.nth(i).get_attribute("value")
            if val:
                predicate_select.select_option(val)
                break
        page.wait_for_timeout(300)

    # Find and click "V" button on first TermPicker
    v_buttons = page.locator("button", has_text="V")
    if v_buttons.count() > 0:
        v_buttons.first.click()
        page.wait_for_timeout(300)

    page.screenshot(path="/tmp/formula_vars_before.png", full_page=True)

    # Check the variable dropdown - should have scenario vars
    # Find the select inside the TermPicker that is now in variable mode
    var_selects = page.locator("select")
    initial_var_options = set()
    for i in range(var_selects.count()):
        html = var_selects.nth(i).inner_html()
        for vn in scenario_var_names:
            if vn in html:
                initial_var_options.add(vn)
    print(f"Scenario vars found in TermPicker: {initial_var_options}")
    assert len(initial_var_options) > 0, "No scenario variables found in TermPicker dropdown"
    print("OK: Scenario variables appear in formula TermPicker")

    # Cancel the formula creation
    cancel_btn = page.locator("button", has_text="Отмена")
    cancel_btn.last.click()
    page.wait_for_timeout(500)

    # --- Step 2: Create a user variable via the VariableEditorPanel ---
    add_var_btn = page.locator("button", has_text="Новая переменная")
    assert add_var_btn.count() > 0, "No '+ Новая переменная' button found"
    add_var_btn.click()
    page.wait_for_timeout(500)

    # Fill in new variable name
    name_input = page.locator('input[placeholder="Имя переменной"]')
    assert name_input.count() > 0, "Variable name input not found"
    name_input.fill("my_test_var")

    # Add an enum value
    val_input = page.locator('input[placeholder="Добавить значение"]')
    if val_input.count() > 0:
        val_input.fill("val1")
        page.locator("button", has_text="+").first.click()
        page.wait_for_timeout(300)

    # Create the variable
    create_btn = page.locator("button", has_text="Создать")
    create_btn.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/formula_vars_after_create.png", full_page=True)
    print("OK: User variable 'my_test_var' created")

    # --- Step 3: Open formula builder again and check user var appears ---
    new_formula_btn = page.locator("text=+ Новая формула")
    new_formula_btn.click()
    page.wait_for_timeout(500)

    formula_name_input = page.locator('input[placeholder="Имя формулы"]')
    formula_name_input.fill("test_formula2")

    # Select predicate
    predicate_select = page.locator("select").filter(has_text="Предикат...")
    if predicate_select.count() > 0:
        options = predicate_select.locator("option")
        for i in range(options.count()):
            val = options.nth(i).get_attribute("value")
            if val:
                predicate_select.select_option(val)
                break
        page.wait_for_timeout(300)

    # Switch TermPicker to Variable mode
    v_buttons = page.locator("button", has_text="V")
    if v_buttons.count() > 0:
        v_buttons.first.click()
        page.wait_for_timeout(300)

    page.screenshot(path="/tmp/formula_vars_after.png", full_page=True)

    # Check that user variable appears in the dropdown
    var_selects = page.locator("select")
    found_user_var = False
    found_optgroup = False
    for i in range(var_selects.count()):
        html = var_selects.nth(i).inner_html()
        if "my_test_var" in html:
            found_user_var = True
            if "Пользовательские" in html:
                found_optgroup = True
            break

    assert found_user_var, "User variable 'my_test_var' not found in formula TermPicker dropdown"
    print("OK: User variable 'my_test_var' appears in formula TermPicker")

    if found_optgroup:
        print("OK: Variables are grouped with optgroup (Сценарий / Пользовательские)")
    else:
        print("WARN: No optgroup grouping detected (may be single-origin list)")

    # Cancel formula
    cancel_btn = page.locator("button", has_text="Отмена")
    cancel_btn.last.click()
    page.wait_for_timeout(300)

    # Print diagnostics
    errors = [m for m in console_msgs if "[error]" in m.lower() or m.startswith("[4") or m.startswith("[5")]
    if errors:
        print("\nConsole errors:")
        for e in errors:
            print(f"  {e}")

    browser.close()
    print("\nAll tests passed!")
