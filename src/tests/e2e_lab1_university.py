"""E2E test: load lab1_university scenario, verify graph and help panel.

Prerequisites:
  - API server running on localhost:8000
  - Web server running on localhost:3000
  - Playwright installed: pip3 install playwright && python3 -m playwright install chromium

Usage:
  python3 src/tests/e2e_lab1_university.py
"""
from __future__ import annotations

import random
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


def main() -> int:
    errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        # Register
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        username = f"testlab1_{random.randint(10000, 99999)}"
        name_input = page.locator("input[name='name'], input[placeholder*='мя']")
        if name_input.count() > 0:
            name_input.first.fill(username)
        email_input = page.locator("input[name='email'], input[type='email']")
        if email_input.count() > 0:
            email_input.first.fill(f"{username}@test.com")
        pw_input = page.locator("input[type='password']")
        if pw_input.count() > 0:
            pw_input.first.fill("Test1234!")
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Select lab1_university and create workspace
        select = page.locator("select")
        if select.count() > 0:
            select.first.select_option("lab1_university")
            page.wait_for_timeout(500)
        page.locator("button:has-text('Создать')").first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Verify concepts in graph
        body = page.text_content("body") or ""
        expected_concepts = [
            ("university", "Университет"),
            ("dept_cs", "Кафедра ИВТ"),
            ("course_db", "Базы данных"),
            ("course_ai", "Искусственный интеллект"),
            ("ivanov", "Иванов"),
            ("petrov", "Петров"),
        ]
        for cid, label in expected_concepts:
            if cid not in body and label not in body:
                errors.append(f"Concept missing: {cid} / {label}")

        # Verify forcing results
        if "ok=True" not in body and "ok: true" not in body.lower():
            errors.append("check result not ok=True")
        if "TriBool.TRUE" not in body:
            errors.append("forces not TriBool.TRUE")

        # Verify variables panel
        if "course" not in body or "student" not in body or "teacher" not in body:
            errors.append("Variables panel missing variable names")

        # Open help panel and verify content
        help_btn = page.locator("a:has-text('?'), button:has-text('?'), [title*='Справка'], [title*='справк']")
        if help_btn.count() > 0:
            help_btn.first.click()
            page.wait_for_timeout(1000)

        body_after = page.text_content("body") or ""
        help_keywords = [
            "Лабораторная работа 1",
            "3.1",
            "3.2",
            "5–7 концептов",
            "Критерии оценки",
        ]
        for kw in help_keywords:
            if kw not in body_after:
                errors.append(f"Help text missing: '{kw}'")

        browser.close()

    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK: lab1_university scenario loaded and verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
