"""E2E test: verify that adding contradicting has_*/lacks_* facts is prevented.

Scenario: lab5_inheritance has lacks_ability(penguin, ability_fly).
When we try to add has_ability(penguin, ability_fly), the system must
show an error and refuse the addition.
"""
import sys
import json
import traceback
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"


def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            page.wait_for_timeout(delay)


def api_request(method, path, body=None, token=None):
    url = f"{API_URL}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        raise RuntimeError(f"API {method} {path} -> {e.code}: {body_text}")


def step_register_and_login(page):
    """Register a test user and log in."""
    print("TEST: Register and login")
    goto_with_retry(page, f"{BASE_URL}/register")
    page.wait_for_timeout(1000)

    inputs = page.locator("input")
    inputs.nth(0).fill("testuser_lacks")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_lacks")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def step_create_workspace_and_load_scenario(page):
    """Create workspace with lab5_inheritance scenario."""
    print("TEST: Create workspace with lab5_inheritance")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    new_btn = page.locator(
        'button:has-text("Новый"), button:has-text("Создать"), a:has-text("Новый")'
    )
    if new_btn.count() > 0:
        new_btn.first.click()
        page.wait_for_timeout(3000)

    scenario_select = page.locator("select.rounded-lg")
    if scenario_select.count() > 0:
        scenario_select.first.select_option("lab5_inheritance")
        page.wait_for_timeout(500)

    load_btn = page.locator('button:has-text("Загрузить")')
    if load_btn.count() > 0:
        load_btn.first.click()
        page.wait_for_timeout(3000)

    assert "/workspace/" in page.url, f"Not on workspace page: {page.url}"
    print("  PASS")
    return page.url.split("/workspace/")[-1].split("/")[0].split("?")[0]


def step_add_contradictory_fact(page, session_id):
    """Try adding has_ability(penguin, ability_fly) — must be rejected with error."""
    print("TEST: Add contradictory fact has_ability(penguin, ability_fly) — expect error")

    # Switch to Fact tab in Network Editor
    fact_tab = page.locator("button:has-text('Fact')")
    fact_tab.click()
    page.wait_for_timeout(1000)

    # The predicate select appears after switching to Fact tab
    # Find select that contains has_ability option
    pred_select = page.locator("text=Выберите предикат").locator("..").locator("select")
    if pred_select.count() == 0:
        # fallback: find select right after "Выберите предикат" text
        pred_select = page.locator("select").last
    pred_select.select_option(label="has_ability (арность: 2)")
    page.wait_for_timeout(500)

    # Use manual input (Способ 2) to enter concept IDs
    manual_input = page.locator("input[placeholder='concept1, concept2, ...']")
    manual_input.fill("penguin, ability_fly")
    page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_lacks_before_add.png")

    # Click "Добавить факт"
    add_btn = page.locator("button:has-text('Добавить факт')")
    assert add_btn.count() > 0, "Add fact button not found"
    add_btn.first.click()
    page.wait_for_timeout(2000)

    page.screenshot(path="/tmp/e2e_lacks_after_add_fact.png")

    # Verify error message is shown in the red error div
    error_div = page.locator("div.bg-red-50")
    assert error_div.count() > 0, "Expected red error div about contradiction"
    error_text = error_div.first.text_content() or ""
    assert "Противоречие" in error_text, f"Expected 'Противоречие' in error, got: {error_text}"
    print(f"  Error shown: {error_text}")
    print("  PASS")


