"""E2E test: HelpPanel shows scenario-specific task description.

Run with:
  python3 -m pytest tests/e2e_help_panel_scenario.py -x
"""
from conftest import BASE_URL, goto_with_retry


def test_login(page):
    """Log in (or register) a test user."""
    goto_with_retry(page, BASE_URL)
    page.wait_for_timeout(2000)

    if "/login" in page.url or page.locator("text=Войти").count() > 0:
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        page.locator('input[type="text"]').first.fill("testuser2")
        page.locator('input[type="password"]').first.fill("testpass123")
        page.locator('button:has-text("Войти")').first.click()
        page.wait_for_timeout(2000)


def test_create_workspace_with_scenario(page):
    """Navigate to workspaces, create one with lab1_university scenario."""
    if "/workspaces" not in page.url and "/workspace/" not in page.url:
        goto_with_retry(page, f"{BASE_URL}/workspaces")
        page.wait_for_timeout(2000)

    new_btn = page.locator(
        'button:has-text("Новый"), button:has-text("Создать"), a:has-text("Новый")'
    )
    if new_btn.count() > 0:
        new_btn.first.click()
        page.wait_for_timeout(3000)

    scenario_select = page.locator("select.rounded-lg")
    if scenario_select.count() > 0:
        scenario_select.first.select_option("lab1_university")
        page.wait_for_timeout(500)

    load_btn = page.locator('button:has-text("Загрузить")')
    if load_btn.count() > 0:
        load_btn.first.click()
        page.wait_for_timeout(3000)


def test_help_panel_shows_task_description(page):
    """Open help panel and verify scenario-specific task description."""
    help_btn = page.locator('button:has-text("?")')
    if help_btn.count() > 0:
        help_btn.first.click()
        page.wait_for_timeout(1000)

    task_heading = page.locator("text=Лабораторная работа 1")
    assert task_heading.count() > 0, "Task description for lab1_university not visible"
