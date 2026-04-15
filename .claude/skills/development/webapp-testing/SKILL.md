# Skill: Webapp Testing

Tests local web applications using Playwright for frontend verification, debugging, and screenshots.
Trigger: "test the webapp", "verify UI", "playwright test", "take screenshot", "check frontend"
Output artifact: Test results with screenshots (screenshot.png, failure.png)

---

# Webapp Testing

Tests local web applications using Playwright for frontend verification and debugging.

## When to Use

- Verifying that a UI feature works correctly
- Debugging why a button, form, or page interaction isn't working
- Taking screenshots to capture current UI state
- Writing automated tests for a web application
- Checking that a newly built feature renders correctly

## Setup

```bash
# Install Playwright if not present
pip install playwright --break-system-packages
playwright install chromium

# Or via npm
npm install -D playwright
npx playwright install chromium
```

## Quick Test Script

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("http://localhost:3000")

    # Take a screenshot
    page.screenshot(path="screenshot.png")

    # Check page title
    print(page.title())

    # Interact with elements
    page.click("button#submit")
    page.fill("input[name='email']", "test@example.com")

    browser.close()
```

## Common Testing Patterns

### Verify Element Exists
```python
assert page.locator("text=Welcome").is_visible()
assert page.locator("#dashboard").count() == 1
```

### Test Form Submission
```python
page.fill("input[name='username']", "testuser")
page.fill("input[name='password']", "password123")
page.click("button[type='submit']")
page.wait_for_url("**/dashboard")
assert page.locator("h1:text('Dashboard')").is_visible()
```

### Wait for Async Content
```python
# Wait for network to settle
page.wait_for_load_state("networkidle")

# Wait for a specific element
page.wait_for_selector(".data-table", timeout=5000)
```

### Check for Errors
```python
errors = []
page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
page.goto("http://localhost:3000")
if errors:
    print("Console errors:", errors)
```

## Screenshot Capture

```python
# Full page
page.screenshot(path="full-page.png", full_page=True)

# Specific element
page.locator(".chart-container").screenshot(path="chart.png")

# On failure
try:
    page.click("#non-existent")
except Exception as e:
    page.screenshot(path="failure.png")
    raise
```

## Playwright Test Format (for saved tests)

```python
# tests/test_homepage.py
import pytest
from playwright.sync_api import Page

def test_homepage_loads(page: Page):
    page.goto("http://localhost:3000")
    assert page.title() == "My App"
    assert page.locator("nav").is_visible()

def test_login_flow(page: Page):
    page.goto("http://localhost:3000/login")
    page.fill("#email", "user@example.com")
    page.fill("#password", "secret")
    page.click("button[type=submit]")
    page.wait_for_url("**/dashboard")
    assert "Welcome" in page.text_content("h1")
```

Run with: `pytest tests/ --headed` (or `--headless`)

## Debugging Tips

- Use `page.pause()` to open the Playwright Inspector for interactive debugging
- Use `--headed` mode to see the browser while tests run
- `page.locator(...).highlight()` to visually identify elements
- Check `page.content()` to see the full HTML if elements can't be found
