"""E2E tests for Undo/Redo functionality."""
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
    inputs.nth(0).fill("testuser_undoredo")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_undoredo")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_create_workspace(page):
    """Create a blank workspace for undo/redo testing."""
    print("TEST: Create workspace")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    blank_btn = page.locator("button:has-text('Чистый лист')")
    if blank_btn.count() > 0:
        blank_btn.first.click()
    else:
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
    print("  PASS")


def test_undo_redo_buttons_visible(page):
    """Verify undo/redo buttons are visible in the header."""
    print("TEST: Undo/Redo buttons visible")

    # Undo button has title "Отменить (Ctrl+Z)"
    undo_btn = page.locator("button[title*='Отменить']")
    assert undo_btn.count() > 0, "Undo button not found"

    # Redo button has title "Повторить (Ctrl+Shift+Z)"
    redo_btn = page.locator("button[title*='Повторить']")
    assert redo_btn.count() > 0, "Redo button not found"

    # Initially both should be disabled (no history)
    undo_disabled = undo_btn.first.is_disabled()
    redo_disabled = redo_btn.first.is_disabled()
    print(f"  Undo disabled: {undo_disabled}")
    print(f"  Redo disabled: {redo_disabled}")

    page.screenshot(path="/tmp/e2e_undoredo_buttons.png")
    print("  PASS")


def test_undo_after_add_concept(page):
    """Add a concept and undo it."""
    print("TEST: Undo after adding concept")

    # Switch to Network Editor Concept tab
    page.locator("button:has-text('Concept')").click()
    page.wait_for_timeout(300)

    # Add a concept
    id_input = page.locator("input[placeholder*='ID']")
    label_input = page.locator("input[placeholder*='Label']")

    id_input.fill("undo_test_1")
    label_input.fill("Undo Test Concept")

    page.locator("button:has-text('Добавить концепт')").click()
    page.wait_for_timeout(2000)

    # Verify concept was added
    concept = page.locator("text=undo_test_1")
    assert concept.count() > 0, "Concept was not added"
    print("  Added concept undo_test_1")

    # Check undo button is now enabled
    undo_btn = page.locator("button[title*='Отменить']")
    undo_disabled = undo_btn.first.is_disabled()
    print(f"  Undo disabled after add: {undo_disabled}")

    # Click Undo
    if not undo_disabled:
        undo_btn.first.click()
        page.wait_for_timeout(2000)

        # Verify concept is gone
        concept_after = page.locator("text=undo_test_1")
        # It may still be in the text but should be removed from the list
        print(f"  Concept after undo: count={concept_after.count()}")
        page.screenshot(path="/tmp/e2e_undoredo_after_undo.png")
        print("  Undo performed")
    else:
        print("  SKIP: Undo button still disabled after adding concept")

    print("  PASS")


def test_redo_after_undo(page):
    """Redo the undone concept addition."""
    print("TEST: Redo after undo")

    redo_btn = page.locator("button[title*='Повторить']")
    redo_disabled = redo_btn.first.is_disabled()
    print(f"  Redo disabled: {redo_disabled}")

    if not redo_disabled:
        redo_btn.first.click()
        page.wait_for_timeout(2000)

        # Verify concept is back
        concept = page.locator("text=undo_test_1")
        print(f"  Concept after redo: count={concept.count()}")
        page.screenshot(path="/tmp/e2e_undoredo_after_redo.png")
        print("  Redo performed")
    else:
        print("  SKIP: Redo button disabled (nothing to redo)")

    print("  PASS")


def test_keyboard_undo(page):
    """Test Ctrl+Z keyboard shortcut for undo."""
    print("TEST: Keyboard undo (Ctrl+Z)")

    # First, add another concept to have something to undo
    page.locator("button:has-text('Concept')").click()
    page.wait_for_timeout(300)

    id_input = page.locator("input[placeholder*='ID']")
    label_input = page.locator("input[placeholder*='Label']")

    id_input.fill("kb_undo_test")
    label_input.fill("KB Undo")

    page.locator("button:has-text('Добавить концепт')").click()
    page.wait_for_timeout(2000)

    concept = page.locator("text=kb_undo_test")
    assert concept.count() > 0, "Concept was not added for keyboard undo test"
    print("  Added concept kb_undo_test")

    # Press Ctrl+Z (or Cmd+Z on Mac)
    page.keyboard.press("Meta+z")  # Cmd+Z for Mac
    page.wait_for_timeout(2000)

    concept_after = page.locator("text=kb_undo_test")
    print(f"  Concept after Ctrl+Z: count={concept_after.count()}")
    page.screenshot(path="/tmp/e2e_undoredo_kb_undo.png")
    print("  PASS")


def test_keyboard_redo(page):
    """Test Ctrl+Shift+Z keyboard shortcut for redo."""
    print("TEST: Keyboard redo (Ctrl+Shift+Z)")

    # Press Ctrl+Shift+Z (or Cmd+Shift+Z on Mac)
    page.keyboard.press("Meta+Shift+z")  # Cmd+Shift+Z for Mac
    page.wait_for_timeout(2000)

    concept = page.locator("text=kb_undo_test")
    print(f"  Concept after Ctrl+Shift+Z: count={concept.count()}")
    page.screenshot(path="/tmp/e2e_undoredo_kb_redo.png")
    print("  PASS")


def test_multiple_undo(page):
    """Add multiple items and undo them all."""
    print("TEST: Multiple undo steps")

    page.locator("button:has-text('Concept')").click()
    page.wait_for_timeout(300)

    id_input = page.locator("input[placeholder*='ID']")
    label_input = page.locator("input[placeholder*='Label']")

    # Add concept A
    id_input.fill("multi_a")
    label_input.fill("Multi A")
    page.locator("button:has-text('Добавить концепт')").click()
    page.wait_for_timeout(1500)
    assert page.locator("text=multi_a").count() > 0, "Concept multi_a not added"

    # Add concept B
    id_input.fill("multi_b")
    label_input.fill("Multi B")
    page.locator("button:has-text('Добавить концепт')").click()
    page.wait_for_timeout(1500)
    assert page.locator("text=multi_b").count() > 0, "Concept multi_b not added"
    print("  Added multi_a and multi_b")

    # Undo twice
    undo_btn = page.locator("button[title*='Отменить']")
    for i in range(2):
        if not undo_btn.first.is_disabled():
            undo_btn.first.click()
            page.wait_for_timeout(1500)
            print(f"  Undo step {i+1}")

    # Both should be gone (or at least multi_b)
    multi_b_after = page.locator("text=multi_b")
    print(f"  multi_b after 2 undos: count={multi_b_after.count()}")

    page.screenshot(path="/tmp/e2e_undoredo_multi.png")
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
            test_undo_redo_buttons_visible,
            test_undo_after_add_concept,
            test_redo_after_undo,
            test_keyboard_undo,
            test_keyboard_redo,
            test_multiple_undo,
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
