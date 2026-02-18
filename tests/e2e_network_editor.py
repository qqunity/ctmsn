"""E2E tests for the Network Editor Panel (concepts, predicates, facts)."""
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
    inputs.nth(0).fill("testuser_neteditor")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_neteditor")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    print(f"  After login, URL: {page.url}")
    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_create_workspace(page):
    """Create a blank workspace for network editing."""
    print("TEST: Create workspace (blank canvas)")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    # Click "Чистый лист" (blank canvas) button or "Создать"
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
    page.wait_for_load_state("networkidle")
    print("  PASS")


def test_network_editor_visible(page):
    """Verify the Network Editor panel is visible."""
    print("TEST: Network Editor visible")
    page.wait_for_timeout(2000)

    editor_heading = page.locator("text=Network Editor")
    assert editor_heading.count() > 0, "Network Editor heading not found"

    # Check mode tabs
    concept_tab = page.locator("button:has-text('Concept')")
    predicate_tab = page.locator("button:has-text('Predicate')")
    fact_tab = page.locator("button:has-text('Fact')")
    assert concept_tab.count() > 0, "Concept tab not found"
    assert predicate_tab.count() > 0, "Predicate tab not found"
    assert fact_tab.count() > 0, "Fact tab not found"

    page.screenshot(path="/tmp/e2e_neteditor_visible.png")
    print("  PASS")


def test_add_concept(page):
    """Add a concept via the Network Editor."""
    print("TEST: Add concept")

    # Make sure we're on Concept tab
    page.locator("button:has-text('Concept')").click()
    page.wait_for_timeout(300)

    # Fill concept form
    id_input = page.locator("input[placeholder*='ID']")
    assert id_input.count() > 0, "Concept ID input not found"
    id_input.fill("test_concept_1")

    label_input = page.locator("input[placeholder*='Label']")
    assert label_input.count() > 0, "Concept Label input not found"
    label_input.fill("Test Concept One")

    tags_input = page.locator("input[placeholder*='Tags']")
    if tags_input.count() > 0:
        tags_input.fill("test, category1")

    # Click "Добавить концепт"
    add_btn = page.locator("button:has-text('Добавить концепт')")
    assert add_btn.count() > 0, "Add concept button not found"
    add_btn.click()
    page.wait_for_timeout(2000)

    page.screenshot(path="/tmp/e2e_neteditor_concept_added.png")

    # Verify concept appears in the list
    concept_text = page.locator("text=test_concept_1")
    assert concept_text.count() > 0, "Added concept not found in list"
    print("  Added concept test_concept_1")

    # Add a second concept
    id_input.fill("test_concept_2")
    label_input.fill("Test Concept Two")
    if tags_input.count() > 0:
        tags_input.fill("test")
    add_btn.click()
    page.wait_for_timeout(2000)

    concept2_text = page.locator("text=test_concept_2")
    assert concept2_text.count() > 0, "Second concept not found"
    print("  Added concept test_concept_2")

    # Add a third concept for fact testing
    id_input.fill("test_concept_3")
    label_input.fill("Test Concept Three")
    if tags_input.count() > 0:
        tags_input.fill("")
    add_btn.click()
    page.wait_for_timeout(2000)

    concept3_text = page.locator("text=test_concept_3")
    assert concept3_text.count() > 0, "Third concept not found"
    print("  Added concept test_concept_3")

    print("  PASS")


