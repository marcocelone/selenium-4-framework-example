# Troubleshooting Guide

## Quick Diagnosis Checklist

1. Is `.env` populated? (`cp .env.example .env` then fill values)
2. Is MySQL running and the `marcoai` database accessible?
3. Is the venv activated? (`source venv/bin/activate`)
4. Is Chrome/ChromeDriver up to date? (`pip install -U webdriver-manager`)
5. Is the site responsive? (try opening https://rahulshettyacademy.com/client manually)

---

## Error Reference

### `OSError: Starting path not found`
**Cause:** `load_dotenv()` called without an explicit path — `find_dotenv()` traverses the filesystem from a path that doesn't exist (common when pytest is launched from a different working directory).

**Fix:**
```python
# WRONG
load_dotenv()

# CORRECT
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
```

---

### `EnvironmentError: Missing required environment variable(s): DB_PASSWORD`
**Cause:** `.env` file is missing or the variable is not set.

**Fix:**
```bash
cp .env.example .env
# edit .env and fill in DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
```

---

### `ERROR` on all `TestLogin` tests (fixture error, not test failure)
**Cause:** The `registered_user` session fixture failed during setup — UI registration didn't complete.

**Diagnosis:** Look for the fixture error message above the test errors:
```
ERROR tests/login/test_login.py::TestLogin::test_user_exists_in_db
  AssertionError: UI registration failed for user.xxx@testmail.com during session setup
```

**Common causes:**
- Site is slow → increase timeout in `rp.verify_registration_successful(timeout=15)`
- `click_register_link()` called before `driver.get(base_url)` → ensure navigation happens first
- ChromeDriver version mismatch → `pip install -U webdriver-manager`

---

### `selenium.common.exceptions.ElementNotInteractableException` on register link
**Cause:** The register link element is found in the DOM but outside the viewport.

**Fix:** `RegisterPage.click_register_link()` already uses `scrollIntoView` + JS click. If it still fails, the locator may be wrong — inspect the page with DevTools.

---

### `xfail` in register suite
**Not a bug.** The `test_register_duplicate_email` test is marked `@pytest.mark.xfail` because `rahulshettyacademy.com` (a demo site) does not enforce unique email addresses. The site allows duplicate registration and returns a success toast. This is a known app limitation, not a framework defect.

---

### `test_register_short_password` fails
**Cause:** The site silently blocks short password submission — no toast, no inline error. The `verify_required_field_error()` method uses a three-layer check:
1. `.ng-invalid` / `.is-invalid` inline markers
2. Error toast
3. URL still contains `/register` with no success toast

If all three fail, the site behaviour has changed. Inspect the page manually to find the new validation signal.

---

### `test_register_duplicate_email` passes unexpectedly (`xpass`)
**Cause:** The site may have started enforcing unique emails. Remove the `@pytest.mark.xfail` decorator and update `verify_email_already_exists()` to assert the error toast locator.

---

### Browser crashes mid-run (`ConnectionRefusedError` / `WebDriverException`)
**Cause:** A previous test left the browser in a broken state (e.g. a successful login navigated away from the login page and a subsequent test's `navigate_to_login()` timed out waiting for the email field).

**Fix:**
- Each `navigate_to_login()` call does a full `driver.get(base_url)` — ensure this is the case
- Check that the `driver` fixture scope is `"class"` — one browser per class is correct
- If Chrome crashes, check available memory and disk space

---

### `Unknown pytest.mark.order` warning
**Cause:** `pytest-order` is not installed in the active virtual environment.

**Fix:**
```bash
pip install pytest-order==1.4.0
```

---

### Tests pass locally but fail in CI
**Common causes:**

| Symptom | Fix |
|---|---|
| `EnvironmentError: Missing DB_*` | Add `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` to GitHub Secrets |
| Chrome crashes in CI | Ensure `CI=true` is set — factory auto-switches to `chrome-headless` |
| Timeout failures | Demo site is slow; CI has higher latency — increase `wait_for_visibility` timeout |
| Wrong `--sel-browser` flag | CI uses `--sel-browser=chrome-headless`, not `--browser` |
