from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from base.selenium_driver import SeleniumDriver
import utilities.custom_logger as cl
import logging


class RegisterPage(SeleniumDriver):

    log = cl.customLogger(logging.DEBUG)

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # Locators
    _register_link = (By.CSS_SELECTOR, "a[routerlink*='register']")
    _first_name_field = (By.ID, "firstName")
    _last_name_field = (By.ID, "lastName")
    _email_field = (By.ID, "userEmail")
    _phone_field = (By.ID, "userMobile")
    _occupation_dropdown = (By.CSS_SELECTOR, "select[formcontrolname='occupation']")
    _gender_male = (By.CSS_SELECTOR, "input[value='Male']")
    _password_field = (By.ID, "userPassword")
    _confirm_password_field = (By.ID, "confirmPassword")
    _register_button = (By.ID, "login")
    _age_checkbox = (By.CSS_SELECTOR, "input[type='checkbox']")
    _success_message = (By.CSS_SELECTOR, ".toast-success, [class*='toast'][class*='success']")
    _email_error = (By.CSS_SELECTOR, ".toast-error, [class*='toast'][class*='error']")
    _required_field_error = (By.CSS_SELECTOR, ".is-invalid, .ng-invalid:not(form):not(ng-form)")

    def click_register_link(self):
        element = self.wait_for_visibility(self._register_link)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.driver.execute_script("arguments[0].click();", element)

    def register(self, first_name: str, last_name: str, email: str,
                 phone: str, occupation: str, password: str, gender: str = "Male"):
        self.wait_for_visibility(self._first_name_field)
        self.driver.find_element(*self._first_name_field).clear()
        self.driver.find_element(*self._first_name_field).send_keys(first_name)
        self.driver.find_element(*self._last_name_field).clear()
        self.driver.find_element(*self._last_name_field).send_keys(last_name)
        self.driver.find_element(*self._email_field).clear()
        self.driver.find_element(*self._email_field).send_keys(email)
        self.driver.find_element(*self._phone_field).clear()
        self.driver.find_element(*self._phone_field).send_keys(phone)
        occupation_select = Select(self.driver.find_element(*self._occupation_dropdown))
        occupation_select.select_by_visible_text(occupation)
        if gender == "Male":
            self.driver.find_element(*self._gender_male).click()
        self.driver.find_element(*self._password_field).clear()
        self.driver.find_element(*self._password_field).send_keys(password)
        self.driver.find_element(*self._confirm_password_field).clear()
        self.driver.find_element(*self._confirm_password_field).send_keys(password)
        self.driver.find_element(*self._age_checkbox).click()
        self.driver.find_element(*self._register_button).click()

    def verify_registration_successful(self) -> bool:
        return self.wait_for_visibility(self._success_message, timeout=10) is not None

    def verify_email_already_exists(self) -> bool:
        """
        Returns True if the site shows an error toast for duplicate email.
        NOTE: rahulshettyacademy.com (demo site) does not enforce unique emails —
        this will return False by design on that environment.
        """
        return self.wait_for_visibility(self._email_error, timeout=5) is not None

    def verify_required_field_error(self) -> bool:
        """
        Validation failed if ANY of:
          - Angular inline ng-invalid/is-invalid marker is present
          - An error toast is visible
          - The page stayed on /register with no success toast (silent block)
        """
        inline_error = self.is_element_present(self._required_field_error)
        if inline_error:
            return True

        toast_error = self.wait_for_visibility(self._email_error, timeout=3) is not None
        if toast_error:
            return True

        # Silent block: form submission rejected, no success, still on register page
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            WebDriverWait(self.driver, 3).until(EC.url_contains("register"))
            success_shown = self.is_element_present(self._success_message)
            return not success_shown
        except Exception:
            return False
