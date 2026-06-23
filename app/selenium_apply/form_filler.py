from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class FormFiller:
    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def fill_text(self, selector: str, value: str,
                   by: By = By.CSS_SELECTOR) -> bool:
        try:
            el = self.wait.until(EC.presence_of_element_located((by, selector)))
            el.clear()
            el.send_keys(value)
            return True
        except TimeoutException:
            return False

    def click(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        try:
            el = self.wait.until(EC.element_to_be_clickable((by, selector)))
            el.click()
            return True
        except TimeoutException:
            return False

    def select_dropdown(self, selector: str, value: str,
                         by: By = By.CSS_SELECTOR) -> bool:
        try:
            el = self.wait.until(EC.presence_of_element_located((by, selector)))
            Select(el).select_by_visible_text(value)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def upload_file(self, input_selector: str, file_path: str) -> bool:
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, input_selector)
            el.send_keys(file_path)
            return True
        except NoSuchElementException:
            return False

    def wait_for_confirmation(self, selector: str,
                               timeout: int = 30) -> bool:
        """Wait for a success confirmation element on the page."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            return False
