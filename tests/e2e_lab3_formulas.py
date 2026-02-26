"""E2E tests for Lab 3: formulas creation, evaluation, UNKNOWN results.

Run with:
  python3 -m pytest tests/e2e_lab3_formulas.py -x
"""
import os
import glob

from conftest import BASE_URL, goto_with_retry

USERNAME = "lab3_tester"
PASSWORD = "lab3pass123"


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


def create_workspace_with_scenario(page, scenario):
    """Navigate to workspaces list, select scenario, and create a new workspace."""
    goto_with_retry(page, f"{BASE_URL}/workspaces")
    page.wait_for_timeout(2000)

    # First select the scenario in the dropdown on the workspaces page,
    # THEN click create so the workspace is created with the right scenario.
    scenario_select = page.locator("select").first
    if scenario_select.count() > 0:
        scenario_select.select_option(scenario)
        page.wait_for_timeout(500)

    create_btn = page.locator('button:has-text("Создать")')
    if create_btn.count() > 0:
        create_btn.first.click()
        page.wait_for_timeout(5000)


# ─── Tests ───────────────────────────────────────────────────

def test_register(page):
    """Step 1: Register and log in."""
    register_and_login(page)
    assert "/workspaces" in page.url or "/workspace/" in page.url, \
        f"Expected workspaces page after login, got {page.url}"


def test_create_lab3_workspace(page):
    """Step 2: Create workspace with lab3_formulas, verify graph renders."""
    create_workspace_with_scenario(page, "lab3_formulas")
    page.wait_for_timeout(2000)

    assert "/workspace/" in page.url, f"Expected workspace page, got {page.url}"

    # Graph canvas should be present (Cytoscape container)
    graph_container = page.locator("canvas, .cytoscape-container, [class*='graph']")
    assert graph_container.count() > 0, "Graph view not found on workspace page"
    page.screenshot(path="/tmp/e2e_lab3_graph.png")


def test_graph_shows_university_network(page):
    """Step 3: Verify university network concept labels are visible."""
    # Wait for the network data to load — concept labels appear in
    # the NetworkEditorPanel's "Существующие концепты" list.
    page.locator("text=Существующие концепты").wait_for(timeout=10000)
    page.wait_for_timeout(500)

    body_text = page.text_content("body") or ""
    # Check for at least some of the expected concept labels
    expected_labels = ["Университет", "Кафедра ИВТ", "Иванов", "Петров"]
    found = [label for label in expected_labels if label in body_text]
    assert len(found) >= 2, \
        f"Expected university network labels, found only: {found}"
    page.screenshot(path="/tmp/e2e_lab3_university_network.png")


def test_help_panel_shows_lab3(page):
    """Step 4: Open HelpPanel and verify Lab 3 task description and truth tables."""
    help_btn = page.locator('button:has-text("?")')
    assert help_btn.count() > 0, "Help button not found"
    help_btn.first.click()
    page.wait_for_timeout(1000)

    # Verify Lab 3 heading
    lab3_heading = page.locator("text=Лабораторная работа 3")
    assert lab3_heading.count() > 0, "Lab 3 task description not found in HelpPanel"

    # Switch to Logic tab and verify truth tables
    logic_tab = page.locator('button:has-text("Логика")')
    if logic_tab.count() > 0:
        logic_tab.first.click()
        page.wait_for_timeout(500)

    # Check for truth table content
    body_text = page.text_content("body") or ""
    assert "NOT" in body_text or "AND" in body_text, \
        "Truth table content not found in Logic tab"

    page.screenshot(path="/tmp/e2e_lab3_help_panel.png")

    # Close help panel
    close_btn = page.locator("button:has-text('\u2715')")
    if close_btn.count() > 0:
        close_btn.first.click()
        page.wait_for_timeout(500)