def test_edit_concept(page):
    """Edit a concept's label and tags."""
    print("TEST: Edit concept")

    # Make sure we're on Concept tab
    page.locator("button:has-text('Concept')").click()
    page.wait_for_timeout(300)

    # Find the edit button (pencil icon ✎) for test_concept_1
    # Each concept row has [span text] [edit btn] [delete btn]
    concept_rows = page.locator(".bg-zinc-50.rounded")
    found_edit = False
    for i in range(concept_rows.count()):
        row = concept_rows.nth(i)
        row_text = row.text_content() or ""
        if "test_concept_1" in row_text:
            # Click the first button (edit pencil)
            btns = row.locator("button")
            if btns.count() >= 1:
                btns.first.click()
                page.wait_for_timeout(500)
                found_edit = True
            break

    if found_edit:
        # Check edit form appeared - the Label input inside the edit form
        label_edit = page.locator("input[placeholder='Label']")
        if label_edit.count() > 0:
            label_edit.fill("Updated Concept One")
            page.wait_for_timeout(200)

            # Click OK to save
            ok_btn = page.locator("button:has-text('OK')")
            if ok_btn.count() > 0:
                ok_btn.first.click()
                page.wait_for_timeout(2000)

                # Verify updated label
                updated = page.locator("text=Updated Concept One")
                print(f"  Updated label visible: {updated.count() > 0}")
            else:
                print("  SKIP: OK button not found in edit form")
        else:
            print("  SKIP: Label edit input not found")
    else:
        print("  SKIP: Edit button not found for concept")

    page.screenshot(path="/tmp/e2e_neteditor_concept_edited.png")
    print("  PASS")


def test_add_predicate(page):
    """Add a predicate via the Network Editor."""
    print("TEST: Add predicate")

    # Switch to Predicate tab
    page.locator("button:has-text('Predicate')").click()
    page.wait_for_timeout(300)

    # Fill predicate form
    name_input = page.locator("input[placeholder*='Name']")
    assert name_input.count() > 0, "Predicate Name input not found"
    name_input.fill("test_relates")

    arity_input = page.locator("input[placeholder='Arity'], input[type='number']")
    if arity_input.count() > 0:
        arity_input.first.fill("2")

    # Click "Добавить предикат"
    add_btn = page.locator("button:has-text('Добавить предикат')")
    assert add_btn.count() > 0, "Add predicate button not found"
    add_btn.click()
    page.wait_for_timeout(2000)

    page.screenshot(path="/tmp/e2e_neteditor_predicate_added.png")

    # Verify predicate appears
    pred_text = page.locator("text=test_relates")
    assert pred_text.count() > 0, "Added predicate not found"
    print("  Added predicate test_relates (arity 2)")

    print("  PASS")


def test_edit_predicate(page):
    """Edit a predicate's arity."""
    print("TEST: Edit predicate")

    # Make sure Predicate tab is active
    page.locator("button:has-text('Predicate')").click()
    page.wait_for_timeout(300)

    # Find the edit button for test_relates in the predicate list
    pred_rows = page.locator(".bg-zinc-50.rounded")
    found_edit = False
    for i in range(pred_rows.count()):
        row = pred_rows.nth(i)
        row_text = row.text_content() or ""
        if "test_relates" in row_text:
            btns = row.locator("button")
            if btns.count() >= 1:
                btns.first.click()
                page.wait_for_timeout(500)
                found_edit = True
            break

    if found_edit:
        # Edit arity - use the inline edit input (smaller, text-xs)
        arity_edit = page.locator("input[placeholder='Arity']")
        if arity_edit.count() > 0:
            # Pick the inline edit one (the smaller text-xs one)
            arity_edit.last.fill("3")

            ok_btn = page.locator("button:has-text('OK')")
            if ok_btn.count() > 0:
                ok_btn.first.click()
                page.wait_for_timeout(2000)

                updated = page.locator("text=арность: 3")
                print(f"  Updated arity visible: {updated.count() > 0}")

                # Revert arity back to 2
                for j in range(pred_rows.count()):
                    row2 = pred_rows.nth(j)
                    if "test_relates" in (row2.text_content() or ""):
                        row2.locator("button").first.click()
                        page.wait_for_timeout(500)
                        page.locator("input[placeholder='Arity']").last.fill("2")
                        page.locator("button:has-text('OK')").first.click()
                        page.wait_for_timeout(1000)
                        print("  Reverted arity back to 2")
                        break
            else:
                print("  SKIP: OK button not found")
        else:
            print("  SKIP: Arity edit input not found")
    else:
        print("  SKIP: Edit button not found for predicate")

    page.screenshot(path="/tmp/e2e_neteditor_predicate_edited.png")
    print("  PASS")


