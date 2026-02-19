"""Shared fixtures for e2e tests.

These tests were designed to run sequentially within each module,
sharing a single page/browser context (register -> login -> create workspace -> ...).
We override pytest-playwright's default function-scoped page with a module-scoped
one so that state persists across all test functions in a file.
"""
import pytest


BASE_URL = "http://localhost:3000"


@pytest.fixture(scope="module")
def _browser(browser_type, browser_type_launch_args):
    """Module-scoped browser instance."""
    browser = browser_type.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture(scope="module")
def context(_browser):
    """Module-scoped browser context so all tests in a module share state."""
    ctx = _browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture(scope="module")
def page(context):
    """Module-scoped page so tests in a module share the same page instance.

    This matches the original design where each test file runs its tests
    sequentially on a single page (register -> login -> workspace -> test).
    """
    pg = context.new_page()

    # Warmup: ensure the dev server is reachable
    for url in [BASE_URL, f"{BASE_URL}/login", f"{BASE_URL}/register"]:
        for attempt in range(3):
            pg.goto(url)
            pg.wait_for_load_state("networkidle")
            if pg.locator("text=This page could not be found").count() == 0:
                break
            pg.wait_for_timeout(3000)

    yield pg
    pg.close()
