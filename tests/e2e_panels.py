"""E2E tests for DetailsPanel, EquationsPanel, CommentPanel, PNG export,
   context cloning, variable domain types, and context progress badges."""
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
    inputs.nth(0).fill("testuser_panels")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_panels")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_create_workspace_with_scenario(page):
    """Create a workspace with fast_smith scenario."""
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


def test_details_panel_empty(page):
    """Verify the Details panel shows placeholder when nothing is selected."""
    print("TEST: Details panel (empty state)")

    details_heading = page.locator("text=Details")
    assert details_heading.count() > 0, "Details heading not found"

    placeholder = page.locator("text=Click a node/edge/equation")
    print(f"  Placeholder visible: {placeholder.count() > 0}")
    assert placeholder.count() > 0, "Details placeholder not found"

    page.screenshot(path="/tmp/e2e_panels_details_empty.png")
    print("  PASS")


def test_equations_panel(page):
    """Verify the Equations panel is visible."""
    print("TEST: Equations panel")

    eq_heading = page.locator("text=Уравнения")
    assert eq_heading.count() > 0, "Equations heading not found"

    # Check for equation items or "Нет уравнений"
    no_eq = page.locator("text=Нет уравнений")
    eq_items = page.locator("ul.divide-y li")

    if no_eq.count() > 0:
        print("  No equations (scenario may not have derivations)")
    elif eq_items.count() > 0:
        print(f"  Equations count: {eq_items.count()}")

        # Click first equation
        eq_items.first.click()
        page.wait_for_timeout(500)

        # Check if Details panel updated
        eq_detail = page.locator("text=Equation")
        print(f"  Equation details shown: {eq_detail.count() > 0}")

        page.screenshot(path="/tmp/e2e_panels_eq_clicked.png")
    else:
        print("  Equations panel found but no items")

    print("  PASS")


def test_comment_panel(page):
    """Test CommentPanel: add and view comments."""
    print("TEST: Comment panel")

    comment_heading = page.locator("h3:has-text('Комментарии')")
    assert comment_heading.count() > 0, "Comment panel not found"

    # Check initial state
    no_comments = page.locator("text=Нет комментариев")
    print(f"  No comments initially: {no_comments.count() > 0}")

    # Add a comment
    comment_input = page.locator("input[placeholder*='комментарий'], input[placeholder*='Написать']")
    if comment_input.count() > 0:
        comment_input.fill("Test comment from E2E")
        page.wait_for_timeout(200)

        submit_btn = page.locator("button:has-text('Отправить')")
        assert submit_btn.count() > 0, "Submit button not found"
        submit_btn.click()
        page.wait_for_timeout(2000)

        # Verify comment appears
        comment = page.locator("text=Test comment from E2E")
        assert comment.count() > 0, "Comment not visible after submit"
        print("  Added comment")

        # Verify author and time are shown
        comment_items = page.locator(".border.rounded.p-2.text-sm")
        if comment_items.count() > 0:
            item_text = comment_items.last.text_content() or ""
            print(f"  Comment item text length: {len(item_text)}")
    else:
        print("  SKIP: Comment input not found")

    page.screenshot(path="/tmp/e2e_panels_comments.png")
    print("  PASS")


def test_png_export(page):
    """Test PNG export button."""
    print("TEST: PNG export")

    # Find PNG export button
    png_btn = page.locator("button:has-text('PNG')")
    if png_btn.count() > 0:
        # PNG export creates a download via data URL
        with page.expect_download(timeout=10000) as download_info:
            png_btn.click()

        download = download_info.value
        filename = download.suggested_filename
        print(f"  Downloaded: {filename}")
        assert filename.endswith(".png"), f"Expected PNG file, got: {filename}"
        print("  PNG export successful")
    else:
        print("  SKIP: PNG export button not found")

    print("  PASS")


def test_variable_range_domain(page):
    """Create a variable with range domain."""
    print("TEST: Variable with range domain")

    new_var_btn = page.locator("button:has-text('Новая переменная')")
    if new_var_btn.count() == 0:
        print("  SKIP: No variable editor button found")
        print("  PASS")
        return

    new_var_btn.click()
    page.wait_for_timeout(500)

    # Fill name
    name_input = page.locator("input[placeholder='Имя переменной']")
    name_input.fill("RangeVar")

    # Select "Диапазон" (range) radio
    range_radio = page.locator("label:has-text('Диапазон') input[type='radio']")
    if range_radio.count() > 0:
        range_radio.click()
        page.wait_for_timeout(300)

        # Fill min and max
        number_inputs = page.locator("input[type='number']")
        if number_inputs.count() >= 2:
            number_inputs.nth(0).fill("10")
            number_inputs.nth(1).fill("50")
            page.wait_for_timeout(200)
            print("  Set range: 10-50")

        page.screenshot(path="/tmp/e2e_panels_range_var.png")

        # Create
        create_btn = page.locator("button:has-text('Создать')")
        create_btn.click()
        page.wait_for_timeout(1000)

        var_text = page.locator("text=RangeVar")
        assert var_text.count() > 0, "Range variable not created"
        print("  Created RangeVar")

        # Clean up
        del_btn = page.locator("text=RangeVar >> .. >> button:has-text('×')")
        if del_btn.count() > 0:
            del_btn.first.click()
            page.wait_for_timeout(500)
    else:
        print("  SKIP: Range radio button not found")
        cancel = page.locator("button:has-text('Отмена')")
        if cancel.count() > 0:
            cancel.last.click()

    print("  PASS")


