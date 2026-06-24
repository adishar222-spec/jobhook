"""
EdxProvider — scrapes edx.org using Selenium (visible Chrome).

Returns a list of course dicts with the standard schema:
  title, provider, instructor, link, description, thumbnail, platform, scraped_at
"""
import time
import logging
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

LIMIT = 15


class EdxProvider:
    name = "edx"
    label = "edX"

    @staticmethod
    def fetch(keyword: str, driver) -> list[dict]:
        """Fetch courses from edx.org for the given keyword using Selenium."""
        courses: list[dict] = []
        url = f"https://www.edx.org/search?q={keyword.replace(' ', '%20')}"
        logger.info(f"[EdxProvider] Fetching keyword='{keyword}'")

        driver.get(url)
        time.sleep(5)  # edX is React-heavy; needs JS time

        try:
            cards = driver.find_elements(
                By.CSS_SELECTOR,
                "a[href*='/course/'], a[href*='/professional-certificate/'], a[href*='/xseries/']",
            )
        except Exception as e:
            logger.error(f"[EdxProvider] DOM error: {e}")
            return courses

        seen: set[str] = set()
        for card in cards:
            if len(courses) >= LIMIT:
                break
            try:
                link = card.get_attribute("href") or ""
                if not link or "edx.org" not in link or link in seen:
                    continue

                parts = [t.strip() for t in (card.text or "").split("\n") if t.strip()]
                if len(parts) < 2:
                    continue

                provider = parts[0]
                title = parts[1]

                try:
                    img = card.find_element(By.TAG_NAME, "img")
                    thumbnail = img.get_attribute("src") or ""
                except Exception:
                    thumbnail = ""

                courses.append({
                    "title": title,
                    "name": title,
                    "provider": provider,
                    "company": provider,
                    "instructor": provider,
                    "link": link,
                    "description": "",
                    "thumbnail": thumbnail,
                    "platform": "edx",
                    "scraped_at": datetime.now(timezone.utc),
                })
                seen.add(link)
            except Exception:
                continue

        logger.info(f"[EdxProvider] Done — {len(courses)} courses")
        return courses
