"""E2E test: verify existing facts are displayed in the Network Editor Fact tab."""
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


def test_register_and_login(page):
    goto_with_retry(page, f"{BASE_URL}/register")
    page.wait_for_timeout(1000)
    inputs = page.locator("input")
    inputs.nth(0).fill("testuser_facts")
    inputs.nth(1).fill("testpass123")
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")
    if "/register" in page.url or page.locator("text=уже существует").count() > 0:
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        inputs = page.locator("input")
        inputs.nth(0).fill("testuser_facts")
        inputs.nth(1).fill("testpass123")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")
    assert "/login" not in page.url and "/register" not in page.url, "Login failed"
    print("  Logged in OK")


def test_create_workspace_with_scenario(page):
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
        scenario_select.first.select_option("lab5_inheritance")
        page.wait_for_timeout(500)
    load_btn = page.locator('button:has-text("Загрузить")')
    if load_btn.count() > 0:
        load_btn.first.click()
        page.wait_for_timeout(3000)


def test_facts_displayed(page):
    """After loading lab5_inheritance, the Fact tab must show existing facts."""
    print("TEST: Existing facts displayed in Fact tab")
    fact_tab = page.locator("button:has-text('Fact')")
    assert fact_tab.count() > 0, "Fact tab button not found"
    fact_tab.first.click()
    page.wait_for_timeout(1000)

    existing_label = page.locator("text=Существующие факты:")
    assert existing_label.count() > 0, "'Существующие факты:' section not found"

    fact_items = page.locator(".max-h-40 div.flex")
    count = fact_items.count()
    print(f"  Found {count} facts")
    assert count > 0, "Facts section visible but no facts shown"

    # Verify some expected facts
    page_text = page.locator(".max-h-40").inner_text()
    for expected in ["isa(", "has_ability(", "instance_of("]:
        assert expected in page_text, f"Expected fact pattern '{expected}' not found"
        print(f"  Found pattern: {expected}")

    print("  PASS")


def main():
    failed = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        # Warmup
        warmup = browser.new_page()
        warmup.goto(BASE_URL)
        warmup.wait_for_load_state("networkidle")
        warmup.wait_for_timeout(2000)
        goto_with_retry(warmup, f"{BASE_URL}/login")
        goto_with_retry(warmup, f"{BASE_URL}/register")
        warmup.close()

        tests = [
            ("register_and_login", lambda: test_register_and_login(page)),
            ("create_workspace", lambda: test_create_workspace_with_scenario(page)),
            ("facts_displayed", lambda: test_facts_displayed(page)),
        ]
        for name, fn in tests:
            try:
                fn()
            except Exception as exc:
                print(f"  FAIL: {exc}")
                page.screenshot(path=f"/tmp/e2e_facts_{name}_fail.png")
                failed.append(name)

        browser.close()

    if failed:
        print(f"\nFailed tests: {failed}")
        sys.exit(1)
    print("\nAll tests passed!")


if __name__ == "__main__":
    main()
