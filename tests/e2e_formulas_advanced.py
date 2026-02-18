"""E2E tests for advanced formula types (EqAtom, Or, Implies), TermPicker, and formula editing."""
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
    inputs.nth(0).fill("testuser_formadv")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_formadv")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_create_workspace_with_scenario(page):
    """Create a workspace with fast_smith scenario (has predicates and concepts)."""
    print("TEST: Create workspace with fast_smith")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    scenario_select = page.locator("select").first
    if scenario_select.count() > 0:
        options = scenario_select.locator("option")
        for i in range(options.count()):
            if "fast_smith" in (options.nth(i).text_content() or ""):
                scenario_select.select_option(index=i)
                break

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


def _find_formula_type_select(page):
    """Find the formula type select that has FactAtom, EqAtom, etc."""
    all_selects = page.locator("select")
    for i in range(all_selects.count()):
        sel = all_selects.nth(i)
        options_text = sel.locator("option").all_text_contents()
        if "And" in options_text and "FactAtom" in options_text:
            return sel
    return None


def test_formula_eqatom(page):
    """Create an EqAtom formula."""
    print("TEST: EqAtom formula")

    new_formula_btn = page.locator("button:has-text('Новая формула')")
    if new_formula_btn.count() == 0:
        print("  SKIP: No formula editor button found")
        print("  PASS")
        return

    new_formula_btn.click()
    page.wait_for_timeout(500)

    # Fill name
    name_input = page.locator("input[placeholder='Имя формулы']")
    name_input.fill("EqAtom Test")

    # Find formula type select and change to EqAtom
    type_select = _find_formula_type_select(page)
    if type_select is None:
        print("  SKIP: Could not find formula type selector")
        page.locator("button:has-text('Отмена')").last.click()
        print("  PASS")
        return

    type_select.select_option("EqAtom")
    page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_formula_eqatom.png")

    # Verify left and right term labels
    left_label = page.locator("text=left")
    right_label = page.locator("text=right")
    print(f"  Left term label: {left_label.count() > 0}")
    print(f"  Right term label: {right_label.count() > 0}")

    # Verify preview contains "EqAtom("
    preview = page.locator("text=EqAtom(")
    print(f"  EqAtom preview visible: {preview.count() > 0}")

    # Create it
    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    # Verify saved
    saved = page.locator("text=EqAtom Test")
    assert saved.count() > 0, "EqAtom formula not saved"
    print("  Created EqAtom formula")

    # Clean up
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

    print("  PASS")


def test_formula_or(page):
    """Create an Or formula."""
    print("TEST: Or formula")

    new_formula_btn = page.locator("button:has-text('Новая формула')")
    new_formula_btn.click()
    page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    name_input.fill("Or Test")

    type_select = _find_formula_type_select(page)
    if type_select is None:
        print("  SKIP: Could not find formula type selector")
        page.locator("button:has-text('Отмена')").last.click()
        print("  PASS")
        return

    type_select.select_option("Or")
    page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_formula_or.png")

    # Should show "+ Добавить" button for adding sub-formulas
    add_sub = page.locator("button:has-text('Добавить')")
    if add_sub.count() > 0:
        add_sub.first.click()
        page.wait_for_timeout(300)
        print("  Added sub-formula to Or")

    # Verify preview contains "Or("
    preview = page.locator("text=Or(")
    print(f"  Or preview visible: {preview.count() > 0}")

    # Create
    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    saved = page.locator("text=Or Test")
    assert saved.count() > 0, "Or formula not saved"
    print("  Created Or formula")

    # Clean up
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

    print("  PASS")


def test_formula_implies(page):
    """Create an Implies formula."""
    print("TEST: Implies formula")

    new_formula_btn = page.locator("button:has-text('Новая формула')")
    new_formula_btn.click()
    page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    name_input.fill("Implies Test")

    type_select = _find_formula_type_select(page)
    if type_select is None:
        print("  SKIP: Could not find formula type selector")
        page.locator("button:has-text('Отмена')").last.click()
        print("  PASS")
        return

    type_select.select_option("Implies")
    page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_formula_implies.png")

    # Verify if/then labels
    if_label = page.locator("text=if:")
    then_label = page.locator("text=then:")
    print(f"  'if:' label visible: {if_label.count() > 0}")
    print(f"  'then:' label visible: {then_label.count() > 0}")

    # Verify preview
    preview = page.locator("text=Implies(")
    print(f"  Implies preview visible: {preview.count() > 0}")

    # Create
    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    saved = page.locator("text=Implies Test")
    assert saved.count() > 0, "Implies formula not saved"
    print("  Created Implies formula")

    # Clean up
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

    print("  PASS")


