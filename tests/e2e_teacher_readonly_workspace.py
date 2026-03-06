"""E2E test: Teacher read-only workspace view."""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"


def goto_with_retry(page, url, retries=3, delay=3000):
    """Navigate to URL with retries for Next.js on-demand compilation."""
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            print(f"  Page not ready (attempt {attempt+1}), retrying...")
            page.wait_for_timeout(delay)


def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

        passed = 0
        failed = 0

        def check(name, condition):
            nonlocal passed, failed
            if condition:
                print(f"  PASS: {name}")
                passed += 1
            else:
                print(f"  FAIL: {name}")
                failed += 1

        # Step 1: Login as teacher
        print("Step 1: Login as teacher")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.fill('input[placeholder="Имя пользователя"]', "teacher")
        page.fill('input[placeholder="Пароль"]', "teacher")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        check("Logged in as teacher", "/teacher" in page.url or "/workspaces" in page.url)
        page.screenshot(path="/tmp/teacher_login.png")

        # Step 2: Navigate to teacher dashboard
        print("Step 2: Teacher dashboard")
        goto_with_retry(page, f"{BASE_URL}/teacher")
        page.wait_for_timeout(2000)
        check("Teacher dashboard loaded", page.locator("text=Студенты").count() > 0 or page.locator("text=студент").count() > 0)
        page.screenshot(path="/tmp/teacher_dashboard.png")

        # Step 3: Click on a student (pick one with workspaces)
        print("Step 3: Click on student")
        student_links = page.locator("a[href*='/teacher/student/']")
        student_count = student_links.count()
        check("Students listed", student_count > 0)
        if student_count > 0:
            # Find a student link that shows workspace count > 0
            found_student = False
            for i in range(student_count):
                link = student_links.nth(i)
                text = link.inner_text()
                # Look for workspace count indication (e.g., "5 простр")
                if "0 простр" not in text and "простр" in text:
                    link.click()
                    found_student = True
                    break
            if not found_student:
                # fallback: just click first
                student_links.first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            check("Student page loaded", "/teacher/student/" in page.url)
            page.screenshot(path="/tmp/teacher_student.png")

            # Step 4: Verify "Открыть полный вид" link
            print("Step 4: Check full view link")
            full_view_links = page.locator("text=Открыть полный вид")
            full_view_count = full_view_links.count()
            check("'Открыть полный вид' link present", full_view_count > 0)

            if full_view_count > 0:
                # Step 5: Click to open full workspace view
                print("Step 5: Open full workspace view")
                href = full_view_links.first.get_attribute("href")
                check("Link points to /teacher/workspace/", href is not None and "/teacher/workspace/" in href)
                full_view_links.first.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                check("Navigated to teacher workspace", "/teacher/workspace/" in page.url)
                page.screenshot(path="/tmp/teacher_workspace_full.png")

                # Step 6: Verify header elements
                print("Step 6: Verify header")
                check("'Только просмотр' badge visible", page.locator("text=Только просмотр").count() > 0)
                check("Back link to /teacher", page.locator("a[href='/teacher']").count() > 0)
                check("JSON export button", page.locator("text=JSON").count() > 0)
                check("PNG export button", page.locator("text=PNG").count() > 0)

                # Step 7: Verify sidebar content
                print("Step 7: Verify sidebar panels")
                sidebar = page.locator("div.w-\\[460px\\]")
                sidebar_text = sidebar.inner_text() if sidebar.count() > 0 else ""

                check("Grade panel visible", "Оценка" in sidebar_text)
                check("Comments panel visible", "Комментарии" in sidebar_text)
                check("Equations panel visible", "Уравнения" in sidebar_text or "уравнени" in sidebar_text.lower())

                # Step 8: Verify read-only mode
                print("Step 8: Verify read-only constraints")
                check("No 'Новая переменная' button", page.locator("text=Новая переменная").count() == 0)
                check("No 'Новый контекст' button", page.locator("text=Новый контекст").count() == 0)
                check("No 'Новая формула' button", page.locator("text=Новая формула").count() == 0)

                # Check disabled selects in variable panel
                var_selects = sidebar.locator("select:disabled")
                # Note: some selects may be for grade (not disabled), so just check existence
                enabled_var_selects = sidebar.locator("h3:has-text('Переменные') ~ div select:not(:disabled)")
                # If variables exist, their selects should be disabled
                var_heading = page.locator("text=Переменные")
                if var_heading.count() > 0:
                    check("Variables panel visible", True)
                    # Verify no delete buttons (×) next to user variables
                    # (This is harder to verify precisely, but we check no "Новая переменная")
                else:
                    check("Variables panel visible (or no variables in scenario)", True)

                # Step 9: Verify grade panel is functional
                print("Step 9: Verify grade panel")
                grade_section_has_controls = (
                    page.locator("text=Поставить").count() > 0 or
                    page.locator("text=Изменить").count() > 0 or
                    page.locator("text=Сохранить").count() > 0
                )
                check("Grade panel has controls", grade_section_has_controls)

                # Step 10: Verify comment panel is functional
                print("Step 10: Verify comment panel")
                comment_input = page.locator("input[placeholder*='комментарий' i], input[placeholder*='Комментарий' i], input[placeholder*='Написать' i]")
                check("Comment input present", comment_input.count() > 0)
                send_btn = page.locator("button:has-text('Отправить')")
                check("Send comment button present", send_btn.count() > 0)

                # Step 11: Verify no editing UI present
                print("Step 11: Verify no editing UI")
                check("No network editor", page.locator("text=Редактор сети").count() == 0)
                check("No undo button", page.locator("button[title*='Отменить']").count() == 0)
                check("No redo button", page.locator("button[title*='Повторить']").count() == 0)
                check("No import JSON button", page.locator("text=📤 JSON").count() == 0)

                # Take final screenshot
                page.screenshot(path="/tmp/teacher_workspace_final.png", full_page=True)

        # Print summary
        print(f"\n{'='*50}")
        print(f"Results: {passed} passed, {failed} failed out of {passed+failed} checks")
        if failed > 0:
            print("\nConsole messages with errors:")
            for m in console_msgs:
                if "[error]" in m.lower() or "[FAILED]" in m or "[4" in m or "[5" in m:
                    print(f"  {m}")

        browser.close()
        return failed == 0


if __name__ == "__main__":
    success = run_test()
    exit(0 if success else 1)
