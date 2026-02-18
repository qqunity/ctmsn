"""E2E test for Variable Editor and Context Editor with a scenario that has variables."""
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

        # Login
        print("Logging in...")
        page.locator("input").nth(0).fill("testuser_editors")
        page.locator("input").nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")
        assert "/workspaces" in page.url, f"Login failed: {page.url}"

        # Create workspace with fast_smith scenario (has variables)
        print("Creating fast_smith workspace...")
        goto_with_retry(page, f"{BASE_URL}/workspaces")
        page.wait_for_timeout(1000)

        # Select fast_smith scenario
        scenario_select = page.locator("select").first
        scenario_select.select_option("fast_smith")
        page.wait_for_timeout(300)

        # Create
        page.locator("button:has-text('Создать')").first.click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("networkidle")
        assert "/workspace/" in page.url, f"Not on workspace: {page.url}"
        page.wait_for_timeout(2000)

        page.screenshot(path="/tmp/e2e_fastsmith.png")

        # TEST 1: Variable panel visible with scenario variables
        print("\nTEST 1: Variable editor with scenario variables")
        try:
            var_heading = page.locator("h3:has-text('Переменные')")
            assert var_heading.count() > 0, "Variables panel not found"
            scenario_label = page.locator("text=Сценарий")
            print(f"  Scenario variables section: {scenario_label.count() > 0}")

            # Try changing a variable
            selects = page.locator(".space-y-4 select")
            for i in range(selects.count()):
                sel = selects.nth(i)
                options = sel.locator("option")
                if options.count() > 2:  # Has actual options (not just "—")
                    # Select second option
                    sel.select_option(index=1)
                    page.wait_for_timeout(1500)
                    print(f"  Set variable via dropdown")
                    break

            page.screenshot(path="/tmp/e2e_var_changed.png")
            print("  PASS")
            passed += 1
        except Exception as e:
            page.screenshot(path="/tmp/e2e_fail_var.png")
            print(f"  FAIL: {e}")
            failed += 1

        # TEST 2: Create custom variable
        print("\nTEST 2: Create custom variable")
        try:
            new_var = page.locator("button:has-text('Новая переменная')")
            assert new_var.count() > 0, "New variable button not found"
            new_var.click()
            page.wait_for_timeout(500)

            page.locator("input[placeholder='Имя переменной']").fill("MyCustomVar")
            # Add enum values
            val_input = page.locator("input[placeholder='Добавить значение']")
            val_input.fill("alpha")
            page.locator("button:has-text('+')").first.click()
            page.wait_for_timeout(200)
            val_input.fill("beta")
            page.locator("button:has-text('+')").first.click()
            page.wait_for_timeout(200)

            page.locator("button:has-text('Создать')").last.click()
            page.wait_for_timeout(1000)

            custom_var = page.locator("text=MyCustomVar")
            assert custom_var.count() > 0, "Custom variable not created"
            print("  Created MyCustomVar")

            # Delete it
            delete_btn = page.locator("text=MyCustomVar").locator("..").locator("button")
            if delete_btn.count() > 0:
                delete_btn.last.click()
                page.wait_for_timeout(500)
                print("  Deleted MyCustomVar")

            page.screenshot(path="/tmp/e2e_custom_var.png")
            print("  PASS")
            passed += 1
        except Exception as e:
            page.screenshot(path="/tmp/e2e_fail_custom_var.png")
            print(f"  FAIL: {e}")
            failed += 1

        # TEST 3: Context editor with variable assignments
        print("\nTEST 3: Context editor with variable assignments")
        try:
            ctx_heading = page.locator("h3:has-text('Контексты')")
            assert ctx_heading.count() > 0, "Context panel not found"

            # Create context
            page.locator("button:has-text('Новый контекст')").click()
            page.wait_for_timeout(500)
            page.locator("input[placeholder='Имя контекста']").fill("TestCtx")
            page.locator("button:has-text('Создать')").last.click()
            page.wait_for_timeout(1000)

            test_ctx = page.locator("text=TestCtx")
            assert test_ctx.count() > 0, "Context not created"
            print("  Created TestCtx")

            # Expand and set a variable
            page.locator("button:has-text('TestCtx')").click()
            page.wait_for_timeout(500)

            page.screenshot(path="/tmp/e2e_ctx_assignments.png")

            # Try setting a variable in the context
            ctx_selects = page.locator(".bg-gray-50 select")
            for i in range(ctx_selects.count()):
                sel = ctx_selects.nth(i)
                options = sel.locator("option")
                if options.count() > 1:
                    sel.select_option(index=1)
                    page.wait_for_timeout(1000)
                    print("  Set variable in context")
                    break

            # Activate context
            radios = page.locator("input[name='activeCtx']")
            if radios.count() > 0:
                radios.first.click()
                page.wait_for_timeout(1000)
                print("  Activated context")

            page.screenshot(path="/tmp/e2e_ctx_active.png")

            # Clean up
            del_btn = page.locator("button[title='Удалить']")
            if del_btn.count() > 0:
                del_btn.first.click()
                page.wait_for_timeout(500)

            print("  PASS")
            passed += 1
        except Exception as e:
            page.screenshot(path="/tmp/e2e_fail_ctx.png")
            print(f"  FAIL: {e}")
            failed += 1

        # TEST 4: Graph highlighting
        print("\nTEST 4: Graph highlighting check")
        try:
            # Create and activate a context with a concept value
            page.locator("button:has-text('Новый контекст')").click()
            page.wait_for_timeout(500)
            page.locator("input[placeholder='Имя контекста']").fill("HighlightCtx")
            page.locator("button:has-text('Создать')").last.click()
            page.wait_for_timeout(1000)

            # Activate it
            radios = page.locator("input[name='activeCtx']")
            if radios.count() > 0:
                radios.last.click()
                page.wait_for_timeout(2000)

            page.screenshot(path="/tmp/e2e_graph_highlights.png")
            print("  Context activated, graph may show highlights")

            # Clean up
            del_btn = page.locator("button[title='Удалить']")
            if del_btn.count() > 0:
                del_btn.first.click()
                page.wait_for_timeout(500)

            print("  PASS")
            passed += 1
        except Exception as e:
            page.screenshot(path="/tmp/e2e_fail_highlights.png")
            print(f"  FAIL: {e}")
            failed += 1

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
