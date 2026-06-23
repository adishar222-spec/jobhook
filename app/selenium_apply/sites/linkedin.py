from selenium.webdriver.common.by import By
from ..form_filler import FormFiller
from ..driver import take_screenshot
import time


class LinkedInApplier:
    """
    Handles Easy Apply flow on LinkedIn.
    NOTE: Requires user to be pre-logged in via browser session
    or pass session cookies.
    """
    EASY_APPLY_BTN = "button.jobs-apply-button"
    PHONE_INPUT = "input[id*='phoneNumber']"
    SUBMIT_BTN = "button[aria-label='Submit application']"
    NEXT_BTN = "button[aria-label='Continue to next step']"
    SUCCESS_ELEMENT = ".artdeco-inline-feedback--success"

    def __init__(self, driver):
        self.driver = driver
        self.filler = FormFiller(driver)

    def apply(self, job_url: str, applicant_data: dict,
               resume_path: str, screenshot_dir: str) -> dict:
        """
        Semi-automatic LinkedIn Easy Apply.
        Returns result dict with success status and screenshot path.
        """
        self.driver.get(job_url)
        time.sleep(2)

        # Click Easy Apply
        if not self.filler.click(self.EASY_APPLY_BTN):
            return {"success": False, "error": "Easy Apply button not found"}

        time.sleep(1)

        # Fill phone if prompted
        self.filler.fill_text(
            self.PHONE_INPUT, applicant_data.get("phone", "")
        )

        # Upload resume if file input present
        self.filler.upload_file(
            "input[name='resume']", resume_path
        )

        # Step through multi-step form
        for _ in range(5):  # Max 5 steps
            if not self.filler.click(self.NEXT_BTN):
                break
            time.sleep(1.5)

        # Submit
        self.filler.click(self.SUBMIT_BTN)
        time.sleep(2)

        # Take screenshot as proof
        screenshot_path = f"{screenshot_dir}/linkedin_{int(time.time())}.png"
        take_screenshot(self.driver, screenshot_path)

        success = self.filler.wait_for_confirmation(self.SUCCESS_ELEMENT, timeout=10)

        return {
            "success": success,
            "screenshot_path": screenshot_path,
            "platform": "LinkedIn"
        }
