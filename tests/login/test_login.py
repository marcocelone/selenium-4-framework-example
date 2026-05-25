import pytest
from pytest_testrail.plugin import pytestrail
from pages.home.login_page import LoginPage
from pages.home.register_page import RegisterPage
from utilities import db_helper


@pytest.fixture()
def login_page(driver) -> LoginPage:
    return LoginPage(driver)


@pytest.fixture()
def register_page(driver) -> RegisterPage:
    return RegisterPage(driver)


@pytest.mark.usefixtures("registered_user")
class TestLogin:

    # ─── DB VERIFICATION ─────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.order(1)
    @pytestrail.case('')
    def test_user_exists_in_db(self, registered_user: dict, login_page: LoginPage):
        """Verify the session-registered user exists in the DB"""
        user = db_helper.get_user_by_name(registered_user["full_name"])
        assert user is not None, f"User '{registered_user['full_name']}' not found in DB"
        assert user["name"] == registered_user["full_name"]

    # ─── POSITIVE TESTS ──────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.order(2)
    @pytestrail.case('')
    def test_login_page_loads(self, login_page: LoginPage):
        """Verify the login page loads with all required elements"""
        login_page.navigate_to_login()
        assert login_page.is_element_present(login_page._email_field), "Email field not found"
        assert login_page.is_element_present(login_page._password_field), "Password field not found"
        assert login_page.is_element_present(login_page._login_button), "Login button not found"

    @pytest.mark.smoke
    @pytest.mark.order(3)
    @pytestrail.case('')
    def test_valid_login_with_db_user(self, registered_user: dict, login_page: LoginPage):
        """Positive - Login with credentials stored in the DB"""
        login_page.navigate_to_login()
        login_page.login(registered_user["email"], registered_user["password"])
        assert login_page.verify_login_successful(), \
            f"Login failed for {registered_user['email']}"

    @pytest.mark.order(4)
    @pytestrail.case('')
    def test_forgot_password_link_visible(self, login_page: LoginPage):
        """Positive - Forgot Password link is present on the login page"""
        login_page.navigate_to_login()
        assert login_page.is_element_present(login_page._forgot_password_link), \
            "Forgot Password link not found"

    @pytest.mark.order(5)
    @pytestrail.case('')
    def test_register_link_visible(self, login_page: LoginPage):
        """Positive - 'Register here' link is present on the login page"""
        login_page.navigate_to_login()
        assert login_page.is_element_present(login_page._register_link), \
            "'Register here' link not found"

    # ─── NEGATIVE TESTS ──────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.order(6)
    @pytestrail.case('')
    def test_login_invalid_password(self, registered_user: dict, login_page: LoginPage):
        """Negative - Valid email but wrong password should show error"""
        login_page.navigate_to_login()
        login_page.login(registered_user["email"], "WrongPassword999!")
        assert login_page.verify_invalid_credentials(), \
            "Expected error message for wrong password"

    @pytest.mark.order(7)
    @pytestrail.case('')
    def test_login_invalid_email(self, registered_user: dict, login_page: LoginPage):
        """Negative - Non-existent email should show error"""
        login_page.navigate_to_login()
        login_page.login("notregistered@fake.com", registered_user["password"])
        assert login_page.verify_invalid_credentials(), \
            "Expected error message for non-existent email"

    @pytest.mark.order(8)
    @pytestrail.case('')
    def test_login_empty_credentials(self, login_page: LoginPage):
        """Negative - Empty email and password should stay on login page"""
        login_page.navigate_to_login()
        login_page.login("", "")
        login_page.wait_for_visibility(login_page._login_button)
        assert login_page.is_element_present(login_page._login_button), \
            "Expected to remain on login page with empty credentials"

    @pytest.mark.order(9)
    @pytestrail.case('')
    def test_login_empty_password(self, registered_user: dict, login_page: LoginPage):
        """Negative - Valid email but empty password should stay on login page"""
        login_page.navigate_to_login()
        login_page.login(registered_user["email"], "")
        login_page.wait_for_visibility(login_page._login_button)
        assert login_page.is_element_present(login_page._login_button), \
            "Expected to remain on login page with empty password"

    @pytest.mark.order(10)
    @pytestrail.case('')
    def test_login_invalid_email_format(self, registered_user: dict, login_page: LoginPage):
        """Negative - Malformed email should stay on login page"""
        login_page.navigate_to_login()
        login_page.login("notanemail", registered_user["password"])
        login_page.wait_for_visibility(login_page._login_button)
        assert login_page.is_element_present(login_page._login_button), \
            "Expected to remain on login page with invalid email format"
