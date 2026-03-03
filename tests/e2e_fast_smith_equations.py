"""E2E: Verify fast_smith scenario shows 3 equations in the UI.

Requires: API (localhost:8000) and Web (localhost:3000) servers running.
"""
from __future__ import annotations

import re
import random

from conftest import BASE_URL


def goto_with_retry(page, url, retries=3, delay=3000):
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            page.wait_for_timeout(delay)


def test_fast_smith_equations(page):
    # Register
    username = f"tester{random.randint(10000, 99999)}"
    goto_with_retry(page, f"{BASE_URL}/register")
    page.locator('input[type="text"]').first.fill(username)
    page.locator('input[type="password"]').first.fill("test1234")
    page.locator('button[type="submit"]').first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # Select fast_smith from scenario dropdown and create workspace
    select = page.locator("select").first
    select.select_option("fast_smith")
    page.wait_for_timeout(500)
    page.locator('button:has-text("Создать")').first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    body_text = page.inner_text("body")

    # Verify equations panel shows equations
    assert "Уравнения" in body_text, "Equations section not found"
    assert "Нет уравнений" not in body_text, "Shows 'no equations' when there should be 3"

    # Verify stats show 3 equations
    eq_matches = re.findall(r'(\d+)\nУравнений', body_text)
    assert eq_matches, "No equation count in stats"
    assert eq_matches[0] == "3", f"Expected 3 equations, got {eq_matches[0]}"

    # Verify actual equations are displayed
    assert "g ∘ h" in body_text, "Equation j = g ∘ h not found"
    assert "not-g ∘ h" in body_text, "Equation s = not-g ∘ h not found"
    assert "r ∘ sf" in body_text, "Equation jf = r ∘ sf not found"

    print("All fast_smith equation checks passed!")


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Warmup
        warmup = browser.new_page()
        warmup.goto(BASE_URL)
        warmup.wait_for_load_state("networkidle")
        warmup.wait_for_timeout(2000)
        warmup.close()

        pg = browser.new_page()
        test_fast_smith_equations(pg)
        browser.close()
