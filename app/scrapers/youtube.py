import time
import logging
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

def parse(keyword: str, driver) -> list[dict]:
    courses = []
    # YouTube search URL
    url = f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}+full+course"
    
    logger.info(f"[YouTube] Starting scrape for keyword='{keyword}'")
    driver.get(url)
    
    try:
        # Wait for video results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
    except TimeoutException:
        logger.warning(f"[YouTube] Timeout waiting for results.")
        return courses
        
    # Scroll a bit
    driver.execute_script("window.scrollTo(0, 1500);")
    time.sleep(2)
    
    elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
    
    for el in elements[:20]:  # Limit to 20 results
        try:
            title_el = el.find_element(By.ID, "video-title")
            title = title_el.get_attribute("title")
            if not title:
                title = title_el.text
            link = title_el.get_attribute("href")
            
            if not link:
                continue
                
            # YouTube channel name
            try:
                channel_el = el.find_element(By.CSS_SELECTOR, "ytd-channel-name a")
                channel = channel_el.text
            except:
                channel = "YouTube"
                
            # Thumbnail
            try:
                thumb_el = el.find_element(By.CSS_SELECTOR, "yt-image img")
                thumbnail = thumb_el.get_attribute("src") or ""
            except:
                thumbnail = ""
                
            # Snippet/Description
            try:
                description_el = el.find_element(By.ID, "description-text")
                description = description_el.text
            except:
                description = ""
                
            courses.append({
                "name": title,
                "title": title,
                "provider": "YouTube",
                "company": channel,  # maps to the UI
                "instructor": channel,
                "link": link,
                "description": description,
                "thumbnail": thumbnail,
                "platform": "youtube",
                "scraped_at": datetime.now(timezone.utc),
            })
        except Exception as e:
            logger.debug(f"[YouTube] Error parsing item: {e}")
            continue
            
    logger.info(f"[YouTube] Done — {len(courses)} courses scraped.")
    return courses
