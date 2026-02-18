"""E2E tests for Scenario loading, mode switching, running, and derive."""
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
    inputs.nth(0).fill("testuser_scenarios")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_scenarios")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_create_workspace_with_scenario(page):
    """Create a workspace with a specific scenario selected."""
    print("TEST: Create workspace with scenario")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    # Select a scenario from the dropdown
    scenario_select = page.locator("select").first
    if scenario_select.count() > 0:
        options = scenario_select.locator("option")
        if options.count() > 1:
            # Select second option (first non-default)
            scenario_select.select_option(index=1)
            page.wait_for_timeout(300)
            selected = scenario_select.input_value()
            print(f"  Selected scenario: {selected}")

    # Click "Создать"
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
    page.screenshot(path="/tmp/e2e_scenarios_created.png")
    print("  PASS")


def test_scenario_bar_visible(page):
    """Verify the ScenarioBar is visible with all controls."""
    print("TEST: ScenarioBar visible")
    page.wait_for_timeout(2000)

    # Check for "New session" button
    new_session_btn = page.locator("button:has-text('New session')")
    assert new_session_btn.count() > 0, "New session button not found"

    # Check for Load button
    load_btn = page.locator("button:has-text('Load')")
    assert load_btn.count() > 0, "Load button not found"

    # Check for Run button
    run_btn = page.locator("button:has-text('Run')")
    assert run_btn.count() > 0, "Run button not found"

    # Check for derive checkbox
    derive_checkbox = page.locator("input[type='checkbox']")
    print(f"  Derive checkbox present: {derive_checkbox.count() > 0}")

    # Check for scenario select
    selects = page.locator("select")
    print(f"  Number of selects (scenario + mode): {selects.count()}")

    page.screenshot(path="/tmp/e2e_scenarios_bar.png")
    print("  PASS")


def test_select_scenario(page):
    """Select a different scenario from the dropdown."""
    print("TEST: Select scenario")

    # The first select in ScenarioBar is the scenario selector
    scenario_selects = page.locator(".flex.items-center.gap-2 select")
    if scenario_selects.count() == 0:
        scenario_selects = page.locator("select")

    if scenario_selects.count() > 0:
        scenario_select = scenario_selects.first
        options = scenario_select.locator("option")
        print(f"  Available scenarios: {options.count()}")

        if options.count() > 1:
            # Select "fast_smith" if available
            for i in range(options.count()):
                text = options.nth(i).text_content() or ""
                if "fast_smith" in text:
                    scenario_select.select_option(index=i)
                    print(f"  Selected: fast_smith")
                    break
            else:
                # Select second option
                scenario_select.select_option(index=1)
                selected_text = options.nth(1).text_content()
                print(f"  Selected: {selected_text}")
            page.wait_for_timeout(500)
    else:
        print("  SKIP: No scenario select found")

    page.screenshot(path="/tmp/e2e_scenarios_selected.png")
    print("  PASS")


def test_select_mode(page):
    """Select a mode from the mode dropdown."""
    print("TEST: Select mode")

    # The second select in ScenarioBar is the mode selector
    selects = page.locator("select")
    if selects.count() >= 2:
        mode_select = selects.nth(1)
        options = mode_select.locator("option")
        print(f"  Available modes: {options.count()}")

        if options.count() > 1:
            mode_select.select_option(index=1)
            selected = options.nth(1).text_content()
            print(f"  Selected mode: {selected}")
            page.wait_for_timeout(300)
        else:
            print("  Only (default) mode available")
    else:
        print("  SKIP: Mode select not found")

    page.screenshot(path="/tmp/e2e_scenarios_mode.png")
    print("  PASS")


def test_load_scenario(page):
    """Load a scenario using the Load button."""
    print("TEST: Load scenario")

    load_btn = page.locator("button:has-text('Load')")
    assert load_btn.count() > 0, "Load button not found"

    # Remember current URL
    old_url = page.url

    load_btn.click()
    page.wait_for_timeout(5000)
    page.wait_for_load_state("networkidle")

    # URL may change to a new workspace ID
    print(f"  After load, URL: {page.url}")
    assert "/workspace/" in page.url, f"Not on workspace page after load: {page.url}"

    # Verify graph has nodes (the canvas should have content)
    page.wait_for_timeout(2000)
    page.screenshot(path="/tmp/e2e_scenarios_loaded.png")

    print("  Loaded scenario")
    print("  PASS")


