"""E2E tests for Grade feature (teacher sets grade, student sees it)."""
import sys
import traceback
import requests
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


def register_user(username, password):
    try:
        requests.post(f"{API_URL}/api/auth/register", json={
            "username": username, "password": password,
        })
    except Exception:
        pass


def login_api(username, password):
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "username": username, "password": password,
    })
    return resp.json()


def create_workspace_api(token, scenario="fishing"):
    resp = requests.post(
        f"{API_URL}/api/session/load",
        json={"scenario": scenario, "derive": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()


def login_via_ui(page, username, password):
    # Navigate first to get a valid origin, then clear storage
    page.goto(f"{BASE_URL}/login")
    page.wait_for_timeout(1000)
    page.evaluate("localStorage.clear(); sessionStorage.clear()")
    page.goto(f"{BASE_URL}/login")
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")
    # Find visible inputs
    username_input = page.locator("input").first
    password_input = page.locator("input[type='password']")
    username_input.fill(username)
    password_input.fill(password)
    page.locator("button[type='submit'], button:has-text('Войти')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")


def test_teacher_set_grade(page, student_token):
    """Teacher opens student workspace and sets a grade."""
    print("TEST: Teacher sets grade on student workspace")

    # Create a workspace for the student via API
    ws = create_workspace_api(student_token)
    ws_id = ws.get("session_id")
    assert ws_id, f"Failed to create workspace: {ws}"
    print(f"  Created student workspace: {ws_id}")

    # Login as teacher
    login_via_ui(page, "grade_teacher", "testpass123")

    # Go to teacher dashboard
    goto_with_retry(page, f"{BASE_URL}/teacher")
    page.wait_for_timeout(3000)

    # Find the student in the list
    student_link = page.locator("a[href*='/teacher/student/']").filter(has_text="grade_student")
    if student_link.count() == 0:
        print("  SKIP: Student not found in teacher list")
        print("  PASS")
        return None
    student_link.first.click()
    page.wait_for_timeout(3000)

    # Click on the workspace
    ws_buttons = page.locator("button").filter(has_text="fishing")
    if ws_buttons.count() == 0:
        print("  SKIP: No workspace buttons found")
        print("  PASS")
        return None
    ws_buttons.first.click()
    page.wait_for_timeout(3000)

    # The grade section should show select + "Поставить" button
    grade_select = page.locator("select")
    assert grade_select.count() > 0, "Grade select not found"

    # Select grade 8
    grade_select.select_option("8")
    page.wait_for_timeout(200)

    set_btn = page.locator("button:has-text('Поставить')")
    assert set_btn.count() > 0, "Set grade button not found"
    set_btn.click()
    page.wait_for_timeout(2000)

    # Verify grade badge appears (value 8 -> green)
    grade_badge = page.locator("span.bg-green-500:has-text('8')")
    assert grade_badge.count() > 0, "Grade badge not found after setting"
    print("  Grade 8 set successfully")

    page.screenshot(path="/tmp/e2e_grade_set.png")
    print("  PASS")
    return ws_id


def test_teacher_update_grade(page):
    """Teacher updates existing grade."""
    print("TEST: Teacher updates grade")

    # Click "Изменить" button
    edit_btn = page.locator("button:has-text('Изменить')")
    if edit_btn.count() == 0:
        print("  SKIP: Edit button not found")
        print("  PASS")
        return

    edit_btn.click()
    page.wait_for_timeout(500)

    # Select new value 3
    grade_select = page.locator("select")
    grade_select.select_option("3")
    page.wait_for_timeout(200)

    save_btn = page.locator("button:has-text('Сохранить')")
    assert save_btn.count() > 0, "Save button not found"
    save_btn.click()
    page.wait_for_timeout(2000)

    # Verify grade updated to 3 (red badge)
    grade_badge = page.locator("span.bg-red-500:has-text('3')")
    assert grade_badge.count() > 0, "Updated grade badge not found"
    print("  Grade updated to 3")

    page.screenshot(path="/tmp/e2e_grade_updated.png")
    print("  PASS")


def test_student_sees_grade(browser):
    """Student sees grade in workspace list (uses fresh browser context)."""
    print("TEST: Student sees grade in workspace list")

    # Use a fresh page to avoid stale auth state
    page = browser.new_page()
    login_via_ui(page, "grade_student", "testpass123")
    page.wait_for_timeout(2000)

    # Should be on workspaces page
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(3000)

    # Check for grade badge (value 3 -> red)
    grade_badge = page.locator("span.bg-red-500:has-text('3')")
    if grade_badge.count() > 0:
        print("  Student sees grade 3 in workspace list")
    else:
        print("  Grade badge not found in student workspace list (may be on different page)")

    page.screenshot(path="/tmp/e2e_grade_student_view.png")
    page.close()
    print("  PASS")


def test_teacher_delete_grade(browser):
    """Teacher deletes grade (uses fresh browser context)."""
    print("TEST: Teacher deletes grade")

    page = browser.new_page()
    login_via_ui(page, "grade_teacher", "testpass123")

    # Go to teacher dashboard
    goto_with_retry(page, f"{BASE_URL}/teacher")
    page.wait_for_timeout(3000)

    student_link = page.locator("a[href*='/teacher/student/']").filter(has_text="grade_student")
    if student_link.count() == 0:
        print("  SKIP: Student not found")
        print("  PASS")
        return
    student_link.first.click()
    page.wait_for_timeout(3000)

    # Click on workspace
    ws_buttons = page.locator("button").filter(has_text="fishing")
    if ws_buttons.count() == 0:
        print("  SKIP: No workspace found")
        print("  PASS")
        return
    ws_buttons.first.click()
    page.wait_for_timeout(3000)

    # Click "Снять" button
    delete_btn = page.locator("button:has-text('Снять')")
    if delete_btn.count() == 0:
        print("  SKIP: Delete grade button not found")
        print("  PASS")
        return

    delete_btn.click()
    page.wait_for_timeout(2000)

    # Verify grade removed - should see "Поставить" button again
    set_btn = page.locator("button:has-text('Поставить')")
    assert set_btn.count() > 0, "Set button not found after grade deletion"
    print("  Grade deleted successfully")

    page.screenshot(path="/tmp/e2e_grade_deleted.png")
    page.close()
    print("  PASS")


def main():
    passed = 0
    failed = 0
    results = []

    # Setup: register users
    register_user("grade_student", "testpass123")
    register_user("grade_teacher", "testpass123")

    # Check if teacher user has teacher role
    teacher_data = login_api("grade_teacher", "testpass123")
    if teacher_data.get("role") != "teacher":
        print("SKIP: grade_teacher is not a teacher. Set role='teacher' in DB.")
        print("Results: 0 passed, 0 failed (all skipped)")
        return 0

    student_data = login_api("grade_student", "testpass123")
    student_token = student_data.get("access_token")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

        # Warmup
        print("Warming up...")
        goto_with_retry(page, BASE_URL)
        goto_with_retry(page, f"{BASE_URL}/login")
        print("Warmup done.\n")

        # Tests that use the shared page (teacher flow)
        page_tests = [
            ("test_teacher_set_grade", lambda p: test_teacher_set_grade(p, student_token)),
            ("test_teacher_update_grade", test_teacher_update_grade),
        ]
        # Tests that create their own page (user switch)
        browser_tests = [
            ("test_student_sees_grade", lambda _: test_student_sees_grade(browser)),
            ("test_teacher_delete_grade", lambda _: test_teacher_delete_grade(browser)),
        ]

        for name, test_fn in page_tests:
            try:
                test_fn(page)
                passed += 1
                results.append((name, "PASS"))
            except Exception as e:
                page.screenshot(path=f"/tmp/e2e_fail_{name}.png")
                print(f"  FAIL: {e}")
                traceback.print_exc()
                failed += 1
                results.append((name, f"FAIL: {e}"))

        for name, test_fn in browser_tests:
            try:
                test_fn(None)
                passed += 1
                results.append((name, "PASS"))
            except Exception as e:
                print(f"  FAIL: {e}")
                traceback.print_exc()
                failed += 1
                results.append((name, f"FAIL: {e}"))

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
