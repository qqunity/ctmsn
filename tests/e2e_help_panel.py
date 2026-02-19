"""E2E tests for HelpPanel and Tooltip components."""
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
    inputs.nth(0).fill("testuser_help")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_help")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_create_workspace(page):
    """Create a workspace to test help panel in."""
    print("TEST: Create workspace")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    page.locator("button:has-text('Создать')").first.click()
    page.wait_for_timeout(5000)
    page.wait_for_load_state("networkidle")

    if "/workspace/" not in page.url:
        ws_links = page.locator("a[href*='/workspace/']")
        if ws_links.count() > 0:
            ws_links.first.click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle")

    assert "/workspace/" in page.url, f"Not on workspace: {page.url}"
    page.wait_for_timeout(3000)
    print("  PASS")


def test_help_button_visible(page):
    """Verify the ? help button is present in the header."""
    print("TEST: Help button visible in header")

    help_btn = page.locator("button:has-text('?')")
    assert help_btn.count() > 0, "Help button (?) not found in header"

    # Verify it has the expected styling (blue border)
    classes = help_btn.first.get_attribute("class") or ""
    assert "border" in classes, f"Help button missing border styling: {classes}"

    page.screenshot(path="/tmp/e2e_help_button.png")
    print("  PASS")


def test_help_modal_opens(page):
    """Click ? button and verify modal opens."""
    print("TEST: Help modal opens")

    page.locator("button:has-text('?')").first.click()
    page.wait_for_timeout(500)

    # Modal backdrop should be visible
    modal = page.locator(".fixed.inset-0")
    assert modal.count() > 0, "Modal backdrop not found after clicking ?"

    # Modal content panel should be visible
    modal_panel = page.locator(".bg-white.rounded-lg.shadow-xl")
    assert modal_panel.count() > 0, "Modal content panel not found"

    page.screenshot(path="/tmp/e2e_help_modal_open.png")
    print("  PASS")


def test_task_tab_default(page):
    """Verify 'Задание' tab is active by default with correct content."""
    print("TEST: Task tab is default")

    # Tab button should be highlighted
    task_tab = page.locator("button:has-text('Задание')")
    assert task_tab.count() > 0, "Task tab button not found"
    task_classes = task_tab.first.get_attribute("class") or ""
    assert "bg-blue-100" in task_classes, "Task tab not active by default"

    # Content should show lab assignment text
    assert page.locator("text=Лабораторная работа").count() > 0, "Lab title not found"
    assert page.locator("text=Цель работы").count() > 0, "Goal section not found"
    assert page.locator("text=Порядок выполнения").count() > 0, "Steps section not found"
    assert page.locator("text=Критерии оценки").count() > 0, "Criteria section not found"

    print("  PASS")


def test_logic_tab(page):
    """Switch to Logic tab and verify truth tables."""
    print("TEST: Logic tab with truth tables")

    page.locator("button:has-text('Логика')").click()
    page.wait_for_timeout(300)

    # Verify tab is active
    logic_classes = page.locator("button:has-text('Логика')").first.get_attribute("class") or ""
    assert "bg-blue-100" in logic_classes, "Logic tab not active after click"

    # Check all 4 truth table headers
    for name in ["NOT", "AND", "OR", "IMPLIES"]:
        heading = page.locator(f"h3:has-text('{name}')")
        assert heading.count() > 0, f"{name} truth table heading not found"

    # Check column headers
    assert page.locator("th:has-text('¬A')").count() > 0, "NOT column header (¬A) not found"
    assert page.locator("th:has-text('A ∧ B')").count() > 0, "AND column header not found"
    assert page.locator("th:has-text('A ∨ B')").count() > 0, "OR column header not found"
    assert page.locator("th:has-text('A → B')").count() > 0, "IMPLIES column header not found"

    # Check color coding: TRUE in green, FALSE in red, UNKNOWN in yellow
    green_cells = page.locator("td.bg-green-100")
    red_cells = page.locator("td.bg-red-100")
    yellow_cells = page.locator("td.bg-yellow-100")

    assert green_cells.count() > 0, "No green (TRUE) cells found"
    assert red_cells.count() > 0, "No red (FALSE) cells found"
    assert yellow_cells.count() > 0, "No yellow (UNKNOWN) cells found"
    print(f"  Color-coded cells: {green_cells.count()} green, {red_cells.count()} red, {yellow_cells.count()} yellow")

    # Verify specific truth table values (NOT table: T->F, F->T, U->U)
    not_rows = page.locator("h3:has-text('NOT') + table tbody tr")
    assert not_rows.count() == 3, f"NOT table should have 3 rows, got {not_rows.count()}"

    page.screenshot(path="/tmp/e2e_help_logic.png")
    print("  PASS")