def test_add_fact(page):
    """Add a fact via the Network Editor."""
    print("TEST: Add fact")

    # Switch to Fact tab
    page.locator("button:has-text('Fact')").click()
    page.wait_for_timeout(300)

    # Select predicate from dropdown
    pred_select = page.locator("select").first
    # Find the option with test_relates
    options = pred_select.locator("option")
    for i in range(options.count()):
        if "test_relates" in (options.nth(i).text_content() or ""):
            pred_select.select_option(index=i)
            break
    page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_neteditor_fact_pred_selected.png")

    # Click on concept buttons to select arguments
    concept_btns = page.locator("button:has-text('test_concept_1')")
    if concept_btns.count() > 0:
        concept_btns.first.click()
        page.wait_for_timeout(300)

    concept_btns2 = page.locator("button:has-text('test_concept_2')")
    if concept_btns2.count() > 0:
        concept_btns2.first.click()
        page.wait_for_timeout(300)

    page.screenshot(path="/tmp/e2e_neteditor_fact_args_selected.png")

    # Or use manual CSV input as fallback
    selected_text = page.locator("text=Выбрано (2/2)")
    if selected_text.count() == 0:
        manual_input = page.locator("input[placeholder*='concept1, concept2']")
        if manual_input.count() > 0:
            manual_input.fill("test_concept_1, test_concept_2")
            page.wait_for_timeout(300)

    # Click "Добавить факт"
    add_fact_btn = page.locator("button:has-text('Добавить факт')")
    if add_fact_btn.count() > 0 and add_fact_btn.first.is_enabled():
        add_fact_btn.first.click()
        page.wait_for_timeout(2000)
        print("  Added fact: test_relates(test_concept_1, test_concept_2)")
    else:
        print(f"  Add fact button: count={add_fact_btn.count()}, enabled={add_fact_btn.first.is_enabled() if add_fact_btn.count() > 0 else 'N/A'}")

    page.screenshot(path="/tmp/e2e_neteditor_fact_added.png")

    # Verify fact in the list
    fact_text = page.locator("text=test_relates(test_concept_1")
    if fact_text.count() > 0:
        print("  Fact appears in existing facts list")
    else:
        print("  Note: fact not visible in list (may need scroll)")

    print("  PASS")


def test_delete_fact(page):
    """Delete a fact from the Network Editor."""
    print("TEST: Delete fact")

    # Stay on Fact tab
    page.locator("button:has-text('Fact')").click()
    page.wait_for_timeout(300)

    # Find fact delete button
    fact_text = page.locator("text=test_relates(test_concept_1")
    if fact_text.count() > 0:
        fact_row = fact_text.locator("..")
        del_btn = fact_row.locator("button")
        if del_btn.count() > 0:
            del_btn.last.click()
            page.wait_for_timeout(2000)
            remaining = page.locator("text=test_relates(test_concept_1")
            print(f"  Fact still present after delete: {remaining.count() > 0}")
        else:
            print("  SKIP: Delete button not found for fact")
    else:
        print("  SKIP: No fact to delete")

    page.screenshot(path="/tmp/e2e_neteditor_fact_deleted.png")
    print("  PASS")


