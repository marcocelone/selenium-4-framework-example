# GitHub Copilot Instructions — Selenium QA Framework

## Project Identity
- **App under test**: https://rahulshettyacademy.com/client (demo e-commerce site)
- **Language**: Python 3.12+
- **Test runner**: pytest (pure pytest style — NO unittest.TestCase)
- **Browser automation**: Selenium 4 + WebDriver Manager
- **DB**: MySQL (`marcoai` database, `Customers` table)

## Architecture at a Glance
```
conftest.py (root)       → browser fixture, load_dotenv with explicit path
tests/conftest.py        → registered_user session fixture (UI reg + DB save/delete)
                           driver class fixture, screenshot hook
pages/home/              → Page Object Model (LoginPage, RegisterPage)
base/selenium_driver.py  → Base class: wait_for_visibility, wait_for_element, take_screenshot
base/webdriverfactory.py → Chrome/Firefox/Safari/headless factory, CI auto-headless
utilities/db_helper.py   → MySQL CRUD: save_user, get_user_by_name, delete_user_by_id
setup/login.py           → BASE_URL constant
```

## Critical Patterns

### Fixture hierarchy (never break this order)
```
session: browser → credentials → registered_user (registers on site + saves to DB)
class:   driver  (one browser per test class)
func:    login_page(driver), register_page(driver)
```

### registered_user fixture
- Spins up its OWN temporary browser for UI registration (separate from test driver)
- Saves to DB after successful UI registration
- Teardown deletes from DB — guaranteed even on crash
- Tests should NEVER register the session user themselves

### Environment variables (all required — fail-fast if missing)
```
BROWSER, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
```
Loaded via `load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))`
— always use explicit path, never bare `load_dotenv()`

### Waits — explicit only
- Use `wait_for_visibility(locator, timeout)` — never `time.sleep()`
- Use `wait_for_element(locator)` for clickable elements

### Page Object conventions
- Locators are class-level tuples: `_email_field = (By.ID, "userEmail")`
- Prefixed with `_` (private by convention)
- All actions return `bool` or the element — never raise from page objects

## Known Site Limitations (rahulshettyacademy.com)
- **Duplicate emails**: site does NOT enforce uniqueness → `test_register_duplicate_email` is `@pytest.mark.xfail`
- **Short password**: no toast shown, form silently blocked → `verify_required_field_error` checks URL + no success toast as fallback
- **Angular app**: invalid fields use `ng-invalid`, not Bootstrap's `is-invalid`

## Test File Conventions
- Class name: `TestLogin`, `TestRegister` (no unittest base)
- Ordering: `@pytest.mark.order(N)`
- Smoke tests: `@pytest.mark.smoke`
- All tests receive fixtures as method parameters — no `self.driver`, no globals

## Common Failure Causes & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| `OSError: Starting path not found` | bare `load_dotenv()` | use `load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))` |
| `EnvironmentError: Missing DB_*` | `.env` not populated | copy `.env.example` → `.env`, fill values |
| `ERROR` on all TestLogin tests | `registered_user` fixture failed | check UI registration — site may be slow, increase timeout |
| `selenium.common.exceptions.WebDriverException` in fixture | `click_register_link()` called before navigation | ensure `driver.get(base_url)` is called first |
| `xfail` in register suite | expected — demo site limitation | not a bug |