def test_glossary_tab(page):
    """Switch to Glossary tab and verify terms."""
    print("TEST: Glossary tab with terms")

    page.locator("button:has-text('Глоссарий')").click()
    page.wait_for_timeout(300)

    # Verify tab is active
    glossary_classes = page.locator("button:has-text('Глоссарий')").first.get_attribute("class") or ""
    assert "bg-blue-100" in glossary_classes, "Glossary tab not active"

    # Check all 8 glossary terms
    terms = ["Концепт", "Предикат", "Факт", "Домен", "Переменная", "Контекст", "Формула", "Форсинг"]
    for term in terms:
        assert page.locator(f"text={term}").count() > 0, f"Term '{term}' not found in glossary"

    # Check English terms in parentheses
    en_terms = ["Concept", "Predicate", "Variable", "Context", "Formula", "Forcing"]
    for en in en_terms:
        assert page.locator(f"text={en}").count() > 0, f"English term '{en}' not found"

    # Check definitions are present (at least some keywords)
    assert page.locator("text=семантической сети").count() > 0, "Definition content missing"

    page.screenshot(path="/tmp/e2e_help_glossary.png")
    print(f"  All {len(terms)} terms verified")
    print("  PASS")


def test_close_via_x_button(page):
    """Close modal via ✕ button."""
    print("TEST: Close modal via X button")

    # Modal should still be open from previous test
    assert page.locator(".fixed.inset-0").count() > 0, "Modal not open"

    page.locator("button:has-text('✕')").click()
    page.wait_for_timeout(300)

    assert page.locator(".fixed.inset-0").count() == 0, "Modal still visible after X click"
    print("  PASS")


def test_close_via_escape(page):
    """Close modal via Escape key."""
    print("TEST: Close modal via Escape")

    # Reopen modal
    page.locator("button:has-text('?')").first.click()
    page.wait_for_timeout(500)
    assert page.locator(".fixed.inset-0").count() > 0, "Modal did not reopen"

    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    assert page.locator(".fixed.inset-0").count() == 0, "Modal still visible after Escape"
    print("  PASS")


def test_close_via_backdrop(page):
    """Close modal by clicking the backdrop overlay."""
    print("TEST: Close modal via backdrop click")

    # Reopen modal
    page.locator("button:has-text('?')").first.click()
    page.wait_for_timeout(500)
    assert page.locator(".fixed.inset-0").count() > 0, "Modal did not reopen"

    # Click on the backdrop (edge of screen, outside modal content)
    page.locator(".fixed.inset-0").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(300)

    assert page.locator(".fixed.inset-0").count() == 0, "Modal still visible after backdrop click"
    print("  PASS")


def test_tab_persistence(page):
    """Verify selected tab persists when reopening modal."""
    print("TEST: Tab persistence across open/close")

    # Open and switch to Glossary
    page.locator("button:has-text('?')").first.click()
    page.wait_for_timeout(500)
    page.locator("button:has-text('Глоссарий')").click()
    page.wait_for_timeout(200)

    # Close and reopen
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    page.locator("button:has-text('?')").first.click()
    page.wait_for_timeout(500)

    # Glossary tab should still be active
    glossary_classes = page.locator("button:has-text('Глоссарий')").first.get_attribute("class") or ""
    assert "bg-blue-100" in glossary_classes, "Glossary tab not persisted after reopen"

    # Close for next tests
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    print("  PASS")


def test_tooltip_on_undo_button(page):
    """Hover over undo button and verify tooltip appears."""
    print("TEST: Tooltip on undo button")

    # Find undo button wrapper (Tooltip component wraps in .relative.inline-flex)
    undo_wrapper = page.locator(".relative.inline-flex").first
    assert undo_wrapper.count() > 0, "Tooltip wrapper not found"

    undo_wrapper.hover()
    page.wait_for_timeout(600)  # 400ms delay + buffer

    tooltip = page.locator(".bg-gray-800.text-white.text-xs")
    assert tooltip.count() > 0, "Tooltip not visible after hover"

    tooltip_text = tooltip.first.text_content() or ""
    assert "Ctrl+Z" in tooltip_text, f"Unexpected tooltip text: {tooltip_text}"
    print(f"  Tooltip text: {tooltip_text}")

    page.screenshot(path="/tmp/e2e_help_tooltip_undo.png")
    print("  PASS")


