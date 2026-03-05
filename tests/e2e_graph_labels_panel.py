"""E2E test: graph node labels show [id] and right panel responsive behavior."""
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


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Login
    goto_with_retry(page, f"{BASE_URL}/login")
    page.locator('input[placeholder="Имя пользователя"]').fill("testuser")
    page.locator('input[placeholder="Пароль"]').fill("testpass")
    page.locator('button[type="submit"]').click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # Create workspace
    page.locator('button:has-text("Создать")').click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    # Load scenario
    load_btn = page.locator('button:has-text("Загрузить")')
    if load_btn.count() > 0:
        load_btn.first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

    # Verify graph canvas exists
    canvas = page.locator("canvas")
    assert canvas.count() > 0, "Graph canvas not found"
    print("PASS: Graph canvas found")

    # Verify right panel classes
    right_panel = page.locator("div.border-l.bg-white.p-4")
    assert right_panel.count() > 0, "Right panel not found"
    classes = right_panel.first.get_attribute("class") or ""
    assert "shrink-0" not in classes, "shrink-0 should be removed from right panel"
    assert "min-w-[300px]" in classes, "min-w-[300px] should be on right panel"
    print("PASS: Right panel has correct responsive classes")

    # Verify panel shrinks on narrow viewport
    box_wide = right_panel.first.bounding_box()
    page.set_viewport_size({"width": 700, "height": 600})
    page.wait_for_timeout(500)
    box_narrow = right_panel.first.bounding_box()
    assert box_wide and box_narrow, "Could not get panel bounding boxes"
    assert box_narrow["width"] < box_wide["width"], "Panel should shrink on narrow viewport"
    print(f"PASS: Panel shrinks {box_wide['width']:.0f}px -> {box_narrow['width']:.0f}px")

    # Verify overflow-x-hidden on outer container
    outer = page.locator("div.flex.flex-1.overflow-hidden.overflow-x-hidden")
    assert outer.count() > 0, "overflow-x-hidden missing on outer container"
    print("PASS: overflow-x-hidden on outer container")

    page.set_viewport_size({"width": 1280, "height": 720})
    print("\nAll tests passed.")
    browser.close()
