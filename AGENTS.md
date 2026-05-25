# AI Agent Instructions — Selenium QA Framework

## Purpose
End-to-end UI test automation for https://rahulshettyacademy.com/client covering Login and Registration flows.

## Tech Stack
- Python 3.12, pytest 8.1, Selenium 4.18, MySQL (marcoai DB)
- Pure pytest classes (no unittest.TestCase)
- Page Object Model (POM)

## Repo Layout
```
conftest.py             root — browser fixture, .env loading
tests/
  conftest.py           session/class fixtures + screenshot hook
  login/
    test_login.py       TestLogin class (10 tests)
    test_register.py    TestRegister class (6 tests, 1 xfail)
pages/home/             LoginPage, RegisterPage (locators + actions)
base/                   SeleniumDriver (waits, screenshot), WebDriverFactory
utilities/db_helper.py  MySQL CRUD helpers
setup/login.py          BASE_URL
.env                    local secrets (not committed)
.env.example            template
```

## Rules for AI Agents

### NEVER do these
- Add `import time` or `time.sleep()` — use `wait_for_visibility()` instead
- Use `unittest.TestCase` as base class for test classes
- Hardcode credentials — always read from `.env` via `os.getenv()`
- Call bare `load_dotenv()` — always pass explicit `dotenv_path`
- Add module-level global variables to share state between tests — use fixtures
- Create tests that depend on other tests having run first — use session fixtures

### ALWAYS do these
- Inject `driver`, `login_page`, `register_page` as pytest fixture parameters
- Use `@pytest.mark.order(N)` for ordering
- Use `@pytest.mark.xfail` with a `reason=` for known app limitations
- Keep locators as `(By.X, "selector")` tuples at class level in page objects
- Write `verify_*` methods that return `bool` — no assertions inside page objects

## Fixture Contract
```python
# Session — runs once, registers user on site + DB, cleans up after
@pytest.fixture(scope="session")
def registered_user(credentials, browser) -> dict:
    # yields: {first_name, last_name, full_name, email, password, id}

# Class — one browser per test class
@pytest.fixture(scope="class")
def driver(browser): ...

# Function — fresh page object per test
@pytest.fixture()
def login_page(driver) -> LoginPage: ...
```

## Environment Variables
All required — framework raises `EnvironmentError` with a clear message if any are missing:
```
BROWSER        chrome | chrome-headless | firefox | safari
DB_HOST        MySQL host
DB_USER        MySQL user
DB_PASSWORD    MySQL password
DB_NAME        MySQL database name
```

## Running Tests
```bash
pytest tests/ -v                                    # full suite
pytest tests/ -m smoke -v                           # smoke only
pytest tests/login/test_login.py -v                 # single file
pytest tests/ --sel-browser=chrome-headless -v      # specific browser
CI=true pytest tests/ -v                            # auto headless
```

## Known Limitations of App Under Test
- `rahulshettyacademy.com` does not enforce unique emails → duplicate email test is `xfail`
- Short password validation is silent (no toast, no inline error) → verified via URL + no-success-toast check
- Angular uses `ng-invalid` not `is-invalid` for field validation
