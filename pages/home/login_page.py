from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
import utilities.custom_logger as cl
import logging


class LoginPage(SeleniumDriver):

    log = cl.customLogger(logging.DEBUG)

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # Locators - rahulshettyacademy.com/client
    _email_field = (By.ID, "userEmail")
    _password_field = (By.ID, "userPassword")
    _login_button = (By.ID, "login")
    _error_message = (By.CSS_SELECTOR, ".toast-error")
    _dashboard_header = (By.CSS_SELECTOR, ".btn-danger")
    _forgot_password_link = (By.CSS_SELECTOR, "a[routerLink*='forgot'], a[href*='forgot'], .forgot-password, a:contains('Forgot')")
    _register_link = (By.CSS_SELECTOR, "a[routerLink*='register'], a[routerlink*='register']")

    def navigate_to_login(self):
        # Clear auth tokens so the Angular app always lands on the login page,
        # not the dashboard (critical when reusing a session-scoped driver).
        self.driver.get("https://rahulshettyacademy.com/client")
        self.driver.delete_all_cookies()
        try:
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        except Exception:
            pass
        self.driver.get("https://rahulshettyacademy.com/client")
        self.wait_for_visibility(self._email_field)

    def login(self, email: str, password: str):
        self.wait_for_visibility(self._email_field)
        self.driver.find_element(*self._email_field).clear()
        self.driver.find_element(*self._email_field).send_keys(email)
        self.driver.find_element(*self._password_field).clear()
        self.driver.find_element(*self._password_field).send_keys(password)
        self.driver.find_element(*self._login_button).click()

    def verify_login_successful(self) -> bool:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("dashboard")
            )
            return True
        except Exception:
            return self.wait_for_visibility(self._dashboard_header, timeout=5) is not None

    def verify_invalid_credentials(self) -> bool:
        return self.wait_for_visibility(self._error_message, timeout=5) is not None

    def verify_login_title(self) -> bool:
        return "login" in self.driver.current_url.lower()

    def get_title(self, expected_title: str) -> bool:
        self.wait_for_visibility(self._email_field)
        return self.driver.title == expected_title

    def click_forgot_password(self):
        self.driver.find_element(*self._forgot_password_link).click()

    def click_register_link(self):
        self.driver.find_element(*self._register_link).click()

    def refresh_page(self):
        self.driver.refresh()
        self.wait_for_visibility(self._email_field)