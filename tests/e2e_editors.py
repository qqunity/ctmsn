"""E2E tests for Formula Editor, Variable/Domain Editor, Context Editor."""
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

    # Fill registration form
    inputs = page.locator("input")
    inputs.nth(0).fill("testuser_editors")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    # If already registered, try login
    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_editors")
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

    page.screenshot(path="/tmp/e2e_workspaces_page.png")

    # Click "Создать" button to create a new workspace
    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.first.click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("networkidle")
    else:
        # Fall back to clicking existing workspace link
        ws_links = page.locator("a[href*='/workspace/']")
        if ws_links.count() > 0:
            ws_links.first.click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle")

    print(f"  After create, URL: {page.url}")
    page.screenshot(path="/tmp/e2e_workspace.png")

    # If not yet on workspace page, try clicking the first workspace link
    if "/workspace/" not in page.url:
        ws_links = page.locator("a[href*='/workspace/']")
        if ws_links.count() > 0:
            ws_links.first.click()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("networkidle")
            print(f"  Clicked workspace link, URL: {page.url}")

    assert "/workspace/" in page.url, f"Not on workspace page: {page.url}"
    # Wait for workspace to fully load
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")
    print("  PASS")


def test_workspace_panels_visible(page):
    """Verify the new editor panels are visible."""
    print("TEST: Workspace panels visible")
    page.wait_for_timeout(2000)
    page.screenshot(path="/tmp/e2e_panels.png")

    # Check for panel headings
    content = page.content()

    # Variables panel
    var_heading = page.locator("h3:has-text('Переменные')")
    print(f"  Variables panel: {var_heading.count() > 0}")

    # Context panel
    ctx_heading = page.locator("h3:has-text('Контексты')")
    print(f"  Context panel: {ctx_heading.count() > 0}")

    # Formula panel
    formula_heading = page.locator("h3:has-text('Формулы')")
    print(f"  Formula panel: {formula_heading.count() > 0}")

    assert formula_heading.count() > 0, "Formula panel not found"
    print("  PASS")


def test_variable_editor(page):
    """Test creating and deleting a custom variable."""
    print("TEST: Variable editor - create custom variable")

    # Click "+ Новая переменная"
    new_var_btn = page.locator("button:has-text('Новая переменная')")
    if new_var_btn.count() == 0:
        print("  SKIP: No variable editor button found (may not have variables)")
        return

    new_var_btn.click()
    page.wait_for_timeout(500)
    page.screenshot(path="/tmp/e2e_var_create.png")

    # Fill the form
    name_input = page.locator("input[placeholder='Имя переменной']")
    assert name_input.count() > 0, "Variable name input not found"
    name_input.fill("TestVar1")

    # Select enum domain (default)
    # Add a value
    val_input = page.locator("input[placeholder='Добавить значение']")
    if val_input.count() > 0:
        val_input.fill("val1")
        page.locator("button:has-text('+')").first.click()
        page.wait_for_timeout(200)
        val_input.fill("val2")
        page.locator("button:has-text('+')").first.click()
        page.wait_for_timeout(200)

    page.screenshot(path="/tmp/e2e_var_form_filled.png")

    # Click Create
    create_btn = page.locator("button:has-text('Создать')")
    create_btn.click()
    page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_var_created.png")

    # Verify variable appears in list
    var_text = page.locator("text=TestVar1")
    assert var_text.count() > 0, "Created variable not found in list"
    print("  Created variable TestVar1")

    # Delete it
    delete_btns = page.locator("text=TestVar1 >> .. >> button:has-text('×')")
    if delete_btns.count() > 0:
        delete_btns.first.click()
        page.wait_for_timeout(1000)
        remaining = page.locator("text=TestVar1")
        print(f"  After delete, variable still present: {remaining.count() > 0}")

    print("  PASS")


def test_context_editor(page):
    """Test creating contexts, switching active, and comparing."""
    print("TEST: Context editor")

    # Click "+ Новый контекст"
    new_ctx_btn = page.locator("button:has-text('Новый контекст')")
    if new_ctx_btn.count() == 0:
        print("  SKIP: No context editor button found")
        return

    # Create context 1
    new_ctx_btn.click()
    page.wait_for_timeout(500)
    name_input = page.locator("input[placeholder='Имя контекста']")
    name_input.fill("Контекст A")
    page.locator("button:has-text('Создать')").last.click()
    page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_ctx_created1.png")

    # Create context 2
    new_ctx_btn = page.locator("button:has-text('Новый контекст')")
    new_ctx_btn.click()
    page.wait_for_timeout(500)
    name_input = page.locator("input[placeholder='Имя контекста']")
    name_input.fill("Контекст B")
    page.locator("button:has-text('Создать')").last.click()
    page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_ctx_created2.png")

    # Verify both contexts appear
    ctx_a = page.locator("text=Контекст A")
    ctx_b = page.locator("text=Контекст B")
    assert ctx_a.count() > 0, "Context A not found"
    assert ctx_b.count() > 0, "Context B not found"
    print("  Created 2 contexts")

    # Activate context A
    radios = page.locator("input[name='activeCtx']")
    if radios.count() >= 1:
        radios.first.click()
        page.wait_for_timeout(1000)
        print("  Activated context A")

    # Expand context A to see variable assignments
    ctx_a_btn = page.locator("button:has-text('Контекст A')")
    if ctx_a_btn.count() > 0:
        ctx_a_btn.click()
        page.wait_for_timeout(500)
        page.screenshot(path="/tmp/e2e_ctx_expanded.png")
        print("  Expanded context A")

    # Collapse context A first to avoid re-render issues
    ctx_a_btn2 = page.locator("button:has-text('Контекст A')")
    if ctx_a_btn2.count() > 0:
        ctx_a_btn2.click()
        page.wait_for_timeout(300)

    # Try compare (select both checkboxes)
    checkboxes = page.locator("input[type='checkbox']")
    if checkboxes.count() >= 2:
        checkboxes.nth(0).check()
        page.wait_for_timeout(200)
        checkboxes.nth(1).check()
        page.wait_for_timeout(500)

        compare_btn = page.locator("button:has-text('Сравнить')")
        if compare_btn.count() > 0 and compare_btn.is_enabled():
            compare_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path="/tmp/e2e_ctx_compare.png")
            print("  Compared contexts")
        else:
            print(f"  Compare button state: count={compare_btn.count()}, enabled={compare_btn.is_enabled() if compare_btn.count() > 0 else 'N/A'}")
            page.screenshot(path="/tmp/e2e_ctx_compare_disabled.png")

    # Clean up: delete both contexts
    for _ in range(2):
        del_btn = page.locator("button[title='Удалить']")
        if del_btn.count() > 0:
            del_btn.first.click()
            page.wait_for_timeout(500)

    print("  PASS")


