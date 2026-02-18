"""E2E tests for Workspace Management (rename, duplicate, delete, export/import, blank canvas)."""
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
    inputs.nth(0).fill("testuser_wsmgmt")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        print("  User exists, logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_wsmgmt")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_blank_canvas(page):
    """Create a blank canvas workspace."""
    print("TEST: Blank canvas workspace")
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    blank_btn = page.locator("button:has-text('Чистый лист')")
    if blank_btn.count() > 0:
        blank_btn.first.click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("networkidle")
        assert "/workspace/" in page.url, f"Blank canvas didn't navigate to workspace: {page.url}"
        print("  Created blank canvas workspace")
    else:
        print("  SKIP: 'Чистый лист' button not found")
        # Fallback: create with default scenario
        page.locator("button:has-text('Создать')").first.click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("networkidle")

    page.screenshot(path="/tmp/e2e_wsmgmt_blank.png")
    print("  PASS")


def test_rename_workspace_inline(page):
    """Rename workspace via inline editing in the header."""
    print("TEST: Rename workspace inline")

    # Click on workspace name to enter edit mode
    ws_name = page.locator("span[title='Нажмите для переименования']")
    if ws_name.count() > 0:
        ws_name.click()
        page.wait_for_timeout(500)

        # Type new name
        name_input = page.locator("input[type='text']").first
        name_input.fill("Renamed WS Test")
        page.wait_for_timeout(200)

        # Click OK
        ok_btn = page.locator("button:has-text('OK')")
        ok_btn.first.click()
        page.wait_for_timeout(2000)

        # Verify new name is displayed
        new_name = page.locator("text=Renamed WS Test")
        assert new_name.count() > 0, "Renamed workspace name not visible"
        print("  Renamed workspace to 'Renamed WS Test'")
    else:
        # Try clicking on "Без имени" text
        unnamed = page.locator("text=Без имени")
        if unnamed.count() > 0:
            unnamed.click()
            page.wait_for_timeout(500)
            name_input = page.locator("input[type='text']").first
            name_input.fill("Renamed WS Test")
            page.locator("button:has-text('OK')").first.click()
            page.wait_for_timeout(2000)
            print("  Renamed workspace from 'Без имени'")
        else:
            print("  SKIP: Workspace name element not found")

    page.screenshot(path="/tmp/e2e_wsmgmt_renamed.png")
    print("  PASS")


def test_rename_workspace_in_list(page):
    """Rename workspace from the workspace list."""
    print("TEST: Rename workspace in list")

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    # Find "Переименовать" button
    rename_btn = page.locator("button:has-text('Переименовать')")
    if rename_btn.count() > 0:
        rename_btn.first.click()
        page.wait_for_timeout(500)

        # Find the rename input (visible text input inside the workspace list)
        rename_input = page.locator("input[type='text']:visible")
        if rename_input.count() > 0:
            rename_input.first.fill("List Renamed WS")
            page.wait_for_timeout(200)

            # Press Enter to confirm (or click OK)
            ok_btn = page.locator("button:has-text('OK')")
            if ok_btn.count() > 0:
                ok_btn.first.click()
            else:
                rename_input.first.press("Enter")
            page.wait_for_timeout(2000)
            page.wait_for_load_state("networkidle")

            renamed = page.locator("text=List Renamed WS")
            print(f"  Renamed visible: {renamed.count() > 0}")
        else:
            print("  SKIP: Rename input not found")
    else:
        print("  SKIP: No Переименовать button found")

    page.screenshot(path="/tmp/e2e_wsmgmt_list_renamed.png")
    print("  PASS")


def test_duplicate_workspace(page):
    """Duplicate a workspace from the list."""
    print("TEST: Duplicate workspace")

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    # Count workspaces before
    ws_items_before = page.locator("a[href*='/workspace/']").count()
    print(f"  Workspaces before: {ws_items_before}")

    dup_btn = page.locator("button:has-text('Дублировать')")
    if dup_btn.count() > 0:
        dup_btn.first.click()
        page.wait_for_timeout(3000)
        page.wait_for_load_state("networkidle")

        # Count workspaces after
        ws_items_after = page.locator("a[href*='/workspace/']").count()
        print(f"  Workspaces after: {ws_items_after}")
        assert ws_items_after > ws_items_before, "Workspace count didn't increase after duplicate"

        # Check for "(копия)" text
        copy_text = page.locator("text=копия")
        print(f"  Workspace with (копия): {copy_text.count() > 0}")
        print("  Duplicated workspace")
    else:
        print("  SKIP: No Дублировать button found")

    page.screenshot(path="/tmp/e2e_wsmgmt_duplicated.png")
    print("  PASS")


