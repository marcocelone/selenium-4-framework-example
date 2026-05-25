# QA Automation Framework with Selenium

A modern Selenium 4 + pytest end-to-end automation framework for [rahulshettyacademy.com/client](https://rahulshettyacademy.com/client), covering the full **Login** and **Registration** user flows with dynamic test data, DB persistence, and automatic failure screenshots.

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Language |
| Selenium | 4.18 | Browser automation |
| pytest | 8.1 | Test runner |
| webdriver-manager | 4.1 | Auto-managed ChromeDriver/GeckoDriver |
| mysql-connector-python | 9.7 | DB persistence of test users |
| pytest-order | 1.4 | Enforce test execution order |
| pytest-html | 4.1 | HTML test reports |
| allure-pytest | 2.13 | Allure reports |
| pytest-testrail | 2.9 | TestRail integration |
| pytest-rerunfailures | 14.0 | Automatic retry for flaky tests |
| pytest-xdist | 3.6 | Parallel test execution |
| python-dotenv | 1.0 | Environment variable management |

---

## Project Structure

```
├── base/
│   ├── selenium_driver.py       # Base class: waits, element helpers, screenshot capture
│   └── webdriverfactory.py      # Browser factory (Chrome, Firefox, Safari, headless)
├── pages/
│   └── home/
│       ├── login_page.py        # Login page object (locators + actions)
│       └── register_page.py     # Register page object (locators + actions)
├── tests/
│   ├── conftest.py              # Session fixtures (credentials, registered_user, driver) + screenshot hook
│   └── login/
│       ├── test_login.py        # Login test suite — pure pytest class
│       └── test_register.py     # Registration test suite — pure pytest class
├── utilities/
│   ├── custom_logger.py         # File-based logger (automation.log)
│   └── db_helper.py             # MySQL CRUD helpers (save, get, delete user)
├── setup/
│   └── login.py                 # Base URL config
├── ai-agents/
│   ├── architecture.md          # Fixture hierarchy, POM conventions, DB schema
│   ├── troubleshooting.md       # Error reference and common fixes
│   └── adding-tests.md          # Templates for new tests, page objects, suites
├── .github/
│   ├── copilot-instructions.md  # AI coding assistant context (auto-loaded by Copilot)
│   └── workflows/tests.yml      # CI pipeline
├── AGENTS.md                    # AI agent instructions (Copilot, Codex, Cursor)
├── conftest.py                  # Root: browser fixture + --sel-browser option
├── pytest.ini                   # Markers + default options
├── requirements.txt             # Pinned dependencies
├── .env                         # Local env vars (not committed)
└── .env.example                 # Safe credential template to copy from
```

---

## Setup

### 1. Clone & create virtual environment

```bash
git clone <repo-url>
cd selenium-fe-qa-automation
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# edit .env and fill in your values
```

```env
BROWSER=chrome          # chrome | chrome-headless | firefox | safari
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=marcoai
```

> ⚠️ Never commit `.env`. Credentials are loaded automatically via `python-dotenv`.

### 4. MySQL DB requirement

The framework writes test users to a `Customers` table:

```sql
CREATE TABLE IF NOT EXISTS Customers (
    id   INT PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255),
    age  INT
);
```

---

## Running Tests

### Full suite
```bash
pytest tests/ -v
```

### Smoke suite only
```bash
pytest tests/ -m smoke -v
```

### Single test file
```bash
pytest tests/login/test_login.py -v
```

### Specific browser
```bash
pytest tests/ -v --sel-browser=firefox
pytest tests/ -v --sel-browser=chrome-headless
```

### Parallel execution
```bash
pytest tests/ -v -n auto          # auto-detect CPU cores
pytest tests/ -v -n 4             # fixed 4 workers
```

### Auto-retry flaky tests
```bash
pytest tests/ -v --reruns 2 --reruns-delay 1
```

### Generate HTML report
```bash
pytest tests/ -v --html=reports/report.html --self-contained-html
```

### Generate Allure report
```bash
pytest tests/ -v --alluredir=allure-results
allure serve allure-results
```

---

## Test Architecture — Pure pytest Style

The framework uses **pure pytest classes** with **fixture injection** — no `unittest.TestCase` inheritance.

### Why this matters

| Old approach | New approach |
|---|---|
| `class LoginTests(unittest.TestCase)` | `class TestLogin` — plain pytest class |
| Module-level globals for shared state | `credentials` / `registered_user` session fixtures |
| `test_01_register` + `test_99_delete` were tests acting as setup/teardown | `registered_user` fixture handles the full DB lifecycle |
| `self.driver` set by `usefixtures("oneTimeSetUp")` | `driver` injected directly as a method parameter |
| `time.sleep()` hard waits | `wait_for_visibility()` explicit waits everywhere |

### Fixture hierarchy

```
session
  ├── credentials        # unique timestamp-based user data (email, name, password)
  └── registered_user    # 1. registers via UI  2. saves to DB  3. teardown deletes from DB ✦
        │
class   └── driver       # one WebDriver instance per test class
              ├── login_page      # LoginPage(driver) — created fresh per test
              └── register_page   # RegisterPage(driver) — created fresh per test
```

> ✦ Because teardown lives in a fixture `yield`, the DB user is **always** deleted — even if tests fail or are interrupted.

---

## Test Flow — Login Suite (`test_login.py`)

The suite runs in order using `@pytest.mark.order(N)`. Test data and DB lifecycle are fully managed by fixtures — no test depends on another test having run first.

| # | Test | Marker | Description |
|---|------|--------|-------------|
| 1 | `test_user_exists_in_db` | smoke | Confirms session user was saved to DB by the fixture |
| 2 | `test_login_page_loads` | smoke | Verifies all login form elements are present |
| 3 | `test_valid_login_with_db_user` | smoke | Logs in with credentials from the `registered_user` fixture |
| 4 | `test_forgot_password_link_visible` | — | Checks Forgot Password link is present |
| 5 | `test_register_link_visible` | — | Checks Register link is present |
| 6 | `test_login_invalid_password` | smoke | Expects error on wrong password |
| 7 | `test_login_invalid_email` | — | Expects error on non-existent email |
| 8 | `test_login_empty_credentials` | — | Stays on login page with empty fields |
| 9 | `test_login_empty_password` | — | Stays on login page with empty password |
| 10 | `test_login_invalid_email_format` | — | Stays on login page with malformed email |

## Test Flow — Register Suite (`test_register.py`)

| # | Test | Marker | Description |
|---|------|--------|-------------|
| 1 | `test_register_page_loads` | smoke | Register page accessible from login |
| 2 | `test_register_successfully` | smoke | Full happy-path registration |
| 3 | `test_register_duplicate_email` | smoke | Duplicate email — **xfail** (demo site limitation) |
| 4 | `test_register_missing_required_fields` | — | Empty form shows validation errors |
| 5 | `test_register_invalid_email_format` | — | Invalid email format shows error |
| 6 | `test_register_short_password` | — | Short password silently blocked |

---

## Screenshot on Failure

When any test fails, a screenshot is automatically captured and saved to:

```
screenshots/<test_node_id>_<YYYYMMDD_HHMMSS>.png
```

---

## Logging

All test activity is logged to `automation.log`. Logs include element interactions, wait results, DB operations, and screenshot paths.

---

## CI / Headless Mode

Set `CI=true` to automatically switch to `chrome-headless` regardless of `--sel-browser`:

```bash
CI=true pytest tests/ -m smoke -v
```

The GitHub Actions workflow (`.github/workflows/tests.yml`) sets this automatically and uploads the HTML report and failure screenshots as artifacts.

---

## Documentation

| File | Contents |
|---|---|
| [`ai-agents/architecture.md`](ai-agents/architecture.md) | Fixture hierarchy, POM conventions, DB schema, factory behaviour |
| [`ai-agents/troubleshooting.md`](ai-agents/troubleshooting.md) | Every known error mapped to its cause and fix |
| [`ai-agents/adding-tests.md`](ai-agents/adding-tests.md) | Templates for new tests, page objects, and test suites |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | AI assistant context — auto-loaded by GitHub Copilot |

---

## TestRail Integration

Test cases are mapped via `@pytestrail.case('C<id>')` decorators. Configure `testrail.cfg` with your TestRail instance credentials to push results automatically on each run.