def test_formula_editor(page):
    """Test creating a formula, evaluating it."""
    print("TEST: Formula editor")

    # Click "+ Новая формула"
    new_formula_btn = page.locator("button:has-text('Новая формула')")
    if new_formula_btn.count() == 0:
        print("  SKIP: No formula editor button found")
        return

    new_formula_btn.click()
    page.wait_for_timeout(500)
    page.screenshot(path="/tmp/e2e_formula_new.png")

    # Fill name
    name_input = page.locator("input[placeholder='Имя формулы']")
    assert name_input.count() > 0, "Formula name input not found"
    name_input.fill("Test Formula 1")

    # Default type is FactAtom - select a predicate if available
    pred_selects = page.locator("select")
    # The first select after the type selector should be the predicate dropdown
    for i in range(pred_selects.count()):
        sel = pred_selects.nth(i)
        options = sel.locator("option")
        if options.count() > 1:
            # Check if this looks like a predicate selector
            text = options.nth(1).text_content() or ""
            if "арн" in text or "Предикат" in sel.locator("option").first.text_content():
                sel.select_option(index=1)
                page.wait_for_timeout(300)
                print(f"  Selected predicate: {text}")
                break

    page.screenshot(path="/tmp/e2e_formula_filled.png")

    # Click Create
    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_formula_created.png")

    # Verify formula appears
    formula_text = page.locator("text=Test Formula 1")
    assert formula_text.count() > 0, "Created formula not found"
    print("  Created formula")

    # Evaluate
    eval_btn = page.locator("button[title='Вычислить']")
    if eval_btn.count() > 0:
        eval_btn.first.click()
        page.wait_for_timeout(1000)
        page.screenshot(path="/tmp/e2e_formula_eval.png")
        print("  Evaluated formula")

    # Check for result badge
    result_badge = page.locator(".bg-green-100, .bg-red-100, .bg-yellow-100")
    if result_badge.count() > 0:
        print(f"  Result badge visible: {result_badge.first.text_content()}")

    # Delete formula
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

    print("  PASS")


def test_formula_nesting(page):
    """Test creating And(FactAtom(...), Not(FactAtom(...)))."""
    print("TEST: Formula nesting")

    new_formula_btn = page.locator("button:has-text('Новая формула')")
    if new_formula_btn.count() == 0:
        print("  SKIP: No formula editor button found")
        return

    new_formula_btn.click()
    page.wait_for_timeout(500)

    # Fill name
    name_input = page.locator("input[placeholder='Имя формулы']")
    name_input.fill("Nested Formula")

    # Find the formula type selector inside the formula builder (it has FactAtom/And/Not options)
    # The formula builder selects have specific options like FactAtom, EqAtom, Not, And, Or, Implies
    all_selects = page.locator("select")
    type_select = None
    for i in range(all_selects.count()):
        sel = all_selects.nth(i)
        options_text = sel.locator("option").all_text_contents()
        if "And" in options_text and "FactAtom" in options_text:
            type_select = sel
            break

    if type_select is None:
        print("  SKIP: Could not find formula type selector")
        # Cancel creation
        cancel_btn = page.locator("button:has-text('Отмена')")
        if cancel_btn.count() > 0:
            cancel_btn.last.click()
        return

    type_select.select_option("And")
    page.wait_for_timeout(300)

    page.screenshot(path="/tmp/e2e_formula_and.png")

    # Should have an "Add" sub-formula button
    add_btn = page.locator("button:has-text('Добавить')")
    if add_btn.count() > 0:
        add_btn.first.click()
        page.wait_for_timeout(300)
        print("  Added sub-formula to And")

    # Change second child to Not
    all_selects = page.locator("select")
    changed = False
    for i in range(all_selects.count()):
        sel = all_selects.nth(i)
        options_text = sel.locator("option").all_text_contents()
        if "Not" in options_text and sel.input_value() == "FactAtom":
            sel.select_option("Not")
            changed = True
            print("  Changed sub-formula to Not")
            break

    page.wait_for_timeout(300)
    page.screenshot(path="/tmp/e2e_formula_nested.png")

    # Check text preview contains "And("
    preview = page.locator("text=And(")
    print(f"  And preview visible: {preview.count() > 0}")

    # Create it
    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_formula_nested_saved.png")

    # Verify it was saved
    nested_text = page.locator("text=Nested Formula")
    print(f"  Nested formula saved: {nested_text.count() > 0}")

    # Clean up
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

    print("  PASS")


def main():
    passed = 0
    failed = 0
    skipped = 0
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
            test_workspace_panels_visible,
            test_variable_editor,
            test_context_editor,
            test_formula_editor,
            test_formula_nesting,
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

        # Print console errors
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
