"""
Chrome WebDriver factory.
Uses webdriver-manager to auto-download the correct ChromeDriver version.
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_driver() -> webdriver.Chrome:
    """
    Returns a headless Chrome WebDriver ready for scraping.
    - Headless mode (no browser window)
    - Sandbox disabled for container/CI compatibility
    - Image loading disabled for speed
    """
    options = Options()
    # options.add_argument("--headless=new") # Make visible for user to see scraping
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    # Disable images for faster page loads
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    # Check if running in container (Docker)
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # Selenium 4.x has built-in manager, no need for ChromeDriverManager
        driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver
