import pytest
from datetime import datetime
from pytest_testrail.plugin import pytestrail
from pages.home.register_page import RegisterPage
from pages.home.login_page import LoginPage


def _john_doe() -> dict:
    ts = datetime.now().strftime('%m%d%Y%H%M%S')
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john.doe.{ts}@testmail.com",
        "phone": "1234567890",
        "occupation": "Engineer",
        "password": "John@Doe123",
        "gender": "Male",
    }


@pytest.fixture(scope="class")
def john_doe() -> dict:
    """Unique John Doe credentials per test class run."""
    return _john_doe()


@pytest.fixture()
def register_page(driver) -> RegisterPage:
    return RegisterPage(driver)


@pytest.fixture()
def login_page(driver) -> LoginPage:
    return LoginPage(driver)


class TestRegister:

    # ─── POSITIVE TESTS ──────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.order(1)
    @pytestrail.case('')
    def test_register_page_loads(self, register_page: RegisterPage, driver):
        """Verify the Register page is accessible from the login page"""
        driver.get("https://rahulshettyacademy.com/client")
        register_page.click_register_link()
        register_page.wait_for_visibility(register_page._first_name_field)
        assert "register" in driver.current_url.lower() or \
               register_page.is_element_present(register_page._first_name_field)

    @pytest.mark.smoke
    @pytest.mark.order(2)
    @pytestrail.case('')
    def test_register_successfully(self, john_doe: dict, register_page: RegisterPage, driver):
        """Positive - Register a new user successfully"""
        driver.get("https://rahulshettyacademy.com/client")
        register_page.click_register_link()
        register_page.wait_for_visibility(register_page._first_name_field)
        register_page.register(**john_doe)
        assert register_page.verify_registration_successful(), \
            "Registration was not successful"

    # ─── NEGATIVE TESTS ──────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.order(3)
    @pytest.mark.xfail(
        reason="rahulshettyacademy.com (demo site) does not enforce unique emails — "
               "duplicate registration succeeds instead of returning an error.",
        strict=False,
    )
    @pytestrail.case('')
    def test_register_duplicate_email(self, john_doe: dict, register_page: RegisterPage, driver):
        """Negative - Registering with an already-used email should show error"""
        driver.get("https://rahulshettyacademy.com/client")
        register_page.click_register_link()
        register_page.wait_for_visibility(register_page._first_name_field)
        register_page.register(**john_doe)
        assert register_page.verify_email_already_exists(), \
            "Expected 'Email already exists' error message"

    @pytest.mark.order(4)
    @pytestrail.case('')
    def test_register_missing_required_fields(self, register_page: RegisterPage, driver):
        """Negative - Submitting empty form should show required field errors"""
        driver.get("https://rahulshettyacademy.com/client")
        register_page.click_register_link()
        register_page.wait_for_visibility(register_page._first_name_field)
        driver.find_element(*register_page._register_button).click()
        assert register_page.verify_required_field_error(), \
            "Expected validation errors for empty form"

    @pytest.mark.order(5)
    @pytestrail.case('')
    def test_register_invalid_email_format(self, register_page: RegisterPage, driver):
        """Negative - Invalid email format should show validation error"""
        driver.get("https://rahulshettyacademy.com/client")
        register_page.click_register_link()
        register_page.wait_for_visibility(register_page._first_name_field)
        register_page.register(
            first_name="Jane", last_name="Doe", email="not-an-email",
            phone="9876543210", occupation="Engineer",
            password="Jane@Doe123", gender="Male",
        )
        assert register_page.verify_required_field_error(), \
            "Expected validation error for invalid email format"

    @pytest.mark.order(6)
    @pytestrail.case('')
    def test_register_short_password(self, register_page: RegisterPage, driver):
        """Negative - Password too short should show validation error"""
        driver.get("https://rahulshettyacademy.com/client")
        register_page.click_register_link()
        register_page.wait_for_visibility(register_page._first_name_field)
        register_page.register(
            first_name="Jane", last_name="Doe", email="jane.shortpass@test.com",
            phone="9876543210", occupation="Engineer",
            password="123", gender="Male",
        )
        assert register_page.verify_required_field_error(), \
            "Expected validation error for short password"
