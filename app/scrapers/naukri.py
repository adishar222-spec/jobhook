"""
Naukri.com job scraper using Selenium.

URL pattern: https://www.naukri.com/{role}-jobs
Extracts: title, company, location, salary, link, description, platform
"""
import time
import logging
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)

logger = logging.getLogger(__name__)

LIMIT = 30          # max jobs to collect
PAGE_WAIT = 8       # seconds to wait for job list to load
DETAIL_WAIT = 5     # seconds to wait for detail page elements


def _safe_text(element, by, selector, default="") -> str:
    """Find a child element and return its text, or default if not found."""
    try:
        return element.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return default


def _safe_attr(element, by, selector, attr, default="") -> str:
    """Find a child element and return an attribute value, or default."""
    try:
        return element.find_element(by, selector).get_attribute(attr) or default
    except NoSuchElementException:
        return default


def _get_description(driver, link: str) -> str:
    """Open job detail page and extract the full description."""
    try:
        driver.get(link)
        WebDriverWait(driver, DETAIL_WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "styles_JDC__dang-inner-html__h0K4t"))
        )
        return driver.find_element(By.CLASS_NAME, "styles_JDC__dang-inner-html__h0K4t").text[:2000]
    except Exception:
        # Fall back — try alternate selector
        try:
            return driver.find_element(By.CLASS_NAME, "job-desc").text[:2000]
        except Exception:
            return ""


def parse(role: str, driver) -> list[dict]:
    """
    Scrape Naukri.com for jobs matching `role`.
    Returns a list of job dicts ready for MongoDB insertion.
    """
    jobs: list[dict] = []
    role_slug = role.strip().lower().replace(" ", "-")
    base_url = f"https://www.naukri.com/{role_slug}-jobs"
    page = 1

    logger.info(f"[Naukri] Starting scrape for role='{role}'")

    while len(jobs) < LIMIT:
        url = base_url if page == 1 else f"{base_url}-{page}"
        try:
            driver.get(url)
            WebDriverWait(driver, PAGE_WAIT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
            )
        except TimeoutException:
            logger.warning(f"[Naukri] Timeout on page {page}, stopping.")
            break

        cards = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
        if not cards:
            logger.info(f"[Naukri] No cards found on page {page}, stopping.")
            break

        page_jobs = 0
        for card in cards:
            if len(jobs) >= LIMIT:
                break
            try:
                title = _safe_text(card, By.CLASS_NAME, "title")
                if not title:
                    # Alternate title selector used in newer Naukri layout
                    title = _safe_text(card, By.CSS_SELECTOR, "a.title")
                link = _safe_attr(card, By.CLASS_NAME, "title", "href") or \
                       _safe_attr(card, By.CSS_SELECTOR, "a.title", "href")
                company = _safe_text(card, By.CLASS_NAME, "comp-name")
                location = _safe_text(card, By.CLASS_NAME, "locWdth")
                salary = _safe_text(card, By.CLASS_NAME, "sal-wrap") or None

                if not title or not link:
                    continue

                jobs.append({
                    "name": title,
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary_text": salary,
                    "salary": None,  # Naukri salary is unstructured text
                    "link": link,
                    "description": "",   # filled below
                    "platform": "naukri",
                    "scraped_at": datetime.now(timezone.utc),
                })
                page_jobs += 1
            except StaleElementReferenceException:
                continue
            except Exception as e:
                logger.debug(f"[Naukri] Error parsing card: {e}")
                continue

        logger.info(f"[Naukri] Page {page}: collected {page_jobs} jobs (total {len(jobs)})")

        if page_jobs == 0:
            logger.info(f"[Naukri] No new jobs collected on page {page}, stopping.")
            break

        # Check for next page
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
            if not next_btn.is_enabled():
                break
        except NoSuchElementException:
            break

        page += 1
        time.sleep(1.5)  # polite delay between pages

    # Fetch descriptions from detail pages (up to first 25 to save time)
    logger.info(f"[Naukri] Fetching descriptions for {min(len(jobs), 25)} jobs…")
    for i, job in enumerate(jobs[:25]):
        if job["link"]:
            job["description"] = _get_description(driver, job["link"])
            time.sleep(0.5)

    logger.info(f"[Naukri] Done — {len(jobs)} jobs scraped.")
    return jobs