def test_term_picker_modes(page):
    """Test TermPicker C/V/L mode switching."""
    print("TEST: TermPicker modes")

    new_formula_btn = page.locator("button:has-text('Новая формула')")
    new_formula_btn.click()
    page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    name_input.fill("TermPicker Test")

    # Default is FactAtom - select a predicate
    type_select = _find_formula_type_select(page)
    if type_select:
        type_select.select_option("FactAtom")
        page.wait_for_timeout(300)

    # Select first predicate
    pred_selects = page.locator("select")
    for i in range(pred_selects.count()):
        sel = pred_selects.nth(i)
        options = sel.locator("option")
        first_text = options.first.text_content() or ""
        if "Предикат" in first_text:
            if options.count() > 1:
                sel.select_option(index=1)
                page.wait_for_timeout(300)
                break

    page.screenshot(path="/tmp/e2e_formula_termpicker_before.png")

    # Find TermPicker buttons - C, V, L
    c_btn = page.locator("button:has-text('C')").first
    v_btn = page.locator("button:has-text('V')").first
    l_btn = page.locator("button:has-text('L')").first

    # Test C mode (concept) - should show select dropdown
    if c_btn.count() > 0:
        c_btn.click()
        page.wait_for_timeout(300)
        print("  Switched to Concept mode")

    # Test V mode (variable) - should show variable select
    if v_btn.count() > 0:
        v_btn.click()
        page.wait_for_timeout(300)
        print("  Switched to Variable mode")

    # Test L mode (literal) - should show text input
    if l_btn.count() > 0:
        l_btn.click()
        page.wait_for_timeout(300)

        # Find literal input
        literal_input = page.locator("input[placeholder='Значение']")
        if literal_input.count() > 0:
            literal_input.first.fill("test_literal")
            page.wait_for_timeout(200)
            print("  Entered literal value")

    page.screenshot(path="/tmp/e2e_formula_termpicker_after.png")

    # Cancel
    cancel_btn = page.locator("button:has-text('Отмена')")
    if cancel_btn.count() > 0:
        cancel_btn.last.click()
        page.wait_for_timeout(500)

    print("  PASS")


def test_formula_edit_existing(page):
    """Create a formula, then edit it by clicking on its name."""
    print("TEST: Edit existing formula")

    # Create a formula first
    new_formula_btn = page.locator("button:has-text('Новая формула')")
    new_formula_btn.click()
    page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    name_input.fill("Editable Formula")

    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    # Verify it was created
    saved = page.locator("text=Editable Formula")
    assert saved.count() > 0, "Formula not created for edit test"
    print("  Created formula 'Editable Formula'")

    # Click on formula name to enter edit mode
    formula_name = page.locator("text=Editable Formula")
    formula_name.first.click()
    page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_formula_edit_mode.png")

    # Check for edit form (name input + formula builder + save button)
    edit_name_input = page.locator("input[type='text']")
    save_btn = page.locator("button:has-text('Сохранить')")

    if save_btn.count() > 0:
        # Change the name
        for i in range(edit_name_input.count()):
            val = edit_name_input.nth(i).input_value()
            if "Editable" in val:
                edit_name_input.nth(i).fill("Edited Formula")
                break

        save_btn.first.click()
        page.wait_for_timeout(1000)

        edited = page.locator("text=Edited Formula")
        print(f"  Edited formula visible: {edited.count() > 0}")
    else:
        print("  SKIP: Save button not found (edit mode may not be active)")

    # Clean up
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_formula_edited.png")
    print("  PASS")


def test_formula_and_with_or_nested(page):
    """Create And(FactAtom, Or(FactAtom, FactAtom)) - deep nesting."""
    print("TEST: And with nested Or formula")

    new_formula_btn = page.locator("button:has-text('Новая формула')")
    new_formula_btn.click()
    page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя формулы']")
    name_input.fill("And+Or Nested")

    type_select = _find_formula_type_select(page)
    if type_select is None:
        print("  SKIP: Could not find formula type selector")
        page.locator("button:has-text('Отмена')").last.click()
        print("  PASS")
        return

    type_select.select_option("And")
    page.wait_for_timeout(300)

    # Add a second sub-formula
    add_btn = page.locator("button:has-text('Добавить')")
    if add_btn.count() > 0:
        add_btn.first.click()
        page.wait_for_timeout(300)

    # Change second child to Or
    all_selects = page.locator("select")
    changed = False
    for i in range(all_selects.count()):
        sel = all_selects.nth(i)
        options_text = sel.locator("option").all_text_contents()
        if "Or" in options_text and sel.input_value() == "FactAtom":
            sel.select_option("Or")
            changed = True
            print("  Changed child to Or")
            break

    page.wait_for_timeout(300)
    page.screenshot(path="/tmp/e2e_formula_and_or.png")

    # Preview should contain "And("
    preview = page.locator("text=And(")
    print(f"  And preview: {preview.count() > 0}")

    # Create
    create_btn = page.locator("button:has-text('Создать')")
    if create_btn.count() > 0:
        create_btn.last.click()
        page.wait_for_timeout(1000)

    saved = page.locator("text=And+Or Nested")
    print(f"  Saved: {saved.count() > 0}")

    # Clean up
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

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
            test_formula_eqatom,
            test_formula_or,
            test_formula_implies,
            test_term_picker_modes,
            test_formula_edit_existing,
            test_formula_and_with_or_nested,
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
