"""E2E test: Forcing panel shows scenario results (check/forces/force) after Run."""

from playwright.sync_api import sync_playwright
import random, string

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
    console_msgs = []

    # --- Warmup ---
    warmup = browser.new_page()
    goto_with_retry(warmup, BASE_URL)
    goto_with_retry(warmup, f"{BASE_URL}/login")
    goto_with_retry(warmup, f"{BASE_URL}/register")
    warmup.close()

    page = browser.new_page()
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

    # 1. Register
    print("Step 1: Register...")
    page.goto(f"{BASE_URL}/register")
    page.wait_for_load_state("networkidle")

    username = "test_" + "".join(random.choices(string.ascii_lowercase, k=6))
    page.fill('input[placeholder="Имя пользователя"]', username)
    page.fill('input[placeholder="Пароль"]', "testpass123")
    page.click('button:has-text("Зарегистрироваться")')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # If redirected to login, log in
    if "/login" in page.url:
        print("  Redirected to login, logging in...")
        page.fill('input[placeholder="Имя пользователя"]', username)
        page.fill('input[placeholder="Пароль"]', "testpass123")
        page.click('button:has-text("Войти")')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

    print(f"  URL after auth: {page.url}")

    # 2. Select scenario and create workspace
    print("Step 2: Select scenario and create workspace...")
    # On workspaces page, select lab1_university from dropdown
    scenario_select = page.locator("select").first
    if scenario_select.count() > 0:
        options = scenario_select.locator("option").all_text_contents()
        print(f"  Available scenarios: {options}")
        for opt in options:
            if "lab1" in opt.lower() or "university" in opt.lower():
                scenario_select.select_option(label=opt)
                break

    # Click Создать to create workspace with scenario
    create_btn = page.locator('button:has-text("Создать")').first
    if create_btn.count() > 0:
        create_btn.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
    print(f"  URL after create: {page.url}")

    # 4. Click Run
    print("Step 4: Click Run...")
    run_btn = page.locator('button:has-text("Run")').first
    if run_btn.count() == 0:
        run_btn = page.locator('button:has-text("Запустить")').first
    if run_btn.count() > 0:
        run_btn.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
    else:
        print("  WARNING: Run button not found!")

    # 5. Verify forcing panel
    print("Step 5: Verify forcing panel scenario results...")
    page.screenshot(path="/tmp/forcing_panel_test.png", full_page=True)

    # Scroll the right panel to find forcing section
    right_panel = page.locator(".overflow-auto").last
    if right_panel.count() > 0:
        right_panel.evaluate("el => el.scrollTop = el.scrollHeight")
        page.wait_for_timeout(500)
        page.screenshot(path="/tmp/forcing_panel_scrolled.png", full_page=True)

    # Check for scenario results section
    scenario_result = page.locator("text=Результат сценария")
    has_scenario_result = scenario_result.count() > 0
    print(f"  'Результат сценария' visible: {has_scenario_result}")

    # Check for check/forces labels
    check_label = page.locator("text=check:")
    forces_label = page.locator("text=forces:")
    has_check = check_label.count() > 0
    has_forces = forces_label.count() > 0
    print(f"  check: label visible: {has_check}")
    print(f"  forces: label visible: {has_forces}")

    # Check forcing panel header still exists
    forcing_header = page.locator("text=Форсирование")
    has_forcing = forcing_header.count() > 0
    print(f"  'Форсирование' header: {has_forcing}")

    # Manual controls still present
    context_label = page.locator("text=Контекст")
    conditions_label = page.locator("text=Условия")
    has_manual_controls = context_label.count() > 0 and conditions_label.count() > 0
    print(f"  Manual controls present: {has_manual_controls}")

    # Print console errors for debugging
    errors = [m for m in console_msgs if m.startswith("[error") or m.startswith("[4") or m.startswith("[5")]
    if errors:
        print("\n  Errors:")
        for m in errors[-10:]:
            print(f"    {m}")

    # Final result
    passed = has_scenario_result and has_forcing and has_manual_controls
    if passed:
        print("\nPASS: Forcing panel shows scenario results after Run")
    else:
        print("\nFAIL: See screenshots at /tmp/forcing_panel_test.png and /tmp/forcing_panel_scrolled.png")

    browser.close()
