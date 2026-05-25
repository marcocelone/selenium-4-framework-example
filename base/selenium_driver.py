from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotVisibleException,
    ElementNotSelectableException
)
from traceback import print_stack
from typing import Tuple
import utilities.custom_logger as cl
import logging
import os
import time


class SeleniumDriver:

    log = cl.customLogger(logging.DEBUG)

    def __init__(self, driver):
        self.driver = driver

    def is_element_present(self, locator: Tuple[By, str]) -> bool:
        """Safe check if element exists on the page"""
        try:
            self.driver.find_element(*locator)
            self.log.info(f"Element present: {locator}")
            return True
        except NoSuchElementException:
            self.log.warning(f"Element not present: {locator}")
            return False

    def wait_for_element(self, locator: Tuple[By, str],
                         timeout: int = 10, poll_frequency: float = 0.5):
        """Wait until element is clickable"""
        try:
            element = WebDriverWait(
                self.driver, timeout=timeout, poll_frequency=poll_frequency,
                ignored_exceptions=[NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException]
            ).until(EC.element_to_be_clickable(locator))
            self.log.info(f"Element clickable: {locator}")
            return element
        except Exception:
            self.log.error(f"Element not clickable after {timeout}s: {locator}")
            print_stack()
            return None

    def wait_for_visibility(self, locator: Tuple[By, str], timeout: int = 10):
        """Wait until element is visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            self.log.info(f"Element visible: {locator}")
            return element
        except Exception:
            self.log.error(f"Element not visible after {timeout}s: {locator}")
            return None

    def scroll_down_page(self, pixels: int = 1000):
        """Scroll down the page by given pixels"""
        try:
            self.driver.execute_script(f"window.scrollTo(0, {pixels});")
            self.log.info(f"Page scrolled {pixels}px")
        except Exception:
            self.log.error("Could not scroll page")
            print_stack()

    def take_screenshot(self, test_name: str) -> str | None:
        """
        Capture a screenshot and save it under screenshots/<test_name>_<timestamp>.png
        Returns the file path, or None if it failed.
        """
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        screenshots_dir = os.path.join(root_dir, "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)
        try:
            self.driver.save_screenshot(filepath)
            self.log.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.log.error(f"Failed to save screenshot: {e}")
            return None