"""E2E test for the Transition Panel (переходные/устойчивые режимы).

Setup is done via the API (register/login, blank workspace, tiny staged network,
two transition rules A->B and B->C). The browser then opens the workspace, runs
the transitions from the UI and verifies the resulting trace and stable mode.

Run (with dev servers up on :3000 and :8000):
    python3 tests/e2e_transition.py
"""
import json
import sys
import traceback
import urllib.request
import urllib.error

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
API_URL = "http://127.0.0.1:8000"

USER = "testuser_transition"
PASS = "testpass123"


def api(path, payload=None, token=None, method=None):
    url = f"{API_URL}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"{path} -> {e.code}: {body}")


def setup_via_api():
    """Create user, blank workspace, network and transition rules. Returns (token, sid)."""
    try:
        api("/api/auth/register", {"username": USER, "password": PASS})
    except RuntimeError:
        pass  # already exists
    tok = api("/api/auth/login", {"username": USER, "password": PASS})["access_token"]

    load = api("/api/session/load", {"scenario": "", "mode": None, "derive": True, "name": "e2e-transition"}, token=tok)
    sid = load["session_id"]

    for cid, label in (("obj", "Объект"), ("a", "A"), ("b", "B"), ("c", "C")):
        api("/api/session/add_concept", {"session_id": sid, "id": cid, "label": label, "tags": []}, token=tok)
    api("/api/session/add_predicate", {"session_id": sid, "name": "at", "arity": 2}, token=tok)
    api("/api/session/add_fact", {"session_id": sid, "predicate": "at", "args": ["obj", "a"]}, token=tok)

    def guard(stage):
        return {
            "type": "FactAtom",
            "predicate": "at",
            "args": [{"kind": "concept", "id": "obj"}, {"kind": "concept", "id": stage}],
        }

    api(f"/api/workspaces/{sid}/transition/rules", {
        "name": "A->B",
        "guard": guard("a"),
        "effect": [
            {"op": "retract", "predicate": "at", "args": ["obj", "a"]},
            {"op": "add", "predicate": "at", "args": ["obj", "b"]},
        ],
        "priority": 0,
    }, token=tok)
    api(f"/api/workspaces/{sid}/transition/rules", {
        "name": "B->C",
        "guard": guard("b"),
        "effect": [
            {"op": "retract", "predicate": "at", "args": ["obj", "b"]},
            {"op": "add", "predicate": "at", "args": ["obj", "c"]},
        ],
        "priority": 0,
    }, token=tok)
    return tok, sid


def browser_login(page):
    page.goto(f"{BASE_URL}/register")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)
    inputs = page.locator("input")
    inputs.nth(0).fill(USER)
    inputs.nth(1).fill(PASS)
    page.locator("button[type='submit'], button:has-text('Регистр')").first.click()
    page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle")
    if "/register" in page.url:
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        inputs = page.locator("input")
        inputs.nth(0).fill(USER)
        inputs.nth(1).fill(PASS)
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_timeout(1500)
        page.wait_for_load_state("networkidle")
    assert "/login" not in page.url and "/register" not in page.url, "Login failed"


def run():
    results = []

    print("Setup via API...")
    token, sid = setup_via_api()
    print(f"  workspace: {sid}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        try:
            browser_login(page)
            results.append(("login", "PASS"))

            page.goto(f"{BASE_URL}/workspace/{sid}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)

            # Panel visible
            panel = page.locator("[data-testid='transition-panel']")
            assert panel.count() > 0, "Transition panel not found"
            assert page.locator("h3:has-text('Переходы')").count() > 0, "Panel heading missing"
            results.append(("panel-visible", "PASS"))

            # Rules listed
            assert page.locator("text=A->B").count() > 0, "Rule A->B not listed"
            assert page.locator("text=B->C").count() > 0, "Rule B->C not listed"
            results.append(("rules-listed", "PASS"))

            # Run transitions
            run_btn = page.locator("[data-testid='run-transition']")
            assert run_btn.count() > 0 and run_btn.first.is_enabled(), "Run button missing/disabled"
            run_btn.first.click()
            page.wait_for_timeout(2000)

            result_box = page.locator("[data-testid='transition-result']")
            assert result_box.count() > 0, "No transition result"
            final = page.locator("[data-testid='final-mode']")
            final_text = final.first.text_content() or ""
            print(f"  final mode: {final_text}")
            assert "Устойчивый режим" in final_text, f"Expected stable mode, got: {final_text}"
            assert "2" in final_text, f"Expected 2 steps to converge, got: {final_text}"
            results.append(("run-stable", "PASS"))

            # Step entries present and clickable (highlight)
            steps = page.locator("[data-testid='transition-result'] button")
            assert steps.count() >= 2, f"Expected >=2 step entries, got {steps.count()}"
            steps.first.click()
            page.wait_for_timeout(500)
            results.append(("steps-listed", "PASS"))

            page.screenshot(path="/tmp/e2e_transition.png")
        except Exception as e:
            page.screenshot(path="/tmp/e2e_transition_fail.png")
            print(f"  FAIL: {e}")
            traceback.print_exc()
            results.append(("error", f"FAIL: {e}"))
        finally:
            if console_errors:
                print("Browser console errors:")
                for e in console_errors[:10]:
                    print(f"  {e}")
            browser.close()

    print("\n" + "=" * 50)
    passed = sum(1 for _, r in results if r == "PASS")
    failed = sum(1 for _, r in results if r != "PASS")
    for name, r in results:
        print(f"  {name}: {r}")
    print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
