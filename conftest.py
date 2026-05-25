import pytest
import os
from dotenv import load_dotenv
from base.webdriverfactory import WebDriverFactory

# Explicitly resolve .env relative to this file so it works regardless of
# the working directory pytest is invoked from.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def pytest_addoption(parser):
    parser.addoption(
        "--sel-browser",
        action="store",
        default=os.getenv("BROWSER", "chrome"),
        help="Browser to run tests: chrome, chrome-headless, firefox, safari"
    )


@pytest.fixture(scope="session")
def browser(request) -> str:
    return request.config.getoption("--sel-browser")


@pytest.fixture(scope="class")
def driver(browser):
    wdf = WebDriverFactory(browser)
    _driver = wdf.getWebDriverInstance()
    yield _driver
    _driver.quit()
