# Architecture Reference

## Fixture Hierarchy

```
pytest session
│
├── browser (session)           root conftest.py — reads BROWSER env var or --sel-browser
├── credentials (session)       tests/conftest.py — generates unique timestamped user data
└── registered_user (session)   tests/conftest.py
        │  1. spins up a temporary browser
        │  2. navigates to the app and registers via UI
        │  3. saves user to MySQL DB
        │  4. yields {first_name, last_name, full_name, email, password, id}
        │  teardown: deletes user from DB (always runs, even on crash)
        │
        └── driver (class)      one WebDriver instance per test class
                │
                ├── login_page (function)    LoginPage(driver) — fresh per test
                └── register_page (function) RegisterPage(driver) — fresh per test
```

### Why session-scoped registration?
The `registered_user` fixture replaced `test_01_register_and_save_to_db` + `test_99_delete_user_from_db`.
The old approach had two critical flaws:
1. Test ordering was enforced so `test_01` ran before login tests — brittle
2. A mid-run crash would leave orphaned rows in the DB

With a fixture, teardown is guaranteed by pytest's fixture machinery.

---

## Page Object Model

### Base class — `SeleniumDriver`
All page objects extend `SeleniumDriver`. Never instantiate `WebDriver` directly in page objects.

| Method | Purpose |
|---|---|
| `wait_for_visibility(locator, timeout)` | Returns element or `None` — never raises |
| `wait_for_element(locator, timeout)` | Waits for clickable, returns element or `None` |
| `is_element_present(locator)` | Immediate DOM check, returns `bool` |
| `take_screenshot(test_name)` | Saves PNG to `screenshots/`, returns path |
| `scroll_down_page(pixels)` | JS scroll |

### Locator convention
```python
class LoginPage(SeleniumDriver):
    # Class-level tuples — never instance vars
    _email_field    = (By.ID, "userEmail")
    _login_button   = (By.ID, "login")
    _error_message  = (By.CSS_SELECTOR, ".toast-error")
```

### Verify methods always return bool
```python
# CORRECT
def verify_login_successful(self) -> bool:
    return self.wait_for_visibility(self._dashboard_header) is not None

# WRONG — never assert inside page objects
def verify_login_successful(self):
    assert self.wait_for_visibility(self._dashboard_header)
```

---

## DB Helper

All DB functions read credentials lazily from env vars on each call.
No connection is held open between calls.

```
save_user(first_name, last_name, email)  → int (new id)
get_user_by_name(full_name)              → dict | None
get_user_by_id(user_id)                  → dict | None
delete_user_by_id(user_id)               → None
delete_user_by_name(full_name)           → None
user_exists(full_name)                   → bool
```

Schema:
```sql
CREATE TABLE IF NOT EXISTS Customers (
    id   INT PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255),
    age  INT
);
```

> Note: `email` is passed to `save_user` for logging only — the Customers table has no email column.

---

## WebDriver Factory

| Browser value | Result |
|---|---|
| `chrome` | Standard Chrome with `--no-sandbox` |
| `chrome-headless` | Chrome with `--headless --window-size=1920,1080` |
| `firefox` | Firefox via GeckoDriverManager |
| `safari` | Safari (macOS only) |

When `CI=true` env var is set, always uses `chrome-headless` regardless of `--sel-browser`.

---

## CI Pipeline (`.github/workflows/tests.yml`)

- Python 3.12
- pip cache keyed on `requirements.txt` hash
- Env vars injected from GitHub Secrets: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `--reruns 2 --reruns-delay 1` for flaky test resilience
- HTML report uploaded as artifact on every run
- Screenshots uploaded as artifact on failure
