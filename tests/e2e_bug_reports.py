"""E2E test for bug report feature: student submits bug, teacher manages it.

Run with:
  python3 -m pytest tests/e2e_bug_reports.py -x
"""
import glob
import json
import sqlite3
import time
import urllib.request

from conftest import BASE_URL, API_BASE, goto_with_retry

STUDENT_USER = f"bug_student_{int(time.time())}"
TEACHER_USER = f"bug_teacher_{int(time.time())}"
PASSWORD = "testpass123"


def _register_user(page, username, password):
    goto_with_retry(page, f"{BASE_URL}/register")
    page.fill('input[type="text"]', username)
    page.fill('input[type="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)


def _login_user(page, username, password):
    goto_with_retry(page, f"{BASE_URL}/login")
    page.fill('input[type="text"]', username)
    page.fill('input[type="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)


def _promote_to_teacher(username):
    """Promote user to teacher via direct DB update."""
    db_paths = glob.glob("/Users/dmaksimov/TestProjects/ctmsn/apps/api/*.db")
    if not db_paths:
        db_paths = glob.glob("/Users/dmaksimov/TestProjects/ctmsn/*.db")
    if not db_paths:
        db_paths = ["ctmsn.db"]

    for p in db_paths:
        try:
            conn = sqlite3.connect(p)
            conn.execute("UPDATE users SET role='teacher' WHERE username=?", (username,))
            conn.commit()
            conn.close()
            return
        except Exception:
            continue

    raise RuntimeError("Could not promote user to teacher")


def test_register_student(page, context):
    """Register a student user."""
    _register_user(page, STUDENT_USER, PASSWORD)
    assert "/workspaces" in page.url or "/login" in page.url, f"Registration failed, at {page.url}"

    if "/workspaces" not in page.url:
        _login_user(page, STUDENT_USER, PASSWORD)
    assert "/workspaces" in page.url, f"Login failed, at {page.url}"


def test_open_bug_form(page):
    """Open bug report form from workspaces page."""
    page.wait_for_timeout(500)
    bug_button = page.locator("text=Сообщить о баге")
    assert bug_button.count() > 0, "Bug report button not found on /workspaces"
    bug_button.click()
    page.wait_for_timeout(500)

    assert page.locator("h3:has-text('Сообщить о баге')").count() > 0, "Bug report modal not found"


def test_submit_bug_report(page):
    """Fill and submit a bug report."""
    page.locator('input[placeholder*="Кратко"]').fill("Тестовый баг: кнопка не работает")
    page.locator('textarea[placeholder*="Подробное"]').fill(
        "При нажатии на кнопку ничего не происходит. Шаги: 1) Открыть страницу 2) Нажать кнопку"
    )
    page.locator('button:has-text("Отправить")').click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")

    modal_count = page.locator("h3:has-text('Сообщить о баге')").count()
    assert modal_count == 0, f"Modal still open after submit (count={modal_count})"


def test_teacher_setup(_browser):
    """Register teacher in a fresh context (no shared auth state), promote via DB."""
    # Use a fresh browser context to avoid sharing localStorage with the student session
    fresh_ctx = _browser.new_context()
    teacher_page = fresh_ctx.new_page()
    _register_user(teacher_page, TEACHER_USER, PASSWORD)
    teacher_page.close()
    fresh_ctx.close()

    _promote_to_teacher(TEACHER_USER)


def test_teacher_sees_bug(_browser):
    """Log in as teacher in a fresh context and verify the bug is visible."""
    # Use a fresh browser context for the teacher session
    fresh_ctx = _browser.new_context()
    teacher_page = fresh_ctx.new_page()

    _login_user(teacher_page, TEACHER_USER, PASSWORD)
    teacher_page.wait_for_timeout(500)

    goto_with_retry(teacher_page, f"{BASE_URL}/teacher/bugs")
    teacher_page.wait_for_timeout(2000)

    assert teacher_page.locator("text=Тестовый баг: кнопка не работает").count() > 0, \
        "Teacher doesn't see student's bug report"
    assert teacher_page.locator("text=Открыт").count() > 0, "Open badge not found"
    assert teacher_page.locator(f"text={STUDENT_USER}").count() > 0, "Author username not visible"

    # Store page and context references for subsequent tests via module-level
    test_teacher_sees_bug._teacher_page = teacher_page
    test_teacher_sees_bug._teacher_ctx = fresh_ctx


def test_close_bug(page):
    """Teacher closes the bug."""
    tp = test_teacher_sees_bug._teacher_page
    tp.locator('button:has-text("Закрыть")').first.click()
    tp.wait_for_timeout(1000)

    assert tp.locator("text=Закрыт").count() > 0, "Closed badge not found after status change"


def test_reopen_bug(page):
    """Teacher reopens the bug."""
    tp = test_teacher_sees_bug._teacher_page
    tp.locator('button:has-text("Открыть")').first.click()
    tp.wait_for_timeout(1000)

    assert tp.locator("text=Открыт").count() > 0, "Bug not reopened"


def test_filter_bugs(page):
    """Test bug filter buttons."""
    tp = test_teacher_sees_bug._teacher_page

    tp.locator('button:has-text("Закрытые")').click()
    tp.wait_for_timeout(1000)
    assert tp.locator("text=Тестовый баг: кнопка не работает").count() == 0, \
        "Open bug visible in closed filter"

    tp.locator('button:has-text("Все")').click()
    tp.wait_for_timeout(1000)
    assert tp.locator("text=Тестовый баг: кнопка не работает").count() > 0, \
        "Bug not visible in 'All' filter"


def test_delete_bug(page):
    """Teacher deletes the bug."""
    tp = test_teacher_sees_bug._teacher_page
    bug_loc = tp.locator("text=Тестовый баг: кнопка не работает")
    count_before = bug_loc.count()

    tp.on("dialog", lambda dialog: dialog.accept())
    with tp.expect_response(lambda r: "/api/teacher/bugs/" in r.url and r.request.method == "DELETE"):
        tp.locator('button:has-text("Удалить")').first.click()

    tp.wait_for_timeout(1000)
    assert bug_loc.count() == count_before - 1, \
        f"Bug not removed after deletion (before={count_before}, after={bug_loc.count()})"

    tp.close()
    test_teacher_sees_bug._teacher_ctx.close()


def test_student_cannot_access_teacher_bugs(_browser):
    """Verify student cannot access /teacher/bugs."""
    fresh_ctx = _browser.new_context()
    student_page = fresh_ctx.new_page()
    _login_user(student_page, STUDENT_USER, PASSWORD)
    student_page.goto(f"{BASE_URL}/teacher/bugs")
    student_page.wait_for_load_state("networkidle")
    student_page.wait_for_timeout(2000)

    assert "/teacher/bugs" not in student_page.url or \
        student_page.locator("text=Баг-репорты").count() == 0, \
        f"Student has access to teacher bugs page! URL: {student_page.url}"

    student_page.close()
    fresh_ctx.close()
