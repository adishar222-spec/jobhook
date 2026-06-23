from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os


def get_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Initialize and return a Chrome WebDriver.
    Set headless=True for background automation,
    False for visible user-confirmation mode.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver_path = ChromeDriverManager().install()
    if not driver_path.endswith(".exe") and "THIRD_PARTY_NOTICES" in driver_path:
        driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
        
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Anti-bot detection countermeasure
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def take_screenshot(driver: webdriver.Chrome, path: str) -> str:
    """Save a screenshot and return the path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    return path
