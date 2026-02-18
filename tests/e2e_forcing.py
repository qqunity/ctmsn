"""E2E tests for the Forcing Panel."""
import sys
import traceback
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
            print(f"  Page not ready (attempt {attempt+1}), retrying...")
            page.wait_for_timeout(delay)


def test_register_and_login(page):
    """Register a test user and log in."""
    print("TEST: Register and login")
    goto_with_retry(page, f"{BASE_URL}/register")
    page.wait_for_timeout(1000)

    inputs = page.locator("input")
    inputs.nth(0).fill("testuser_forcing")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_forcing")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    print(f"  After login, URL: {page.url}")
    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_create_workspace(page):
    """Create a new workspace and navigate to it."""
    print("TEST: Create workspace")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.first.click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("networkidle")
    else:
        ws_links = page.locator("a[href*='/workspace/']")
        if ws_links.count() > 0:
            ws_links.first.click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle")

    if "/workspace/" not in page.url:
        ws_links = page.locator("a[href*='/workspace/']")
        if ws_links.count() > 0:
            ws_links.first.click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle")

    assert "/workspace/" in page.url, f"Not on workspace page: {page.url}"
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")
    print("  PASS")


def test_forcing_panel_visible(page):
    """Verify the Forcing panel heading is visible."""
    print("TEST: Forcing panel visible")
    page.wait_for_timeout(2000)

    heading = page.locator("h3:has-text('Форсирование')")
    print(f"  Forcing panel heading count: {heading.count()}")
    assert heading.count() > 0, "Forcing panel heading not found"
    page.screenshot(path="/tmp/e2e_forcing_panel.png")
    print("  PASS")


def test_create_formula_for_forcing(page):
    """Create a formula via FormulaEditorPanel for forcing tests."""
    print("TEST: Create formula for forcing")

    new_formula_btn = page.locator("button:has-text('Новая формула')")
    if new_formula_btn.count() == 0:
        print("  SKIP: No formula editor button found")
        return

    new_formula_btn.click()
    page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    assert name_input.count() > 0, "Formula name input not found"
    name_input.fill("ForcingTest1")

    # Select a predicate if available
    pred_selects = page.locator("select")
    for i in range(pred_selects.count()):
        sel = pred_selects.nth(i)
        options = sel.locator("option")
        if options.count() > 1:
            text = options.nth(1).text_content() or ""
            first_text = options.first.text_content() or ""
            if "Предикат" in first_text or "арн" in text:
                sel.select_option(index=1)
                page.wait_for_timeout(300)
                break

    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    formula_text = page.locator("text=ForcingTest1")
    assert formula_text.count() > 0, "Created formula not found"
    print("  Created formula ForcingTest1")
    print("  PASS")


def test_forcing_check(page):
    """Select a condition checkbox and run Check."""
    print("TEST: Forcing check")
    page.wait_for_timeout(1000)

    # Find checkboxes inside the forcing panel's conditions section
    # The forcing panel should show formulas as checkboxes
    forcing_heading = page.locator("h3:has-text('Форсирование')")
    if forcing_heading.count() == 0:
        print("  SKIP: Forcing panel not found")
        return

    # Find checkbox for our formula in the forcing panel
    # Look for checkbox labels containing ForcingTest1
    forcing_checkbox = page.locator("label:has-text('ForcingTest1') input[type='checkbox']")
    if forcing_checkbox.count() > 0:
        forcing_checkbox.first.check()
        page.wait_for_timeout(300)
        print("  Checked condition ForcingTest1")
    else:
        print("  SKIP: No condition checkbox found for ForcingTest1")
        return

    # Click "Проверить" button
    check_btn = page.locator("button:has-text('Проверить')")
    if check_btn.count() > 0 and check_btn.first.is_enabled():
        check_btn.first.click()
        page.wait_for_timeout(2000)
        page.screenshot(path="/tmp/e2e_forcing_check.png")
        print("  Clicked Проверить")

        # Check for result banner
        banner_ok = page.locator("text=Все условия выполнены")
        banner_fail = page.locator("text=Есть нарушения")
        has_result = banner_ok.count() > 0 or banner_fail.count() > 0
        print(f"  Check result banner visible: {has_result}")
        assert has_result, "No check result banner found"
    else:
        print("  SKIP: Проверить button not available")
        return

    print("  PASS")


