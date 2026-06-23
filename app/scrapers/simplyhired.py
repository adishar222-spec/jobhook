"""
SimplyHired India job scraper using Selenium.

URL pattern: https://www.simplyhired.co.in/search?q={role}&l=India
Extracts: title, company, location, salary (parsed to int), link, description, platform
"""
import re
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

LIMIT = 30
PAGE_WAIT = 10


def _parse_salary(salary_text: str) -> int | None:
    """
    Convert salary strings to monthly integer (INR).
    Examples:
      "₹50,000 a month"         → 50000
      "₹6,00,000 a year"        → 50000
      "From ₹40,000 a month"    → 40000
      "₹50,000 - ₹60,000 a month" → 55000
    """
    if not salary_text:
        return None
    try:
        text = salary_text.replace("From", "").replace("Up to", "").strip()
        # Detect period
        period = "month"
        if "a year" in text:
            period = "year"

        # Extract all numeric parts (handles Indian comma format)
        nums = re.findall(r"[\d,]+", text)
        if not nums:
            return None
        amounts = [float(n.replace(",", "")) for n in nums]
        avg = sum(amounts) / len(amounts)

        if period == "year":
            avg /= 12
        return int(avg)
    except Exception:
        return None


def _safe_text(driver_or_el, by, selector, default="") -> str:
    try:
        return driver_or_el.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return default


def parse(role: str, driver) -> list[dict]:
    """
    Scrape SimplyHired India for jobs matching `role`.
    Returns a list of job dicts ready for MongoDB insertion.
    """
    jobs: list[dict] = []
    seen_links: set[str] = set()
    page = 1

    logger.info(f"[SimplyHired] Starting scrape for role='{role}'")

    while len(jobs) < LIMIT:
        encoded_role = role.replace(" ", "+")
        url = (
            f"https://www.simplyhired.co.in/search?q={encoded_role}&l=India"
            if page == 1
            else f"https://www.simplyhired.co.in/search?q={encoded_role}&l=India&pn={page}"
        )

        try:
            driver.get(url)
            WebDriverWait(driver, PAGE_WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='searchSerpJob']"))
            )
        except TimeoutException:
            logger.warning(f"[SimplyHired] Timeout on page {page}, stopping.")
            break

        cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='searchSerpJob']")
        if not cards:
            logger.info(f"[SimplyHired] No cards on page {page}, stopping.")
            break

        page_jobs = 0
        for card in cards:
            if len(jobs) >= LIMIT:
                break
            try:
                # Click card to reveal description panel
                card.click()
                time.sleep(1.2)

                title = _safe_text(card, By.CSS_SELECTOR, "[data-testid='searchSerpJobTitle']")
                company = _safe_text(card, By.CSS_SELECTOR, "[data-testid='companyName']")
                location = _safe_text(card, By.CSS_SELECTOR, "[data-testid='searchSerpJobLocation']")
                salary_raw = _safe_text(card, By.CSS_SELECTOR, "[data-testid='searchSerpJobSalaryConfirmed']")

                # Get link
                try:
                    link_el = card.find_element(By.CSS_SELECTOR, "[data-testid='searchSerpJobTitle']")
                    link = link_el.get_attribute("href") or ""
                except NoSuchElementException:
                    link = ""

                if not title or link in seen_links:
                    continue

                # Try to get full description from right panel
                description = ""
                try:
                    desc_panel = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "[data-testid='viewJobBodyJobFullDescriptionContent']")
                        )
                    )
                    description = desc_panel.text[:2000]
                except TimeoutException:
                    pass

                seen_links.add(link)
                jobs.append({
                    "name": title,
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary": _parse_salary(salary_raw),
                    "salary_text": salary_raw or None,
                    "link": link,
                    "description": description,
                    "platform": "simplyhired",
                    "scraped_at": datetime.now(timezone.utc),
                })
                page_jobs += 1

            except StaleElementReferenceException:
                continue
            except Exception as e:
                logger.debug(f"[SimplyHired] Error parsing card: {e}")
                continue

        logger.info(f"[SimplyHired] Page {page}: collected {page_jobs} jobs (total {len(jobs)})")

        if page_jobs == 0:
            logger.info(f"[SimplyHired] No new jobs collected on page {page}, stopping.")
            break

        # Check for next page button
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "[aria-label='next']")
            if not next_btn.is_enabled():
                break
        except NoSuchElementException:
            break

        page += 1
        time.sleep(1.5)

    logger.info(f"[SimplyHired] Done — {len(jobs)} jobs scraped.")
    return jobs
