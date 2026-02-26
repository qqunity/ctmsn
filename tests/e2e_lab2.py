"""E2E tests for Lab 2: loading scenarios, NetworkStatsPanel, HelpPanel, mode switching, JSON export.

Run with:
  python3 -m pytest tests/e2e_lab2.py -x
"""
import os
import glob

from conftest import BASE_URL, goto_with_retry

USERNAME = "lab2_tester"
PASSWORD = "lab2pass123"


# ─── Helpers ─────────────────────────────────────────────────

def register_and_login(page):
    """Register a new user (ignore if exists) then log in."""
    goto_with_retry(page, f"{BASE_URL}/register")
    page.wait_for_timeout(1000)

    if page.locator('input[type="text"]').count() > 0:
        page.locator('input[type="text"]').first.fill(USERNAME)
        page.locator('input[type="password"]').first.fill(PASSWORD)
        page.locator('button:has-text("Регистрация"), button:has-text("Зарегистрироваться")').first.click()
        page.wait_for_timeout(2000)

    if "/login" in page.url or page.locator("text=Войти").count() > 0:
        goto_with_retry(page, f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        page.locator('input[type="text"]').first.fill(USERNAME)
        page.locator('input[type="password"]').first.fill(PASSWORD)
        page.locator('button:has-text("Войти")').first.click()
        page.wait_for_timeout(2000)


def create_workspace_with_scenario(page, scenario, mode=None):
    """Navigate to workspaces list and create a new workspace with the given scenario."""
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
        scenario_select.first.select_option(scenario)
        page.wait_for_timeout(500)

    if mode:
        mode_select = page.locator("select.rounded-lg").nth(1)
        if mode_select.count() > 0:
            mode_select.select_option(mode)
            page.wait_for_timeout(500)

    load_btn = page.locator('button:has-text("Загрузить")')
    if load_btn.count() > 0:
        load_btn.first.click()
        page.wait_for_timeout(3000)


# ─── Tests ───────────────────────────────────────────────────

def test_register_and_login(page):
    """Step 1: Register and log in."""
    register_and_login(page)
    assert "/workspaces" in page.url or "/workspace/" in page.url, \
        f"Expected workspaces page after login, got {page.url}"


def test_create_workspace_fast_smith(page):
    """Step 2: Create workspace with fast_smith, verify graph renders."""
    create_workspace_with_scenario(page, "fast_smith")
    page.wait_for_timeout(2000)

    assert "/workspace/" in page.url, f"Expected workspace page, got {page.url}"

    # Graph canvas should be present (Cytoscape container)
    graph_container = page.locator("canvas, .cytoscape-container, [class*='graph']")
    assert graph_container.count() > 0, "Graph view not found on workspace page"
    page.screenshot(path="/tmp/e2e_lab2_fast_smith_graph.png")


def test_help_panel_shows_lab2(page):
    """Step 3: Open HelpPanel and verify it shows Lab 2 task description."""
    help_btn = page.locator('button:has-text("?")')
    assert help_btn.count() > 0, "Help button not found"
    help_btn.first.click()
    page.wait_for_timeout(1000)

    lab2_heading = page.locator("text=Лабораторная работа 2")
    assert lab2_heading.count() > 0, "Lab 2 task description not found in HelpPanel"

    # Close help panel
    close_btn = page.locator("button:has-text('\u2715')")
    if close_btn.count() > 0:
        close_btn.first.click()
        page.wait_for_timeout(500)

    page.screenshot(path="/tmp/e2e_lab2_help_panel.png")


def test_network_stats_panel_visible(page):
    """Step 4: NetworkStatsPanel is visible with non-zero values."""
    stats_heading = page.locator("text=Статистика сети")
    assert stats_heading.count() > 0, "NetworkStatsPanel heading not found"

    # Check that at least one stat cell shows a non-zero number (not "—")
    stat_cells = page.locator(".grid .rounded-lg .text-lg")
    assert stat_cells.count() >= 4, f"Expected 4 stat cells, found {stat_cells.count()}"

    has_nonzero = False
    for i in range(stat_cells.count()):
        text = stat_cells.nth(i).text_content() or ""
        if text.strip() not in ("", "\u2014", "0"):
            has_nonzero = True
            break
    assert has_nonzero, "All stat cells are zero or empty"
    page.screenshot(path="/tmp/e2e_lab2_stats_panel.png")


def test_equations_panel_has_equations(page):
    """Step 5: EquationsPanel contains equations (using spawn scenario which has comp2/compN)."""
    # fast_smith has no equations; load spawn which has comp2/compN predicates
    create_workspace_with_scenario(page, "spawn")
    page.wait_for_timeout(2000)

    eq_heading = page.locator("text=Уравнения")
    assert eq_heading.count() > 0, "Equations panel heading not found"

    # There should be at least one equation row
    eq_items = page.locator(".divide-y > li, .divide-y > div, .divide-y > button")
    assert eq_items.count() > 0, "No equations found in EquationsPanel"
    page.screenshot(path="/tmp/e2e_lab2_equations.png")


def test_time_process_mode_switch(page):
    """Step 6: Load time_process with sun, then prereq — graphs differ."""
    # Load time_process with sun mode
    create_workspace_with_scenario(page, "time_process", mode="sun")
    page.wait_for_timeout(2000)

    # Capture stats for sun mode
    stat_cells_sun = page.locator(".grid .rounded-lg .text-lg")
    sun_values = []
    for i in range(stat_cells_sun.count()):
        sun_values.append((stat_cells_sun.nth(i).text_content() or "").strip())
    page.screenshot(path="/tmp/e2e_lab2_time_process_sun.png")

    # Switch to prereq mode via scenario bar
    mode_select = page.locator("select.rounded-lg").nth(1)
    if mode_select.count() > 0:
        mode_select.select_option("prereq")
        page.wait_for_timeout(500)

    load_btn = page.locator('button:has-text("Загрузить")')
    if load_btn.count() > 0:
        load_btn.first.click()
        page.wait_for_timeout(3000)

    # Capture stats for prereq mode
    stat_cells_prereq = page.locator(".grid .rounded-lg .text-lg")
    prereq_values = []
    for i in range(stat_cells_prereq.count()):
        prereq_values.append((stat_cells_prereq.nth(i).text_content() or "").strip())
    page.screenshot(path="/tmp/e2e_lab2_time_process_prereq.png")

    # Graphs should differ (at least one stat value differs)
    assert sun_values != prereq_values, \
        f"sun and prereq modes should produce different stats, got same: {sun_values}"


def test_export_json(page):
    """Step 7: Export JSON — file downloads successfully."""
    # Clean up any previous downloads
    download_dir = "/tmp/e2e_lab2_downloads"
    os.makedirs(download_dir, exist_ok=True)
    for f in glob.glob(os.path.join(download_dir, "*.json")):
        os.remove(f)

    # Set up download handler
    with page.expect_download() as download_info:
        export_btn = page.locator('button:has-text("JSON")').first
        export_btn.click()

    download = download_info.value
    path = os.path.join(download_dir, download.suggested_filename)
    download.save_as(path)

    assert os.path.exists(path), f"Downloaded file not found at {path}"
    assert os.path.getsize(path) > 10, "Downloaded JSON file is suspiciously small"
    page.screenshot(path="/tmp/e2e_lab2_export.png")
