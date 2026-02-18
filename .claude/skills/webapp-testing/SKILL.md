---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Prerequisites

Before writing any Playwright test, ensure the environment is ready:

1. **Check Playwright is installed**: Run `python3 -c "from playwright.sync_api import sync_playwright; print('OK')"`. If it fails, install: `pip3 install playwright && python3 -m playwright install chromium`
2. **Check servers are accessible**: Use `curl -sI http://localhost:<port>` to verify each server responds before running tests. A TCP port being open does NOT mean the app is ready (Next.js may return 500 while compiling).

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Starting Servers

### Preferred approach: start servers manually in background

For monorepo projects, start each server as a **separate background Bash command** with explicit `cd` to the correct directory. This avoids working directory issues with `with_server.py`.

```bash
# Terminal 1 (background): API server
source venv/bin/activate && cd /absolute/path/to/apps/api && PYTHONPATH=../../src:src python3 -m uvicorn app:app --host 127.0.0.1 --port 8000 &

# Terminal 2 (background): Web server
cd /absolute/path/to/apps/web && npm run dev &
```

Then verify servers are ready before running tests:
```bash
# Wait and verify — check HTTP response, not just port
sleep 5
curl -sI http://localhost:8000/some-endpoint  # Should return HTTP status
curl -sI http://localhost:3000/               # Should return 200
```

After tests complete, stop servers:
```bash
pkill -f "uvicorn" 2>/dev/null; pkill -f "next dev" 2>/dev/null
```

### Alternative: using with_server.py

Run `--help` first, then use the helper. **CRITICAL: always use absolute paths with `cd` in `--server` commands** — the script runs all commands from its own working directory.

```bash
python scripts/with_server.py \
  --server "cd /absolute/path/to/backend && python server.py" --port 3000 \
  --server "cd /absolute/path/to/frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

**Known limitation**: `with_server.py` considers a port ready as soon as TCP connects. For Next.js dev servers, the port opens before compilation finishes — pages will return 500 until ready. Use the warmup pattern below.

## Writing Playwright Scripts

Include only Playwright logic (servers are managed separately):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Next.js / SPA Warmup Pattern

Next.js dev server compiles pages on first request. The first visit may return 404 or 500 while compilation happens. Always warm up pages before testing:

```python
def goto_with_retry(page, url, retries=3, delay=3000):
    """Navigate to URL with retries for Next.js on-demand compilation."""
    for attempt in range(retries):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        # Check for common not-ready indicators
        if page.locator("text=This page could not be found").count() == 0:
            return
        if attempt < retries - 1:
            print(f"  Page not ready (attempt {attempt+1}), retrying...")
            page.wait_for_timeout(delay)

# Warm up key pages before running tests
warmup = browser.new_page()
warmup.goto(BASE_URL)
warmup.wait_for_load_state("networkidle")
warmup.wait_for_timeout(2000)
goto_with_retry(warmup, f"{BASE_URL}/login")
goto_with_retry(warmup, f"{BASE_URL}/register")
warmup.close()
```

## Diagnostic Pattern: Capturing Console & Network Errors

When forms or API calls silently fail, capture browser console and network activity:

```python
page = browser.new_page()
console_msgs = []
page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
page.on("requestfailed", lambda req: console_msgs.append(f"[FAILED] {req.method} {req.url} -> {req.failure}"))
page.on("response", lambda res: console_msgs.append(f"[{res.status}] {res.url}") if res.status >= 400 else None)

# ... perform actions ...

# Print diagnostics
for m in console_msgs:
    print(f"  {m}")
```

## Common Pitfalls

- **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps — **Do** wait for `page.wait_for_load_state('networkidle')` first
- **Don't** mix `npm run build` and `npm run dev` without cleaning `.next` — production build creates artifacts incompatible with dev server. Run `rm -rf .next` before switching modes
- **Don't** assume port open = server ready — Next.js opens port before compilation. Use warmup pattern or curl to verify HTTP 200
- **Don't** use relative paths in `with_server.py` `--server` commands — always use `cd /absolute/path && command`

## Best Practices

- **Start servers manually in background** for monorepo projects instead of using `with_server.py` — gives better control over working directories and error visibility
- **Always capture console logs** when debugging form submissions or API interactions — browser console often reveals the root cause (CORS, 500, network errors)
- **Write diagnostic scripts first** when testing unfamiliar apps — a quick script that captures console/network state saves many debugging cycles
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`
- Wrap each test case in try/except with screenshots — failed tests should always leave a screenshot for debugging

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation