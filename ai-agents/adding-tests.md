# Adding Tests — Conventions & Examples

## Adding a new test to an existing suite

```python
@pytest.mark.order(11)          # next available order number
@pytestrail.case('')            # fill in TestRail case ID when assigned
def test_login_with_special_chars(self, registered_user: dict, login_page: LoginPage):
    """Negative - Email with special characters should show error"""
    login_page.navigate_to_login()
    login_page.login("user+tag@test.com", registered_user["password"])
    assert login_page.verify_invalid_credentials(), \
        "Expected error for special char email"
```

---

## Adding a new page object

### 1. Create the file
```
pages/home/checkout_page.py
```

### 2. Follow the template
```python
from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
import utilities.custom_logger as cl
import logging


class CheckoutPage(SeleniumDriver):

    log = cl.customLogger(logging.DEBUG)

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # ── Locators ──────────────────────────────────────────────────────────
    _cart_items     = (By.CSS_SELECTOR, ".cartSection h3")
    _checkout_btn   = (By.CSS_SELECTOR, ".totalAmount button")
    _order_summary  = (By.CSS_SELECTOR, ".order-summary")

    # ── Actions ───────────────────────────────────────────────────────────
    def get_cart_item_names(self) -> list[str]:
        self.wait_for_visibility(self._cart_items)
        return [el.text for el in self.driver.find_elements(*self._cart_items)]

    def click_checkout(self):
        btn = self.wait_for_element(self._checkout_btn)
        if btn:
            btn.click()

    def verify_order_placed(self) -> bool:
        return self.wait_for_visibility(self._order_summary, timeout=10) is not None
```

### 3. Add a fixture in `tests/conftest.py` or the test file
```python
@pytest.fixture()
def checkout_page(driver) -> CheckoutPage:
    return CheckoutPage(driver)
```

---

## Adding a new test suite (new flow)

### 1. Create the folder and files
```
tests/checkout/
    __init__.py
    test_checkout.py
```

### 2. Test file template
```python
import pytest
from pytest_testrail.plugin import pytestrail
from pages.home.checkout_page import CheckoutPage
from pages.home.login_page import LoginPage


@pytest.fixture()
def checkout_page(driver) -> CheckoutPage:
    return CheckoutPage(driver)


@pytest.fixture()
def login_page(driver) -> LoginPage:
    return LoginPage(driver)


@pytest.mark.usefixtures("registered_user")
class TestCheckout:

    @pytest.mark.smoke
    @pytest.mark.order(1)
    @pytestrail.case('')
    def test_cart_has_items(self, registered_user: dict, login_page: LoginPage,
                            checkout_page: CheckoutPage):
        """Verify cart contains items after login"""
        login_page.navigate_to_login()
        login_page.login(registered_user["email"], registered_user["password"])
        assert login_page.verify_login_successful()
        items = checkout_page.get_cart_item_names()
        assert len(items) > 0, "Expected at least one item in the cart"
```

---

## Marking known failures

```python
@pytest.mark.xfail(
    reason="Site does not enforce X — known demo site limitation.",
    strict=False,   # xpass won't break the suite
)
def test_something_the_site_gets_wrong(self, ...):
    ...
```

Use `strict=True` only when you want CI to fail if the app *fixes* the bug
(i.e. you want to be forced to remove the marker).

---

## Marking smoke tests

Add `@pytest.mark.smoke` to any test that should run in the fast smoke suite:
```bash
pytest tests/ -m smoke -v
```

Smoke tests should:
- Cover the critical happy path only
- Complete in under 2 minutes total
- Not depend on non-smoke tests having run first
