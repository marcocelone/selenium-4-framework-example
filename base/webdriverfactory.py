"""
@package base

WebDriver Factory class implementation
It creates a webdriver instance based on browser configurations

Example:
    wdf = WebDriverFactory(browser)
    wdf.getWebDriverInstance()
"""
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from setup.login import base_url
import os


class WebDriverFactory:

    def __init__(self, browser: str):
        """
        Inits WebDriverFactory class

        Returns:
            None
        """
        # Auto-switch to chrome-headless if running in CI pipeline
        is_ci = os.getenv("CI", "false").lower() == "true"
        self.browser = "chrome-headless" if is_ci else (browser or "chrome").lower()
        """
        Set chrome driver and iexplorer environment based on OS
        PREFERRED: Set the path on the machine where browser will be executed
        """

    def getWebDriverInstance(self):
        """
       Get WebDriver Instance based on the browser configuration

        Returns:
            'WebDriver Instance'
        """
        if self.browser == "safari":
            driver = webdriver.Safari()
        elif self.browser == "firefox":
            driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install())
            )
        elif self.browser == "chrome-headless":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)
        else:
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(5)
        driver.maximize_window()
        driver.get(base_url)
        return driver