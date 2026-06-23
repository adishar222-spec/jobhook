from selenium.webdriver.common.by import By
from ..form_filler import FormFiller
from ..driver import take_screenshot
import time

class GreenhouseApplier:
    def __init__(self, driver):
        self.driver = driver
        self.filler = FormFiller(driver)

    def apply(self, job_url: str, applicant_data: dict, resume_path: str, screenshot_dir: str) -> dict:
        self.driver.get(job_url)
        time.sleep(2)
        # Placeholder for Greenhouse Apply logic
        return {"success": False, "error": "Greenhouse Apply logic not implemented yet"}
