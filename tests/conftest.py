import pytest
from datetime import datetime
from base.webdriverfactory import WebDriverFactory
from base.selenium_driver import SeleniumDriver
from pages.home.register_page import RegisterPage
from utilities import db_helper


# ── Shared dynamic credentials for the entire test session ────────────────
def _make_credentials() -> dict:
    now = datetime.now()
    first_name = now.strftime("%B")
    last_name = now.strftime("%d%Y%H%M%S")
    return {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "email": f"user.{now.strftime('%m%d%Y%H%M%S')}@testmail.com",
        "password": "Test@1234",
    }


@pytest.fixture(scope="session")
def credentials() -> dict:
    """Dynamic unique credentials shared across the session."""
    return _make_credentials()


@pytest.fixture(scope="session")
def registered_user(credentials: dict, browser: str):
    """
    Session-scoped fixture:
      1. Opens a temporary browser and registers the user on the website via UI
      2. Saves the user to the local DB
      3. Yields credentials + DB id to all tests
      4. Deletes the user from the DB on session teardown (always runs)
    """
    wdf = WebDriverFactory(browser)
    setup_driver = wdf.getWebDriverInstance()
    try:
        rp = RegisterPage(setup_driver)
        setup_driver.get("https://rahulshettyacademy.com/client")
        rp.click_register_link()
        rp.wait_for_visibility(rp._first_name_field)
        rp.register(
            first_name=credentials["first_name"],
            last_name=credentials["last_name"],
            email=credentials["email"],
            phone="1234567890",
            occupation="Engineer",
            password=credentials["password"],
            gender="Male",
        )
        assert rp.verify_registration_successful(), \
            f"UI registration failed for {credentials['email']} during session setup"
    finally:
        setup_driver.quit()

    user_id = db_helper.save_user(
        credentials["first_name"],
        credentials["last_name"],
        credentials["email"],
    )
    assert user_id is not None, "Failed to save test user to DB during session setup"

    yield {**credentials, "id": user_id}

    db_helper.delete_user_by_id(user_id)


@pytest.fixture(scope="session")
def driver(browser):
    """Session-scoped WebDriver fixture — one browser for the entire test run."""
    wdf = WebDriverFactory(browser)
    _driver = wdf.getWebDriverInstance()
    yield _driver
    _driver.quit()


# Keep oneTimeSetUp so any legacy tests still work
@pytest.fixture(scope="class")
def oneTimeSetUp(request, browser):
    wdf = WebDriverFactory(browser)
    _driver = wdf.getWebDriverInstance()
    if request.cls is not None:
        request.cls.driver = _driver
    yield _driver
    _driver.quit()
    print("\nRunning one time tearDown")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Take a screenshot automatically when a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        _driver = None
        # Pure pytest style: driver fixture injected via funcargs
        if "driver" in item.fixturenames:
            _driver = item.funcargs.get("driver")
        # Legacy unittest.TestCase style
        elif hasattr(item, "instance") and hasattr(item.instance, "driver"):
            _driver = item.instance.driver
        elif "oneTimeSetUp" in item.fixturenames:
            _driver = item.funcargs.get("oneTimeSetUp")

        if _driver:
            sd = SeleniumDriver(_driver)
            test_name = item.nodeid.replace("/", "_").replace("::", "_").replace(" ", "_")
            screenshot_path = sd.take_screenshot(test_name)
            if screenshot_path:
                print(f"\n📸 Screenshot saved: {screenshot_path}")


