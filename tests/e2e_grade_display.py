"""Test that grade displays correctly in teacher read-only workspace view."""
import random
import string
import sqlite3
import requests
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
API_URL = "http://127.0.0.1:8000"
DB_PATH = "/Users/dmaksimov/TestProjects/ctmsn/apps/api/ctmsn.db"

suffix = "".join(random.choices(string.ascii_lowercase, k=5))
STUDENT_USER = f"s_{suffix}"
TEACHER_USER = f"t_{suffix}"
PASSWORD = "testpass123"

def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            page.wait_for_timeout(delay)

# --- Setup via API ---
print(f"Setting up test data (student={STUDENT_USER}, teacher={TEACHER_USER})...")

# Register student
r = requests.post(f"{API_URL}/api/auth/register", json={"username": STUDENT_USER, "password": PASSWORD})
assert r.status_code == 200, f"Register student failed: {r.text}"
student_token = r.json()["access_token"]

# Register teacher (as student, then promote in DB)
r = requests.post(f"{API_URL}/api/auth/register", json={"username": TEACHER_USER, "password": PASSWORD})
assert r.status_code == 200, f"Register teacher failed: {r.text}"

conn = sqlite3.connect(DB_PATH)
conn.execute("UPDATE users SET role='teacher' WHERE username=?", (TEACHER_USER,))
conn.commit()
conn.close()

# Re-login teacher to get token with teacher role
r = requests.post(f"{API_URL}/api/auth/login", json={"username": TEACHER_USER, "password": PASSWORD})
assert r.status_code == 200
teacher_token = r.json()["access_token"]
print(f"  Teacher role: {r.json()['role']}")

# Create workspace as student via session/load
headers_s = {"Authorization": f"Bearer {student_token}"}
headers_t = {"Authorization": f"Bearer {teacher_token}"}

r = requests.post(f"{API_URL}/api/session/load", json={"scenario": "fishing"}, headers=headers_s)
assert r.status_code == 200, f"Load scenario failed: {r.text}"
ws_id = r.json()["session_id"]
print(f"  Created workspace: {ws_id}")

# Set grade as teacher
r = requests.put(f"{API_URL}/api/teacher/workspaces/{ws_id}/grade", json={"value": 8}, headers=headers_t)
assert r.status_code == 200, f"Set grade failed: {r.text}"
grade_data = r.json()
print(f"  Grade set: value={grade_data.get('value')}, teacher={grade_data.get('teacher_username')}")

# --- Playwright test ---
print("\nStarting browser test...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Warmup
    warmup = browser.new_page()
    warmup.goto(BASE_URL)
    warmup.wait_for_load_state("networkidle")
    warmup.wait_for_timeout(2000)
    goto_with_retry(warmup, f"{BASE_URL}/login")
    goto_with_retry(warmup, f"{BASE_URL}/teacher/workspace/{ws_id}")
    warmup.close()

    page = browser.new_page()
    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

    # Login as teacher
    print("Logging in as teacher...")
    goto_with_retry(page, f"{BASE_URL}/login")
    page.get_by_placeholder("Имя пользователя").fill(TEACHER_USER)
    page.get_by_placeholder("Пароль").fill(PASSWORD)
    page.get_by_role("button", name="Войти").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    print(f"  URL after login: {page.url}")

    if "/login" in page.url:
        page.screenshot(path="/tmp/grade_login_fail.png", full_page=True)
        print("  ERROR: Login failed!")
        browser.close()
        exit(1)

    # Navigate to teacher workspace view
    url = f"{BASE_URL}/teacher/workspace/{ws_id}"
    print(f"Opening {url}")
    goto_with_retry(page, url)
    page.wait_for_timeout(3000)
    page.screenshot(path="/tmp/grade_02_workspace.png", full_page=True)

    # Check for grade display
    grade_heading = page.locator("text=Оценка")
    grade_badge = page.locator(".rounded-full")

    has_heading = grade_heading.count() > 0
    has_badge = grade_badge.count() > 0

    print(f"  'Оценка' heading: {has_heading}")
    print(f"  Grade badge: {has_badge}")

    if has_badge:
        badge_text = grade_badge.first.text_content()
        print(f"  Grade value: {badge_text}")

    errors = [m for m in console_msgs if "[4" in m or "[5" in m or "FAILED" in m]
    if errors:
        print("\nHTTP errors:")
        for m in errors[:10]:
            print(f"  {m}")

    if has_heading and has_badge:
        print("\nSUCCESS: Grade is displayed correctly in teacher workspace view!")
    else:
        print("\nFAILURE: Grade not displayed.")
        page.screenshot(path="/tmp/grade_03_debug.png", full_page=True)
        body = page.locator("body").text_content()
        print(f"  Page text: {body[:500]}")

    browser.close()
