"""Test that HelpPanel shows scenario-specific task description."""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"

def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            print(f"  Page not ready (attempt {attempt+1}), retrying...")
            page.wait_for_timeout(delay)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Warmup & login
    goto_with_retry(page, BASE_URL)
    page.wait_for_timeout(2000)

    if "/login" in page.url or page.locator("text=Войти").count() > 0:
        print("Logging in...")
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        page.locator('input[type="text"]').first.fill("testuser2")
        page.locator('input[type="password"]').first.fill("testpass123")
        page.locator('button:has-text("Войти")').first.click()
        page.wait_for_timeout(2000)

    print(f"After login: {page.url}")

    # Go to workspaces and create new
    if "/workspaces" not in page.url and "/workspace/" not in page.url:
        goto_with_retry(page, f"{BASE_URL}/workspaces")
        page.wait_for_timeout(2000)

    new_btn = page.locator('button:has-text("Новый"), button:has-text("Создать"), a:has-text("Новый")')
    if new_btn.count() > 0:
        new_btn.first.click()
        page.wait_for_timeout(3000)

    print(f"Workspace: {page.url}")

    # Select lab1_university from the scenario select
    scenario_select = page.locator('select.rounded-lg')
    if scenario_select.count() > 0:
        scenario_select.first.select_option("lab1_university")
        page.wait_for_timeout(500)
        print("Selected lab1_university")

    # Click Load button
    load_btn = page.locator('button:has-text("Загрузить")')
    if load_btn.count() > 0:
        load_btn.first.click()
        page.wait_for_timeout(3000)
        print("Clicked Load")

    # Click help button
    help_btn = page.locator('button:has-text("?")')
    if help_btn.count() > 0:
        help_btn.first.click()
        page.wait_for_timeout(1000)
        print("Clicked help button")

    page.screenshot(path="/tmp/help_panel_scenario.png", full_page=True)

    # Verify task description
    task_heading = page.locator('text=Лабораторная работа 1')
    if task_heading.count() > 0:
        print("SUCCESS: Task description for lab1_university is visible!")
    else:
        print("FAIL: Task description heading not found")
        panel = page.locator('.fixed')
        if panel.count() > 0:
            print(f"Panel text: {panel.inner_text()[:300]}")

    browser.close()
    print("Done!")