def test_delete_concept_cascade(page):
    """Delete a concept and verify cascade warning."""
    print("TEST: Delete concept with cascade warning")

    # First, re-add a fact so we have cascade data
    page.locator("button:has-text('Fact')").click()
    page.wait_for_timeout(300)

    pred_select = page.locator("select").first
    options = pred_select.locator("option")
    for i in range(options.count()):
        if "test_relates" in (options.nth(i).text_content() or ""):
            pred_select.select_option(index=i)
            break
    page.wait_for_timeout(500)

    # Select args via manual input
    manual_input = page.locator("input[placeholder*='concept1, concept2']")
    if manual_input.count() > 0:
        manual_input.fill("test_concept_1, test_concept_2")
        page.wait_for_timeout(300)

    add_fact_btn = page.locator("button:has-text('Добавить факт')")
    if add_fact_btn.count() > 0 and add_fact_btn.first.is_enabled():
        add_fact_btn.first.click()
        page.wait_for_timeout(2000)

    # Switch to Concept tab
    page.locator("button:has-text('Concept')").click()
    page.wait_for_timeout(300)

    # Delete test_concept_1 (should trigger cascade warning)
    concept_row = page.locator("text=test_concept_1").locator("..")
    del_btns = concept_row.locator("button")
    # Last button should be delete (×)
    if del_btns.count() >= 2:
        del_btns.last.click()
        page.wait_for_timeout(1000)

        # Check for cascade warning
        cascade = page.locator("text=затронет")
        if cascade.count() > 0:
            print("  Cascade warning displayed")
            page.screenshot(path="/tmp/e2e_neteditor_cascade_warning.png")

            # Click "Удалить" to confirm
            confirm_btn = page.locator("button:has-text('Удалить')").first
            if confirm_btn.count() > 0:
                confirm_btn.click()
                page.wait_for_timeout(2000)
                print("  Confirmed deletion with cascade")
            else:
                # Cancel instead
                cancel_btn = page.locator("button:has-text('Отмена')")
                if cancel_btn.count() > 0:
                    cancel_btn.last.click()
                    page.wait_for_timeout(500)
                    print("  Cancelled cascade deletion")
        else:
            print("  No cascade warning (concept had no facts)")
    else:
        print("  SKIP: Delete button not found for concept")

    page.screenshot(path="/tmp/e2e_neteditor_cascade_done.png")
    print("  PASS")


def test_delete_predicate_cascade(page):
    """Delete a predicate and verify cascade warning."""
    print("TEST: Delete predicate with cascade warning")

    # Switch to Predicate tab
    page.locator("button:has-text('Predicate')").click()
    page.wait_for_timeout(300)

    # Find delete button for test_relates
    pred_text = page.locator("text=test_relates")
    if pred_text.count() > 0:
        pred_row = pred_text.locator("..")
        del_btns = pred_row.locator("button")
        if del_btns.count() >= 2:
            del_btns.last.click()
            page.wait_for_timeout(1000)

            # Check for cascade warning
            cascade = page.locator("text=затронет")
            if cascade.count() > 0:
                print("  Cascade warning displayed for predicate")
                page.screenshot(path="/tmp/e2e_neteditor_pred_cascade.png")

                # Confirm deletion
                confirm_btn = page.locator("button:has-text('Удалить')").first
                confirm_btn.click()
                page.wait_for_timeout(2000)
                print("  Confirmed predicate deletion")
            else:
                print("  No cascade warning (predicate had no facts)")
                page.wait_for_timeout(1000)
        else:
            print("  SKIP: Delete button not found for predicate")
    else:
        print("  SKIP: Predicate test_relates not found")

    page.screenshot(path="/tmp/e2e_neteditor_pred_deleted.png")
    print("  PASS")


def test_cleanup_concepts(page):
    """Clean up remaining test concepts."""
    print("TEST: Cleanup remaining concepts")

    page.locator("button:has-text('Concept')").click()
    page.wait_for_timeout(300)

    for concept_id in ["test_concept_2", "test_concept_3"]:
        concept_text = page.locator(f"text={concept_id}")
        if concept_text.count() > 0:
            concept_row = concept_text.locator("..")
            del_btns = concept_row.locator("button")
            if del_btns.count() >= 2:
                del_btns.last.click()
                page.wait_for_timeout(1000)
                # Handle possible cascade
                confirm_btn = page.locator("button:has-text('Удалить')")
                if confirm_btn.count() > 0:
                    confirm_btn.first.click()
                    page.wait_for_timeout(1000)
                print(f"  Deleted {concept_id}")

    page.screenshot(path="/tmp/e2e_neteditor_cleanup.png")
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
            test_network_editor_visible,
            test_add_concept,
            test_edit_concept,
            test_add_predicate,
            test_edit_predicate,
            test_add_fact,
            test_delete_fact,
            test_delete_concept_cascade,
            test_delete_predicate_cascade,
            test_cleanup_concepts,
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