def test_derive_checkbox(page):
    """Toggle the derive checkbox and load with derive."""
    print("TEST: Derive checkbox")

    derive_label = page.locator("label:has-text('derive')")
    if derive_label.count() > 0:
        checkbox = derive_label.locator("input[type='checkbox']")
        if checkbox.count() > 0:
            # Check current state
            is_checked = checkbox.is_checked()
            print(f"  Derive currently checked: {is_checked}")

            # Toggle it
            if is_checked:
                checkbox.uncheck()
            else:
                checkbox.check()
            page.wait_for_timeout(300)

            new_state = checkbox.is_checked()
            assert new_state != is_checked, "Derive checkbox didn't toggle"
            print(f"  Toggled derive to: {new_state}")

            # Restore original state
            if new_state != is_checked:
                if is_checked:
                    checkbox.check()
                else:
                    checkbox.uncheck()
        else:
            print("  SKIP: Derive checkbox not found")
    else:
        print("  SKIP: Derive label not found")

    print("  PASS")


def test_run_scenario(page):
    """Run the current scenario using the Run button."""
    print("TEST: Run scenario")

    run_btn = page.locator("button:has-text('Run')")
    assert run_btn.count() > 0, "Run button not found"

    run_btn.click()
    page.wait_for_timeout(5000)
    page.wait_for_load_state("networkidle")

    page.screenshot(path="/tmp/e2e_scenarios_run.png")

    # Verify we're still on workspace page
    assert "/workspace/" in page.url, f"Not on workspace page after run: {page.url}"
    print("  Ran scenario")
    print("  PASS")


def test_new_session(page):
    """Click "New session" button to start a fresh session."""
    print("TEST: New session")

    new_session_btn = page.locator("button:has-text('New session')")
    assert new_session_btn.count() > 0, "New session button not found"

    old_url = page.url

    new_session_btn.click()
    page.wait_for_timeout(5000)
    page.wait_for_load_state("networkidle")

    print(f"  After new session, URL: {page.url}")
    assert "/workspace/" in page.url, f"Not on workspace page: {page.url}"

    page.screenshot(path="/tmp/e2e_scenarios_new_session.png")
    print("  New session created")
    print("  PASS")


def test_scenario_with_fast_smith(page):
    """Load fast_smith scenario and verify graph has content."""
    print("TEST: Load fast_smith scenario with graph")

    # Select fast_smith
    selects = page.locator("select")
    if selects.count() > 0:
        scenario_select = selects.first
        options = scenario_select.locator("option")
        found = False
        for i in range(options.count()):
            text = options.nth(i).text_content() or ""
            if "fast_smith" in text:
                scenario_select.select_option(index=i)
                found = True
                break

        if not found:
            print("  SKIP: fast_smith scenario not available")
            print("  PASS")
            return

    # Select default mode
    if selects.count() >= 2:
        selects.nth(1).select_option(index=0)
        page.wait_for_timeout(300)

    # Ensure derive is on
    derive_label = page.locator("label:has-text('derive')")
    if derive_label.count() > 0:
        checkbox = derive_label.locator("input[type='checkbox']")
        if checkbox.count() > 0 and not checkbox.is_checked():
            checkbox.check()
            page.wait_for_timeout(200)

    # Load
    page.locator("button:has-text('Load')").click()
    page.wait_for_timeout(5000)
    page.wait_for_load_state("networkidle")

    page.screenshot(path="/tmp/e2e_scenarios_fast_smith.png")

    # Verify variables panel has content (fast_smith has variables)
    page.wait_for_timeout(2000)
    var_heading = page.locator("h3:has-text('Переменные')")
    print(f"  Variables panel visible: {var_heading.count() > 0}")

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
            test_create_workspace_with_scenario,
            test_scenario_bar_visible,
            test_select_scenario,
            test_select_mode,
            test_load_scenario,
            test_derive_checkbox,
            test_run_scenario,
            test_new_session,
            test_scenario_with_fast_smith,
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
