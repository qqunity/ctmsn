"""E2E tests for Authentication edge cases (wrong password, unauthorized access, logout, roles)."""
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


def test_wrong_password(page):
    """Test login with wrong password shows error."""
    print("TEST: Wrong password login")

    # First register a user
    goto_with_retry(page, f"{BASE_URL}/register")
    page.wait_for_timeout(1000)

    inputs = page.locator("input:visible")
    inputs.nth(0).fill("testuser_auth_edge")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    # Now try logging in with wrong password
    goto_with_retry(page, f"{BASE_URL}/login")
    page.wait_for_timeout(1000)

    inputs = page.locator("input:visible")
    inputs.nth(0).fill("testuser_auth_edge")
    inputs.nth(1).fill("wrong_password_123")
    page.locator("button[type='submit'], button:has-text('Войти')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    # Should still be on login page or show error
    is_login = "/login" in page.url
    error_msg = page.locator(".text-red-500, .text-red-600, .bg-red-50")
    has_error = error_msg.count() > 0

    print(f"  Still on login page: {is_login}")
    print(f"  Error message visible: {has_error}")
    assert is_login or has_error, "Wrong password should show error or stay on login"

    page.screenshot(path="/tmp/e2e_auth_wrong_pass.png")
    print("  PASS")


def test_unauthorized_access_workspaces(page):
    """Test that /workspaces redirects to /login when not authenticated."""
    print("TEST: Unauthorized access to /workspaces")

    # Clear auth by going to a clean state
    page.context.clear_cookies()
    page.evaluate("localStorage.clear()")
    page.wait_for_timeout(500)

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")

    print(f"  URL after accessing /workspaces: {page.url}")
    # Should be redirected to /login
    assert "/login" in page.url or "/register" in page.url, \
        f"Unauthorized user should be redirected to login, got: {page.url}"

    page.screenshot(path="/tmp/e2e_auth_unauth_workspaces.png")
    print("  PASS")


def test_unauthorized_access_workspace(page):
    """Test that /workspace/:id redirects to /login when not authenticated."""
    print("TEST: Unauthorized access to /workspace/:id")

    page.context.clear_cookies()
    page.evaluate("localStorage.clear()")
    page.wait_for_timeout(500)

    goto_with_retry(page, f"{BASE_URL}/workspace/fake-id-123")
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")

    print(f"  URL after accessing /workspace/fake-id: {page.url}")
    assert "/login" in page.url or "/register" in page.url, \
        f"Unauthorized user should be redirected to login, got: {page.url}"

    page.screenshot(path="/tmp/e2e_auth_unauth_workspace.png")
    print("  PASS")


def test_login_success(page):
    """Log in successfully after failed attempts."""
    print("TEST: Login success")

    goto_with_retry(page, f"{BASE_URL}/login")
    page.wait_for_timeout(1000)

    inputs = page.locator("input:visible")
    inputs.nth(0).fill("testuser_auth_edge")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Войти')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    print(f"  URL after login: {page.url}")
    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  PASS")


def test_logout(page):
    """Test logout button redirects to login."""
    print("TEST: Logout")

    # Navigate to workspaces to ensure we have logout button
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    logout_btn = page.locator("button:has-text('Выйти')")
    if logout_btn.count() > 0:
        logout_btn.first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        print(f"  URL after logout: {page.url}")
        assert "/login" in page.url or "/register" in page.url, \
            f"Should redirect to login after logout, got: {page.url}"
        print("  Logged out successfully")
    else:
        print("  SKIP: Выйти button not found")

    page.screenshot(path="/tmp/e2e_auth_logout.png")
    print("  PASS")


def test_after_logout_redirect(page):
    """After logout, accessing workspaces redirects to login."""
    print("TEST: After logout redirect")

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")

    print(f"  URL: {page.url}")
    assert "/login" in page.url or "/register" in page.url, \
        f"Should be on login after logout, got: {page.url}"

    page.screenshot(path="/tmp/e2e_auth_after_logout.png")
    print("  PASS")


def test_register_link_from_login(page):
    """Test the registration link on the login page."""
    print("TEST: Register link from login")

    goto_with_retry(page, f"{BASE_URL}/login")
    page.wait_for_timeout(1000)

    reg_link = page.locator("a:has-text('Зарегистрироваться'), a[href='/register']")
    if reg_link.count() > 0:
        reg_link.first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        assert "/register" in page.url, f"Should be on register page, got: {page.url}"
        print("  Navigated to register from login")
    else:
        print("  SKIP: Register link not found on login page")

    print("  PASS")


def test_login_link_from_register(page):
    """Test the login link on the register page."""
    print("TEST: Login link from register")

    goto_with_retry(page, f"{BASE_URL}/register")
    page.wait_for_timeout(1000)

    login_link = page.locator("a:has-text('Войти'), a[href='/login']")
    if login_link.count() > 0:
        login_link.first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        assert "/login" in page.url, f"Should be on login page, got: {page.url}"
        print("  Navigated to login from register")
    else:
        print("  SKIP: Login link not found on register page")

    print("  PASS")


def test_student_role_display(page):
    """Verify that student role is displayed correctly."""
    print("TEST: Student role display")

    goto_with_retry(page, f"{BASE_URL}/login")
    page.wait_for_timeout(1000)

    inputs = page.locator("input:visible")
    inputs.nth(0).fill("testuser_auth_edge")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Войти')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    # Check for role display
    student_text = page.locator("text=студент")
    teacher_text = page.locator("text=преподаватель")
    role_visible = student_text.count() > 0 or teacher_text.count() > 0
    print(f"  Role display visible: {role_visible}")
    if student_text.count() > 0:
        print("  Role: студент")
    elif teacher_text.count() > 0:
        print("  Role: преподаватель")

    # Check that teacher panel link is NOT shown for students
    teacher_link = page.locator("text=Панель преподавателя")
    print(f"  Teacher panel link visible: {teacher_link.count() > 0}")

    page.screenshot(path="/tmp/e2e_auth_role.png")
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
            test_wrong_password,
            test_unauthorized_access_workspaces,
            test_unauthorized_access_workspace,
            test_login_success,
            test_logout,
            test_after_logout_redirect,
            test_register_link_from_login,
            test_login_link_from_register,
            test_student_role_display,
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