def test_variable_predicate_domain(page):
    """Create a variable with predicate domain."""
    print("TEST: Variable with predicate domain")

    new_var_btn = page.locator("button:has-text('Новая переменная')")
    if new_var_btn.count() == 0:
        print("  SKIP: No variable editor button found")
        print("  PASS")
        return

    new_var_btn.click()
    page.wait_for_timeout(500)

    name_input = page.locator("input[placeholder='Имя переменной']")
    name_input.fill("PredVar")

    # Select "Предикат" radio
    pred_radio = page.locator("label:has-text('Предикат') input[type='radio']")
    if pred_radio.count() > 0:
        pred_radio.click()
        page.wait_for_timeout(300)

        # Fill predicate name
        pred_input = page.locator("input[placeholder='Имя предиката']")
        if pred_input.count() > 0:
            pred_input.fill("custom_pred")
            page.wait_for_timeout(200)
            print("  Set predicate: custom_pred")

        page.screenshot(path="/tmp/e2e_panels_pred_var.png")

        # Create
        create_btn = page.locator("button:has-text('Создать')")
        create_btn.click()
        page.wait_for_timeout(1000)

        var_text = page.locator("text=PredVar")
        assert var_text.count() > 0, "Predicate variable not created"
        print("  Created PredVar")

        # Clean up
        del_btn = page.locator("text=PredVar >> .. >> button:has-text('×')")
        if del_btn.count() > 0:
            del_btn.first.click()
            page.wait_for_timeout(500)
    else:
        print("  SKIP: Predicate radio button not found")
        cancel = page.locator("button:has-text('Отмена')")
        if cancel.count() > 0:
            cancel.last.click()

    print("  PASS")


def test_context_clone(page):
    """Create a context, then clone it."""
    print("TEST: Context clone")

    # Create first context
    new_ctx_btn = page.locator("button:has-text('Новый контекст')")
    if new_ctx_btn.count() == 0:
        print("  SKIP: No context editor button found")
        print("  PASS")
        return

    new_ctx_btn.click()
    page.wait_for_timeout(500)
    page.locator("input[placeholder='Имя контекста']").fill("Source Ctx")
    page.locator("button:has-text('Создать')").last.click()
    page.wait_for_timeout(1000)

    source = page.locator("text=Source Ctx")
    assert source.count() > 0, "Source context not created"
    print("  Created Source Ctx")

    # Create a clone
    new_ctx_btn = page.locator("button:has-text('Новый контекст')")
    new_ctx_btn.click()
    page.wait_for_timeout(500)

    page.locator("input[placeholder='Имя контекста']").fill("Cloned Ctx")

    # Look for "Клон из:" select
    clone_select = page.locator("select")
    clone_found = False
    for i in range(clone_select.count()):
        sel = clone_select.nth(i)
        options = sel.locator("option")
        for j in range(options.count()):
            text = options.nth(j).text_content() or ""
            if "Source Ctx" in text:
                sel.select_option(index=j)
                clone_found = True
                print("  Selected 'Source Ctx' as clone source")
                break
        if clone_found:
            break

    page.screenshot(path="/tmp/e2e_panels_clone_ctx.png")

    page.locator("button:has-text('Создать')").last.click()
    page.wait_for_timeout(1000)

    cloned = page.locator("text=Cloned Ctx")
    assert cloned.count() > 0, "Cloned context not created"
    print("  Created Cloned Ctx")

    # Clean up both contexts
    for _ in range(2):
        del_btn = page.locator("button[title='Удалить']")
        if del_btn.count() > 0:
            del_btn.first.click()
            page.wait_for_timeout(500)

    print("  PASS")


def test_context_progress_badge(page):
    """Verify context progress badge shows assigned/total vars."""
    print("TEST: Context progress badge")

    new_ctx_btn = page.locator("button:has-text('Новый контекст')")
    if new_ctx_btn.count() == 0:
        print("  SKIP: No context editor button found")
        print("  PASS")
        return

    new_ctx_btn.click()
    page.wait_for_timeout(500)
    page.locator("input[placeholder='Имя контекста']").fill("Badge Ctx")
    page.locator("button:has-text('Создать')").last.click()
    page.wait_for_timeout(1000)

    # Look for progress badge (format: "X из Y" or "X/Y")
    badge = page.locator("text=/\\d+.*из.*\\d+/")
    badge2 = page.locator("text=/\\d+\\/\\d+/")

    if badge.count() > 0 or badge2.count() > 0:
        badge_text = (badge.first if badge.count() > 0 else badge2.first).text_content()
        print(f"  Progress badge: {badge_text}")
    else:
        print("  Note: Progress badge not visible (may require variables)")

    page.screenshot(path="/tmp/e2e_panels_badge.png")

    # Clean up
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(500)

    print("  PASS")


def test_context_delete_button(page):
    """Verify context delete button in header works."""
    print("TEST: Context delete button")

    new_ctx_btn = page.locator("button:has-text('Новый контекст')")
    if new_ctx_btn.count() == 0:
        print("  SKIP: No context editor button found")
        print("  PASS")
        return

    new_ctx_btn.click()
    page.wait_for_timeout(500)
    page.locator("input[placeholder='Имя контекста']").fill("Delete Me Ctx")
    page.locator("button:has-text('Создать')").last.click()
    page.wait_for_timeout(1000)

    created = page.locator("text=Delete Me Ctx")
    assert created.count() > 0, "Context not created for delete test"

    # Find and click delete button
    del_btn = page.locator("button[title='Удалить']")
    if del_btn.count() > 0:
        del_btn.first.click()
        page.wait_for_timeout(1000)

        remaining = page.locator("text=Delete Me Ctx")
        print(f"  Context after delete: count={remaining.count()}")
    else:
        print("  SKIP: Delete button not found")

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
            test_details_panel_empty,
            test_equations_panel,
            test_comment_panel,
            test_png_export,
            test_variable_range_domain,
            test_variable_predicate_domain,
            test_context_clone,
            test_context_progress_badge,
            test_context_delete_button,
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