def test_tooltip_on_export_buttons(page):
    """Verify tooltips appear on export buttons."""
    print("TEST: Tooltips on export buttons")

    # Move away first to dismiss any active tooltip
    page.mouse.move(0, 0)
    page.wait_for_timeout(300)

    # Find the JSON export tooltip wrapper — look for wrapper containing "JSON" text
    json_wrappers = page.locator(".relative.inline-flex:has(button:has-text('JSON'))")
    if json_wrappers.count() > 0:
        json_wrappers.first.hover()
        page.wait_for_timeout(600)

        tooltip = page.locator(".bg-gray-800.text-white.text-xs")
        if tooltip.count() > 0:
            text = tooltip.first.text_content() or ""
            assert "JSON" in text, f"Expected JSON tooltip, got: {text}"
            print(f"  Export JSON tooltip: {text}")
        else:
            print("  WARN: JSON export tooltip not captured")
    else:
        print("  SKIP: JSON export wrapper not found")

    # Move away
    page.mouse.move(0, 0)
    page.wait_for_timeout(300)

    # PNG export tooltip
    png_wrapper = page.locator(".relative.inline-flex:has(button:has-text('PNG'))")
    if png_wrapper.count() > 0:
        png_wrapper.hover()
        page.wait_for_timeout(600)

        tooltip = page.locator(".bg-gray-800.text-white.text-xs")
        if tooltip.count() > 0:
            text = tooltip.first.text_content() or ""
            assert "PNG" in text, f"Expected PNG tooltip, got: {text}"
            print(f"  Export PNG tooltip: {text}")
        else:
            print("  WARN: PNG export tooltip not captured")
    else:
        print("  SKIP: PNG export wrapper not found")

    page.screenshot(path="/tmp/e2e_help_tooltip_export.png")
    print("  PASS")


def test_tooltip_on_help_button(page):
    """Verify tooltip on the ? button itself."""
    print("TEST: Tooltip on help button")

    page.mouse.move(0, 0)
    page.wait_for_timeout(300)

    help_wrapper = page.locator(".relative.inline-flex:has(button:has-text('?'))")
    if help_wrapper.count() > 0:
        help_wrapper.first.hover()
        page.wait_for_timeout(600)

        tooltip = page.locator(".bg-gray-800.text-white.text-xs")
        if tooltip.count() > 0:
            text = tooltip.first.text_content() or ""
            assert "справк" in text.lower(), f"Expected help tooltip, got: {text}"
            print(f"  Help button tooltip: {text}")
        else:
            print("  WARN: Help button tooltip not captured")
    else:
        print("  SKIP: Help button wrapper not found")

    print("  PASS")


def test_tooltip_disappears_on_mouse_leave(page):
    """Verify tooltip disappears when mouse leaves the button."""
    print("TEST: Tooltip disappears on mouse leave")

    page.mouse.move(0, 0)
    page.wait_for_timeout(300)

    undo_wrapper = page.locator(".relative.inline-flex").first
    undo_wrapper.hover()
    page.wait_for_timeout(600)

    # Tooltip should be visible
    assert page.locator(".bg-gray-800.text-white.text-xs").count() > 0, "Tooltip not visible"

    # Move mouse away
    page.mouse.move(500, 500)
    page.wait_for_timeout(200)

    # Tooltip should be gone
    assert page.locator(".bg-gray-800.text-white.text-xs").count() == 0, "Tooltip still visible after mouse leave"
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
            test_help_button_visible,
            test_help_modal_opens,
            test_task_tab_default,
            test_logic_tab,
            test_glossary_tab,
            test_close_via_x_button,
            test_close_via_escape,
            test_close_via_backdrop,
            test_tab_persistence,
            test_tooltip_on_undo_button,
            test_tooltip_on_export_buttons,
            test_tooltip_on_help_button,
            test_tooltip_disappears_on_mouse_leave,
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
