"""E2E test: load lab1_university scenario, verify graph and help panel.

Run with:
  python3 -m pytest tests/e2e_lab1_university.py -x
"""
from __future__ import annotations

import random

from conftest import BASE_URL, goto_with_retry


def test_register(page):
    """Register a fresh user for this test module."""
    goto_with_retry(page, f"{BASE_URL}/register")
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


def test_create_lab1_workspace(page):
    """Select lab1_university scenario and create workspace."""
    select = page.locator("select")
    if select.count() > 0:
        select.first.select_option("lab1_university")
        page.wait_for_timeout(500)
    page.locator("button:has-text('Создать')").first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)


def test_concepts_in_graph(page):
    """Verify expected concepts are visible in the graph."""
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
        assert cid in body or label in body, f"Concept missing: {cid} / {label}"


def test_forcing_results(page):
    """Verify forcing results show ok=True and TriBool.TRUE."""
    body = page.text_content("body") or ""
    assert "ok=True" in body or "ok: true" in body.lower(), "check result not ok=True"
    assert "TriBool.TRUE" in body, "forces not TriBool.TRUE"


def test_variables_panel(page):
    """Verify variables panel shows variable names."""
    body = page.text_content("body") or ""
    assert "course" in body, "Variable 'course' missing from panel"
    assert "student" in body, "Variable 'student' missing from panel"
    assert "teacher" in body, "Variable 'teacher' missing from panel"


def test_help_panel_content(page):
    """Open help panel and verify lab1 content."""
    help_btn = page.locator(
        "a:has-text('?'), button:has-text('?'), [title*='Справка'], [title*='справк']"
    )
    if help_btn.count() > 0:
        help_btn.first.click()
        page.wait_for_timeout(1000)

    body = page.text_content("body") or ""
    help_keywords = [
        "Лабораторная работа 1",
        "3.1",
        "3.2",
        "5–7 концептов",
        "Критерии оценки",
    ]
    for kw in help_keywords:
        assert kw in body, f"Help text missing: '{kw}'"