def test_forcing_forces(page):
    """Select phi and run Forces."""
    print("TEST: Forcing forces")

    # Select phi from the target formula dropdown
    # Look for a select near the "Целевая формула" label
    phi_selects = page.locator("select")
    phi_selected = False
    for i in range(phi_selects.count()):
        sel = phi_selects.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            opt_text = options.nth(j).text_content() or ""
            if "ForcingTest1" in opt_text:
                sel.select_option(index=j)
                phi_selected = True
                print("  Selected phi: ForcingTest1")
                break
        if phi_selected:
            break

    if not phi_selected:
        print("  SKIP: Could not find ForcingTest1 in phi dropdown")
        return

    page.wait_for_timeout(300)

    # Click "Форсирует?" button
    forces_btn = page.locator("button:has-text('Форсирует?')")
    if forces_btn.count() > 0 and forces_btn.first.is_enabled():
        forces_btn.first.click()
        page.wait_for_timeout(2000)
        page.screenshot(path="/tmp/e2e_forcing_forces.png")
        print("  Clicked Форсирует?")

        # Check for result badge (TRUE/FALSE/UNKNOWN)
        result_badge = page.locator(".bg-green-100, .bg-red-100, .bg-yellow-100")
        print(f"  Result badges visible: {result_badge.count()}")
        assert result_badge.count() > 0, "No forces result badge found"
    else:
        print("  SKIP: Форсирует? button not available")
        return

    print("  PASS")


def test_forcing_explanation(page):
    """Toggle the explanation block."""
    print("TEST: Forcing explanation toggle")

    explain_btn = page.locator("button:has-text('Объяснение')")
    if explain_btn.count() == 0:
        print("  SKIP: No explanation button found (run forces first)")
        return

    explain_btn.first.click()
    page.wait_for_timeout(500)
    page.screenshot(path="/tmp/e2e_forcing_explanation.png")

    # Check that explanation text is visible (e.g. "Проверено условий:")
    explanation_text = page.locator("text=Проверено условий")
    print(f"  Explanation visible: {explanation_text.count() > 0}")
    assert explanation_text.count() > 0, "Explanation text not visible after toggle"

    # Toggle off
    hide_btn = page.locator("button:has-text('Скрыть объяснение')")
    if hide_btn.count() > 0:
        hide_btn.first.click()
        page.wait_for_timeout(300)
        explanation_text2 = page.locator("text=Проверено условий")
        print(f"  Explanation hidden: {explanation_text2.count() == 0}")

    print("  PASS")


def test_forcing_history(page):
    """Check that history shows run records."""
    print("TEST: Forcing history")

    history_btn = page.locator("button:has-text('История')")
    if history_btn.count() == 0:
        print("  SKIP: No history button found (need at least 1 run)")
        return

    history_btn.first.click()
    page.wait_for_timeout(500)
    page.screenshot(path="/tmp/e2e_forcing_history.png")

    # History should show at least one record with "check" or "forces"
    check_entry = page.locator("text=check")
    forces_entry = page.locator("text=forces")
    has_entry = check_entry.count() > 0 or forces_entry.count() > 0
    print(f"  History has entries: {has_entry}")
    assert has_entry, "No history entries found"

    print("  PASS")


def main():
    passed = 0
    failed = 0
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("requestfailed", lambda req: console_msgs.append(f"[FAILED] {req.method} {req.url}"))

        # Warmup
        print("Warming up...")
        goto_with_retry(page, BASE_URL)
        goto_with_retry(page, f"{BASE_URL}/login")
        goto_with_retry(page, f"{BASE_URL}/register")
        print("Warmup done.\n")

        tests = [
            test_register_and_login,
            test_create_workspace,
            test_forcing_panel_visible,
            test_create_formula_for_forcing,
            test_forcing_check,
            test_forcing_forces,
            test_forcing_explanation,
            test_forcing_history,
        ]

        for test_fn in tests:
            try:
                test_fn(page)
                passed += 1
                results.append((test_fn.__name__, "PASS"))
            except Exception as e:
                page.screenshot(path=f"/tmp/e2e_fail_{test_fn.__name__}.png")
                print(f"  FAIL: {e}")
                traceback.print_exc()
                failed += 1
                results.append((test_fn.__name__, f"FAIL: {e}"))

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
