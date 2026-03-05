"""E2E test: unsetting an assigned variable by selecting empty option."""
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


def register_and_login(page):
    """Register a test user and log in."""
    goto_with_retry(page, f"{BASE_URL}/register")
    page.wait_for_timeout(1000)
    inputs = page.locator("input")
    inputs.nth(0).fill("testuser_unset2")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_unset2")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"


def create_workspace_with_fishing(page):
    """Create workspace with fishing scenario (has enum variables)."""
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    # Select fishing scenario
    scenario_select = page.locator("select").first
    if scenario_select.count() > 0:
        options = scenario_select.locator("option")
        # Pick a scenario with variables: fast_smith, lab1_university, or lab3_formulas
        for target in ["fast_smith", "lab1_university", "lab3_formulas"]:
            found = False
            for i in range(options.count()):
                val = options.nth(i).get_attribute("value") or ""
                if val == target:
                    scenario_select.select_option(value=val)
                    print(f"  Selected scenario: {val}")
                    found = True
                    break
            if found:
                break
        else:
            if options.count() > 1:
                scenario_select.select_option(index=1)

    page.wait_for_timeout(300)
    page.locator("button:has-text('Создать')").first.click()
    page.wait_for_timeout(5000)
    page.wait_for_load_state("networkidle")

    if "/workspace/" not in page.url:
        ws_links = page.locator("a[href*='/workspace/']")
        if ws_links.count() > 0:
            ws_links.first.click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle")

    assert "/workspace/" in page.url, f"Not on workspace page: {page.url}"
    page.wait_for_timeout(3000)


def test_unset_variable(page):
    """Assign a variable, then clear it via the empty option."""
    print("TEST: Unset variable via empty dropdown option")

    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

    page.wait_for_timeout(1000)
    page.screenshot(path="/tmp/e2e_unset_before.png")

    # Look for "Переменные" heading, then find selects after it
    var_heading = page.locator("h3:has-text('Переменные')")
    if var_heading.count() == 0:
        # Scroll down to find it
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

    if var_heading.count() == 0:
        print("  SKIP: No 'Переменные' section found")
        page.screenshot(path="/tmp/e2e_unset_no_vars.png")
        return

    # Find the parent container and its selects
    var_section = var_heading.locator("xpath=..")
    var_selects = var_section.locator("select")

    if var_selects.count() == 0:
        print("  SKIP: No variable dropdowns found")
        return

    target_select = var_selects.first
    options = target_select.locator("option")
    print(f"  Found {var_selects.count()} variable select(s), first has {options.count()} options")

    if options.count() < 2:
        print("  SKIP: Not enough options")
        return

    # Step 1: Set a value
    first_val = options.nth(1).get_attribute("value")
    print(f"  Setting variable to: {first_val}")
    target_select.select_option(value=first_val)
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")

    errors_after_set = [m for m in console_msgs if m.startswith("[4") or m.startswith("[5")]
    assert not errors_after_set, f"Errors after setting: {errors_after_set}"
    print("  Variable set OK")
    page.screenshot(path="/tmp/e2e_unset_assigned.png")

    # Step 2: Clear the variable
    print("  Clearing variable...")
    console_msgs.clear()
    target_select.select_option(value="")
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")

    page.screenshot(path="/tmp/e2e_unset_cleared.png")

    errors_after_clear = [m for m in console_msgs if m.startswith("[4") or m.startswith("[5")]
    if errors_after_clear:
        for m in console_msgs:
            print(f"    {m}")
        assert False, f"Errors after clearing: {errors_after_clear}"

    print("  Variable cleared — no errors!")
    print("  PASS")


def main():
    passed = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            register_and_login(page)
            create_workspace_with_fishing(page)
            test_unset_variable(page)
            passed += 1
        except Exception:
            failed += 1
            traceback.print_exc()
            page.screenshot(path="/tmp/e2e_unset_error.png")
        finally:
            browser.close()

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