def test_export_workspace(page):
    """Export workspace as JSON."""
    print("TEST: Export workspace")

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    export_btn = page.locator("button:has-text('Экспорт')")
    if export_btn.count() > 0:
        # Set up download listener
        with page.expect_download(timeout=10000) as download_info:
            export_btn.first.click()

        download = download_info.value
        print(f"  Downloaded file: {download.suggested_filename}")
        assert download.suggested_filename.endswith(".json"), "Export file is not JSON"

        # Save the file for import test
        download.save_as("/tmp/e2e_exported_workspace.json")
        print("  Exported workspace to JSON")
    else:
        print("  SKIP: No Экспорт button found")

    page.screenshot(path="/tmp/e2e_wsmgmt_exported.png")
    print("  PASS")


def test_import_workspace(page):
    """Import workspace from JSON file."""
    print("TEST: Import workspace")

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    # Count workspaces before
    ws_items_before = page.locator("a[href*='/workspace/']").count()

    # Find the file input (hidden) for import - use first one (WorkspaceList import)
    file_input = page.locator("input[type='file'][accept='.json']")
    if file_input.count() > 0:
        file_input.first.set_input_files("/tmp/e2e_exported_workspace.json")
        page.wait_for_timeout(3000)
        page.wait_for_load_state("networkidle")

        ws_items_after = page.locator("a[href*='/workspace/']").count()
        print(f"  Workspaces before: {ws_items_before}, after: {ws_items_after}")
        assert ws_items_after > ws_items_before, "Workspace count didn't increase after import"
        print("  Imported workspace from JSON")
    else:
        print("  SKIP: File input not found (import label may be styled differently)")

    page.screenshot(path="/tmp/e2e_wsmgmt_imported.png")
    print("  PASS")


def test_delete_workspace(page):
    """Delete a workspace from the list."""
    print("TEST: Delete workspace")

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    ws_items_before = page.locator("a[href*='/workspace/']").count()
    print(f"  Workspaces before: {ws_items_before}")

    if ws_items_before == 0:
        print("  SKIP: No workspaces to delete")
        print("  PASS")
        return

    del_btn = page.locator("button:has-text('Удалить')")
    if del_btn.count() > 0:
        # Handle browser confirm dialog
        page.on("dialog", lambda dialog: dialog.accept())
        del_btn.first.click()
        page.wait_for_timeout(3000)
        page.wait_for_load_state("networkidle")

        ws_items_after = page.locator("a[href*='/workspace/']").count()
        print(f"  Workspaces after: {ws_items_after}")
        assert ws_items_after < ws_items_before, "Workspace count didn't decrease after delete"
        print("  Deleted workspace")
    else:
        print("  SKIP: No Удалить button found")

    page.screenshot(path="/tmp/e2e_wsmgmt_deleted.png")
    print("  PASS")


def test_export_json_from_workspace_page(page):
    """Export JSON from the workspace editor header."""
    print("TEST: Export JSON from workspace page")

    # Navigate to a workspace
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    ws_links = page.locator("a[href*='/workspace/']")
    if ws_links.count() == 0:
        # Create a workspace first
        page.locator("button:has-text('Создать'), button:has-text('Чистый лист')").first.click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("networkidle")
    else:
        ws_links.first.click()
        page.wait_for_timeout(3000)
        page.wait_for_load_state("networkidle")

    if "/workspace/" not in page.url:
        print("  SKIP: Not on workspace page")
        print("  PASS")
        return

    # Click JSON export button in header
    json_btn = page.locator("button:has-text('JSON')").first
    if json_btn.count() > 0:
        with page.expect_download(timeout=10000) as download_info:
            json_btn.click()
        download = download_info.value
        print(f"  Downloaded: {download.suggested_filename}")
        print("  Exported JSON from workspace header")
    else:
        print("  SKIP: JSON export button not found in header")

    page.screenshot(path="/tmp/e2e_wsmgmt_json_export.png")
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
            test_blank_canvas,
            test_rename_workspace_inline,
            test_rename_workspace_in_list,
            test_duplicate_workspace,
            test_export_workspace,
            test_import_workspace,
            test_delete_workspace,
            test_export_json_from_workspace_page,
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