def step_create_condition_formulas(page):
    """Create two condition formulas: has_ability and lacks_ability for penguin/fly."""
    print("TEST: Create condition formulas")

    # Create cond_penguin_flies: FactAtom("has_ability", penguin, ability_fly)
    new_btn = page.locator("button:has-text('Новая формула')")
    if new_btn.count() > 0:
        new_btn.first.click()
        page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    if name_input.count() > 0:
        name_input.fill("cond_penguin_flies")

    # Select predicate has_ability
    selects = page.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            txt = options.nth(j).text_content() or ""
            if "has_ability" in txt:
                sel.select_option(index=j)
                page.wait_for_timeout(300)
                break

    # Select args: penguin, ability_fly
    page.wait_for_timeout(500)
    selects = page.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            txt = options.nth(j).text_content() or ""
            if "penguin" in txt.lower():
                sel.select_option(index=j)
                page.wait_for_timeout(200)
                break

    selects = page.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            txt = options.nth(j).text_content() or ""
            if "ability_fly" in txt.lower():
                sel.select_option(index=j)
                page.wait_for_timeout(200)
                break

    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    # Create cond_penguin_no_fly: FactAtom("lacks_ability", penguin, ability_fly)
    new_btn = page.locator("button:has-text('Новая формула')")
    if new_btn.count() > 0:
        new_btn.first.click()
        page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    if name_input.count() > 0:
        name_input.fill("cond_penguin_no_fly")

    selects = page.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            txt = options.nth(j).text_content() or ""
            if "lacks_ability" in txt:
                sel.select_option(index=j)
                page.wait_for_timeout(300)
                break

    page.wait_for_timeout(500)
    selects = page.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            txt = options.nth(j).text_content() or ""
            if "penguin" in txt.lower():
                sel.select_option(index=j)
                page.wait_for_timeout(200)
                break

    selects = page.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            txt = options.nth(j).text_content() or ""
            if "ability_fly" in txt.lower():
                sel.select_option(index=j)
                page.wait_for_timeout(200)
                break

    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_lacks_formulas_created.png")
    print("  PASS")


def step_check_detects_contradiction(page):
    """Run check with both conditions and verify contradiction is detected."""
    print("TEST: Check detects contradiction (lacks vs has)")

    # Select both conditions as checkboxes
    flies_cb = page.locator("label:has-text('cond_penguin_flies') input[type='checkbox']")
    nofly_cb = page.locator("label:has-text('cond_penguin_no_fly') input[type='checkbox']")

    if flies_cb.count() > 0:
        flies_cb.first.check()
        page.wait_for_timeout(200)
    if nofly_cb.count() > 0:
        nofly_cb.first.check()
        page.wait_for_timeout(200)

    # Click "Проверить"
    check_btn = page.locator("button:has-text('Проверить')")
    assert check_btn.count() > 0, "Проверить button not found"
    check_btn.first.click()
    page.wait_for_timeout(2000)

    page.screenshot(path="/tmp/e2e_lacks_check_result.png")

    # With the fix: has_ability is TRUE, lacks_ability is FALSE → "Есть нарушения"
    banner_fail = page.locator("text=Есть нарушения")
    banner_ok = page.locator("text=Все условия выполнены")

    if banner_ok.count() > 0:
        print("  FAIL: Both conditions TRUE — contradiction not detected!")
        assert False, "lacks_ability should be FALSE when has_ability exists"

    assert banner_fail.count() > 0, "Expected 'Есть нарушения' banner"

    # Verify: cond_penguin_flies = TRUE, cond_penguin_no_fly = FALSE
    result_items = page.locator(".space-y-1 .flex")
    for i in range(result_items.count()):
        text = result_items.nth(i).text_content() or ""
        print(f"  Result item: {text}")

    print("  Contradiction detected correctly!")
    print("  PASS")


def main():
    passed = 0
    failed = 0
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("requestfailed", lambda req: console_msgs.append(f"[FAILED] {req.method} {req.url}"))

        # Warmup
        print("Warming up...")
        goto_with_retry(page, BASE_URL)
        goto_with_retry(page, f"{BASE_URL}/login")
        goto_with_retry(page, f"{BASE_URL}/register")
        print("Warmup done.\n")

        session_id = [None]

        def run_login():
            step_register_and_login(page)

        def run_workspace():
            session_id[0] = step_create_workspace_and_load_scenario(page)

        def run_add_fact():
            step_add_contradictory_fact(page, session_id[0])

        tests = [
            ("register_and_login", run_login),
            ("create_workspace", run_workspace),
            ("add_contradictory_fact", run_add_fact),
        ]

        for name, fn in tests:
            try:
                fn()
                passed += 1
                results.append((name, "PASS"))
            except Exception as e:
                page.screenshot(path=f"/tmp/e2e_lacks_{name}_fail.png")
                print(f"  FAIL: {e}")
                traceback.print_exc()
                failed += 1
                results.append((name, f"FAIL: {e}"))

        errors = [m for m in console_msgs if "[error]" in m.lower() or "[FAILED]" in m]
        if errors:
            print(f"\nBrowser console errors ({len(errors)}):")
            for e in errors[:10]:
                print(f"  {e}")

        browser.close()

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    for name, result in results:
        print(f"  {name}: {result}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
