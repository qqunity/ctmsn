"""E2E test: Edit existing user variable (add values to domain)."""
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"

def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            page.wait_for_timeout(delay)

def main():
    passed = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

        # Warmup
        goto_with_retry(page, BASE_URL)
        goto_with_retry(page, f"{BASE_URL}/login")

        # Register first
        print("Registering...")
        goto_with_retry(page, f"{BASE_URL}/register")
        page.wait_for_timeout(1000)
        inputs = page.locator("input:visible")
        inputs.nth(0).fill("testuser_editvar")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Login — registration may have already logged us in
        print(f"After register, URL: {page.url}")
        if "/login" in page.url:
            print("Logging in...")
            page.wait_for_timeout(1000)
            page.locator("input").nth(0).fill("testuser_editvar")
            page.locator("input").nth(1).fill("testpass123")
            page.locator("button[type='submit'], button:has-text('Войти')").first.click()
            page.wait_for_timeout(2000)
            page.wait_for_load_state("networkidle")
        elif "/workspaces" not in page.url and "/workspace" not in page.url:
            goto_with_retry(page, f"{BASE_URL}/login")
            page.wait_for_timeout(1000)
            page.locator("input").nth(0).fill("testuser_editvar")
            page.locator("input").nth(1).fill("testpass123")
            page.locator("button[type='submit'], button:has-text('Войти')").first.click()
            page.wait_for_timeout(2000)
            page.wait_for_load_state("networkidle")
        print(f"After login, URL: {page.url}")
        assert "/workspaces" in page.url or "/workspace" in page.url, f"Login failed: {page.url}"

        # Create workspace with fast_smith scenario
        print("Creating workspace...")
        goto_with_retry(page, f"{BASE_URL}/workspaces")
        page.wait_for_timeout(1000)
        scenario_select = page.locator("select").first
        scenario_select.select_option("fast_smith")
        page.wait_for_timeout(300)
        page.locator("button:has-text('Создать')").first.click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("networkidle")
        assert "/workspace/" in page.url, f"Not on workspace: {page.url}"
        page.wait_for_timeout(2000)

        # TEST 1: Create a user variable, then edit it to add values
        print("\nTEST 1: Create enum variable and edit to add values")
        try:
            # Create variable
            new_var = page.locator("button:has-text('Новая переменная')")
            assert new_var.count() > 0, "New variable button not found"
            new_var.click()
            page.wait_for_timeout(500)

            page.locator("input[placeholder='Имя переменной']").fill("TestEditVar")
            val_input = page.locator("input[placeholder='Добавить значение']")
            val_input.fill("val1")
            page.locator("button:has-text('+')").first.click()
            page.wait_for_timeout(200)
            val_input.fill("val2")
            page.locator("button:has-text('+')").first.click()
            page.wait_for_timeout(200)

            page.locator("button:has-text('Создать')").last.click()
            page.wait_for_timeout(1500)

            # Verify variable created
            assert page.locator("text=TestEditVar").count() > 0, "Variable not created"
            print("  Created TestEditVar with val1, val2")

            # Verify dropdown has 2 values + placeholder
            var_select = page.locator("label:has-text('TestEditVar')").locator("..").locator("select")
            options = var_select.locator("option")
            option_count = options.count()
            print(f"  Dropdown has {option_count} options (expected 3: — + val1 + val2)")
            assert option_count == 3, f"Expected 3 options, got {option_count}"

            page.screenshot(path="/tmp/e2e_before_edit.png")

            # Click edit button (✎)
            edit_btn = page.locator("button[title='Редактировать']")
            assert edit_btn.count() > 0, "Edit button not found"
            edit_btn.first.click()
            page.wait_for_timeout(500)

            page.screenshot(path="/tmp/e2e_edit_form.png")

            # Verify edit form appeared with existing values
            edit_form = page.locator("text=Редактирование: TestEditVar")
            assert edit_form.count() > 0, "Edit form not shown"
            print("  Edit form opened")

            # Verify existing values shown as tags
            tag_val1 = page.locator(".bg-yellow-50 span:has-text('val1')")
            tag_val2 = page.locator(".bg-yellow-50 span:has-text('val2')")
            assert tag_val1.count() > 0, "Existing value val1 not shown"
            assert tag_val2.count() > 0, "Existing value val2 not shown"
            print("  Existing values (val1, val2) displayed in edit form")

            # Add a new value
            edit_input = page.locator(".bg-yellow-50 input[placeholder='Добавить значение']")
            edit_input.fill("val3")
            page.locator(".bg-yellow-50 button:has-text('+')").click()
            page.wait_for_timeout(200)

            # Verify val3 tag appeared
            tag_val3 = page.locator(".bg-yellow-50 span:has-text('val3')")
            assert tag_val3.count() > 0, "New value val3 not shown in form"
            print("  Added val3 to form")

            page.screenshot(path="/tmp/e2e_edit_added_val3.png")

            # Save
            page.locator("button:has-text('Сохранить')").click()
            page.wait_for_timeout(1500)

            # Verify edit form closed
            assert page.locator("text=Редактирование: TestEditVar").count() == 0, "Edit form still visible"
            print("  Edit form closed after save")

            # Verify dropdown now has 3 values + placeholder = 4 options
            var_select = page.locator("label:has-text('TestEditVar')").locator("..").locator("select")
            options = var_select.locator("option")
            option_count = options.count()
            print(f"  Dropdown now has {option_count} options (expected 4: — + val1 + val2 + val3)")
            assert option_count == 4, f"Expected 4 options after edit, got {option_count}"

            page.screenshot(path="/tmp/e2e_after_edit.png")
            print("  PASS")
            passed += 1
        except Exception as e:
            page.screenshot(path="/tmp/e2e_fail_edit.png")
            print(f"  FAIL: {e}")
            failed += 1

        # TEST 2: Edit and cancel
        print("\nTEST 2: Edit and cancel preserves original values")
        try:
            edit_btn = page.locator("button[title='Редактировать']")
            assert edit_btn.count() > 0, "Edit button not found"
            edit_btn.first.click()
            page.wait_for_timeout(500)

            # Add a value but cancel
            edit_input = page.locator(".bg-yellow-50 input[placeholder='Добавить значение']")
            edit_input.fill("val_cancelled")
            page.locator(".bg-yellow-50 button:has-text('+')").click()
            page.wait_for_timeout(200)

            # Cancel
            page.locator("button:has-text('Отмена')").click()
            page.wait_for_timeout(500)

            # Verify dropdown still has 4 options (not 5)
            var_select = page.locator("label:has-text('TestEditVar')").locator("..").locator("select")
            options = var_select.locator("option")
            option_count = options.count()
            print(f"  Dropdown still has {option_count} options (expected 4)")
            assert option_count == 4, f"Cancel didn't work: expected 4, got {option_count}"

            print("  PASS")
            passed += 1
        except Exception as e:
            page.screenshot(path="/tmp/e2e_fail_cancel.png")
            print(f"  FAIL: {e}")
            failed += 1

        # Clean up: delete the variable
        try:
            delete_btn = page.locator("label:has-text('TestEditVar')").locator("..").locator("button[title='Удалить']")
            if delete_btn.count() > 0:
                delete_btn.click()
                page.wait_for_timeout(500)
                print("\nCleaned up TestEditVar")
        except:
            pass

        errors = [m for m in console_msgs if "[error]" in m.lower() or "[FAILED]" in m]
        if errors:
            print(f"\nBrowser errors ({len(errors)}):")
            for e in errors[:5]:
                print(f"  {e}")

        browser.close()

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
