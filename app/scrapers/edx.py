import time
import logging
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def parse(keyword: str, driver) -> list[dict]:
    courses = []
    url = f"https://www.edx.org/search?q={keyword.replace(' ', '%20')}"
    logger.info(f"[EDX] Starting scrape for keyword='{keyword}'")
    
    driver.get(url)
    time.sleep(5)  # Wait for page to load (edX uses heavy React/Nextjs)
    
    try:
        # Search for cards by checking links
        cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/course/'], a[href*='/professional-certificate/']")
        seen_links = set()
        
        for card in cards:
            if len(courses) >= 15:
                break
                
            try:
                link = card.get_attribute("href")
                if not link or link in seen_links:
                    continue
                    
                # Extract text using javascript for reliability since element text might be hidden
                text_content = driver.execute_script("return arguments[0].innerText;", card)
                if not text_content:
                    continue
                    
                text_parts = [t.strip() for t in text_content.split('\n') if t.strip()]
                if len(text_parts) < 2:
                    continue
                    
                provider = text_parts[0] # Usually the university comes first or vice versa
                title = text_parts[1]
                
                # Check if there is an image thumbnail inside
                try:
                    img = card.find_element(By.TAG_NAME, "img")
                    thumbnail = img.get_attribute("src") or ""
                except:
                    thumbnail = ""
                
                courses.append({
                    "name": title,
                    "title": title,
                    "provider": provider,
                    "company": provider, # maps to UI card
                    "instructor": provider,
                    "link": link,
                    "description": "",
                    "thumbnail": thumbnail,
                    "platform": "edx",
                    "scraped_at": datetime.now(timezone.utc),
                })
                seen_links.add(link)
            except Exception:
                continue
    except Exception as e:
        logger.error(f"[EDX] Error parsing: {e}")
        
    logger.info(f"[EDX] Done — {len(courses)} courses scraped.")
    return courses