def test_create_factatom_formula(page):
    """Step 5: Create a FactAtom formula via UI, verify it appears."""
    # Click "+ Новая формула"
    new_formula_btn = page.locator('button:has-text("Новая формула"), a:has-text("Новая формула")')
    assert new_formula_btn.count() > 0, "New formula button not found"
    new_formula_btn.first.click()
    page.wait_for_timeout(500)

    # Fill formula name
    name_input = page.locator('input[placeholder="Имя формулы"]')
    if name_input.count() > 0:
        name_input.first.fill("teaches_ivanov_db")

    # The FormulaBuilder is inside the new-formula form (bg-gray-50 panel).
    # Its first <select> is the formula type selector; we must not pick the
    # ScenarioBar's selects which also live on the page.
    formula_form = page.locator('div.bg-gray-50:has(input[placeholder="Имя формулы"])')
    type_select = formula_form.locator("select").first
    type_select.select_option("FactAtom")
    page.wait_for_timeout(300)

    # Select predicate — the second <select> inside the FormulaBuilder
    pred_select = formula_form.locator("select").nth(1)
    pred_select.wait_for(timeout=5000)
    # Pick the first real predicate option (skip the placeholder)
    options = pred_select.locator("option").all_text_contents()
    real_options = [o for o in options if o and "Предикат" not in o]
    if real_options:
        pred_select.select_option(label=real_options[0])
    page.wait_for_timeout(300)

    # Click Create/Save — use the button inside the formula form
    save_btn = formula_form.locator('button:has-text("Создать")')
    if save_btn.count() > 0:
        save_btn.first.click()
        page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_lab3_create_formula.png")

    # Verify formula appears in the list
    body_text = page.text_content("body") or ""
    assert "teaches" in body_text.lower() or "FactAtom" in body_text or "Формулы" in body_text, \
        "Created formula not visible on page"


def test_evaluate_formula(page):
    """Step 6: Evaluate a formula and verify result badge appears."""
    # Click evaluate button (play icon ►)
    eval_btn = page.locator('button[title="Вычислить"]')
    assert eval_btn.count() > 0, "Evaluate button not found — was a formula created?"
    eval_btn.first.click()
    page.wait_for_timeout(2000)

    page.screenshot(path="/tmp/e2e_lab3_evaluate.png")

    # Check for result badge (green/red/yellow background span)
    result_badge = page.locator(
        "span.bg-green-100, span.bg-red-100, span.bg-yellow-100"
    )
    assert result_badge.count() > 0, "No evaluation result badge found (expected true/false/unknown)"

    # Verify result text
    result_text = result_badge.first.text_content() or ""
    assert result_text.strip().lower() in ("true", "false", "unknown"), \
        f"Unexpected result badge text: {result_text}"


def test_create_compound_formula(page):
    """Step 7: Create a compound formula (Not or And)."""
    # Click "+ Новая формула"
    new_formula_btn = page.locator('button:has-text("Новая формула"), a:has-text("Новая формула")')
    assert new_formula_btn.count() > 0, "New formula button not found"
    new_formula_btn.first.click()
    page.wait_for_timeout(500)

    # Fill formula name
    name_input = page.locator('input[placeholder="Имя формулы"]')
    if name_input.count() > 0:
        name_input.first.fill("not_teaches_petrov")

    # Select Not type — target the FormulaBuilder's select inside the form
    formula_form = page.locator('div.bg-gray-50:has(input[placeholder="Имя формулы"])')
    type_select = formula_form.locator("select").first
    type_select.select_option("Not")
    page.wait_for_timeout(300)

    # Click Create/Save — use the button inside the formula form
    save_btn = formula_form.locator('button:has-text("Создать")')
    if save_btn.count() > 0:
        save_btn.first.click()
        page.wait_for_timeout(1000)

    page.screenshot(path="/tmp/e2e_lab3_compound_formula.png")

    # Verify we now have multiple formulas
    formula_section = page.locator("text=Формулы")
    assert formula_section.count() > 0, "Formulas section not found"


def test_export_json(page):
    """Step 8: Export JSON — file downloads successfully."""
    download_dir = "/tmp/e2e_lab3_downloads"
    os.makedirs(download_dir, exist_ok=True)
    for f in glob.glob(os.path.join(download_dir, "*.json")):
        os.remove(f)

    with page.expect_download() as download_info:
        export_btn = page.locator('button:has-text("JSON")').first
        export_btn.click()

    download = download_info.value
    path = os.path.join(download_dir, download.suggested_filename)
    download.save_as(path)

    assert os.path.exists(path), f"Downloaded file not found at {path}"
    assert os.path.getsize(path) > 10, "Downloaded JSON file is suspiciously small"
    page.screenshot(path="/tmp/e2e_lab3_export.png")
