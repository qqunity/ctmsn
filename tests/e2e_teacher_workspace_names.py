"""Verify teacher's student page shows workspace name and scenario subtitle."""
import random
import string
import sqlite3
import requests
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"
DB_PATH = "/Users/dmaksimov/TestProjects/ctmsn/apps/api/ctmsn.db"

suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
TEACHER = f"t_{suffix}"
STUDENT = f"s_{suffix}"
PASSWORD = "test123"

# Register student
r = requests.post(f"{API_URL}/api/auth/register", json={"username": STUDENT, "password": PASSWORD})
r.raise_for_status()
student_token = r.json()["access_token"]
print(f"Registered student: {STUDENT}")

# Create workspace via session/load
headers = {"Authorization": f"Bearer {student_token}"}
r = requests.post(f"{API_URL}/api/session/load", json={"scenario": "fishing"}, headers=headers)
r.raise_for_status()
session_data = r.json()
ws_id = session_data.get("session_id")
print(f"Created workspace, session_id: {ws_id}")

# Rename workspace
r = requests.patch(f"{API_URL}/api/workspaces/{ws_id}", json={"name": "My Test WS"}, headers=headers)
r.raise_for_status()
print("Renamed workspace")

# Register teacher
r = requests.post(f"{API_URL}/api/auth/register", json={"username": TEACHER, "password": PASSWORD})
r.raise_for_status()
db = sqlite3.connect(DB_PATH)
db.execute("UPDATE users SET role='teacher' WHERE username=?", (TEACHER,))
db.commit()
db.close()
print(f"Registered teacher: {TEACHER}")

# Login teacher to get fresh token
r = requests.post(f"{API_URL}/api/auth/login", json={"username": TEACHER, "password": PASSWORD})
r.raise_for_status()
teacher_token = r.json()["access_token"]

# Verify via API
r = requests.get(f"{API_URL}/api/teacher/students", headers={"Authorization": f"Bearer {teacher_token}"})
r.raise_for_status()
students = r.json()
our_student = [s for s in students if s["username"] == STUDENT]
print(f"Student found in API: {len(our_student) > 0}")

student_id = our_student[0]["id"]
r = requests.get(f"{API_URL}/api/teacher/students/{student_id}/workspaces", headers={"Authorization": f"Bearer {teacher_token}"})
r.raise_for_status()
ws_list = r.json()
print(f"Workspaces via API: {ws_list}")

# --- Playwright test ---
def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            page.wait_for_timeout(delay)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Login as teacher
    goto_with_retry(page, f"{BASE_URL}/login")
    page.fill('input[placeholder="Имя пользователя"]', TEACHER)
    page.fill('input[placeholder="Пароль"]', PASSWORD)
    page.click('button:has-text("Войти")')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    print(f"Logged in, URL: {page.url}")

    # Go to teacher page
    goto_with_retry(page, f"{BASE_URL}/teacher")
    page.wait_for_timeout(1000)

    # Click student
    student_link = page.locator(f"text={STUDENT}").first
    if not student_link.is_visible():
        page.screenshot(path="/tmp/teacher_list.png", full_page=True)
        print("Student not visible, see /tmp/teacher_list.png")
        browser.close()
        exit(1)

    student_link.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    page.screenshot(path="/tmp/teacher_student_page.png", full_page=True)
    print(f"Student page: {page.url}")

    # Find workspace buttons
    workspace_buttons = page.locator("button.w-full.text-left").all()
    print(f"Found {len(workspace_buttons)} workspace buttons")
    assert len(workspace_buttons) > 0, "No workspace buttons!"

    btn = workspace_buttons[0]
    text = btn.inner_text()
    print(f"Button text: {repr(text)}")

    # Check name element
    name_el = btn.locator("span.font-medium.truncate")
    assert name_el.count() > 0, "Missing span.font-medium.truncate"
    name_text = name_el.inner_text()
    print(f"Name: {repr(name_text)}")
    assert name_text == "My Test WS", f"Expected 'My Test WS', got: {name_text}"

    # Check scenario subtitle
    scenario_el = btn.locator("span.text-gray-500.text-xs")
    assert scenario_el.count() > 0, "Missing scenario subtitle"
    scenario_text = scenario_el.inner_text()
    print(f"Scenario: {repr(scenario_text)}")
    assert "fishing" in scenario_text, f"Expected 'fishing' in subtitle, got: {scenario_text}"

    print("\nAll assertions passed!")
    browser.close()
