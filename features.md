# Job Scraping Feature — Automatic Job Collection from Multiple Platforms

**Feature Name:** Automatic Job Scraper  
**Tech Stack:** Selenium · Python · BeautifulSoup · FastAPI  
**Supported Platforms:** Naukri · Simply Hired · EDX (courses) · YouTube (courses)

---

## Overview

This feature provides **automated job scraping** from multiple job boards using Selenium web automation. Instead of manually scraping with BeautifulSoup (which only works on static HTML), Selenium handles dynamic JavaScript-rendered content and pagination.

**Key benefits:**
- Scrapes jobs from **multiple platforms** with a single interface
- Handles **pagination** automatically
- Extracts **detailed job information** (title, company, location, salary, description)
- Runs in **headless mode** (no UI) for production
- Works in **containerized environments** (Docker)
- **Async support** for non-blocking scraping

---

## Supported Job Platforms

### 1. **Naukri.com** (India's largest job board)
- **URL pattern:** `https://www.naukri.com/{job-name}-jobs`
- **Data extracted:** name, company, location, salary, description, link, timestamp
- **Pagination:** Yes (automatic, configurable limit)
- **Job details page:** Yes (fetches full description)

### 2. **Simply Hired** (Global, India-focused)
- **URL pattern:** `https://www.simplyhired.co.in/search?q={job_name}&l=India`
- **Data extracted:** name, company, location, salary (parsed), description, link, timestamp
- **Pagination:** Yes (automatic, configurable limit)
- **Salary parsing:** Yes (converts "₹50,000 a month" to monthly integer)

### 3. **EDX** (Course recommendations)
- **URL pattern:** `https://www.edx.org/search?q={course}`
- **Data extracted:** title, channel, duration, level, link
- **Use case:** Recommend courses to users based on job gaps

### 4. **YouTube** (Course/video recommendations)
- **URL pattern:** `https://www.youtube.com/results?search_query={course}`
- **Data extracted:** title, channel, channel_link, link
- **Use case:** Recommend YouTube playlists for skill-building

---

## Architecture

### Webdriver Management

**File:** `webdriver.py`

```python
def get_web_driver():
    """
    Returns a Chrome WebDriver configured for:
    - Container environments (Docker, Kubernetes)
    - Development vs production modes
    - Headless execution in production
    """
    options = Options()
    
    # Detect if running in container
    if running_in_container():  # /.dockerenv or /run/.containerenv
        options.binary_location = "/usr/bin/chromium"
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    
    # Headless only in production
    if not DEV_MODE:  # From configs
        options.add_argument("--headless=new")
    
    return WebDriver(options=options)
```

**Why this approach?**
- Container detection allows same code to run locally and in Docker
- `--no-sandbox` prevents permission issues in containers
- `--disable-dev-shm-usage` avoids shared memory exhaustion
- Development mode shows browser for debugging

---

## Implementation

### 1. Naukri Job Scraper

**File:** `naukri.py`

**Function signature:**
```python
def parse(job_name: str, driver: WebDriver) -> list[dict]:
    """
    Scrapes Naukri for jobs matching job_name.
    Returns list of job dicts with full details.
    """
```

**Usage:**
```python
from selenium.webdriver import Chrome
from scrapers.naukri import parse

driver = Chrome()
jobs = parse("Backend Developer", driver)
# Returns:
# [
#   {
#       "name": "Senior Backend Developer",
#       "company": "TCS",
#       "location": "Bangalore, India",
#       "salary": None,  # Naukri salary is unstructured
#       "link": "https://www.naukri.com/job-details/...",
#       "description": "Building scalable systems... 5+ years experience...",
#       "time": "2026-01-15T12:00:00+00:00"
#   },
#   ...
# ]
driver.quit()
```

**Key features:**
```python
# Pagination loop
page_no = 1
while count < LIMIT:
    job_list = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
    
    for job in job_list:
        # Extract title
        name = job.find_element(By.CLASS_NAME, "title").text
        
        # Extract link
        link = job.find_element(By.CLASS_NAME, "title").get_attribute("href")
        
        # Extract company
        company = job.find_element(By.CLASS_NAME, "comp-name").text
        
        # Add to results
        jobs.append({...})
        count += 1
    
    # Navigate to next page
    next_page = driver.find_element(By.ID, "lastCompMark").find_elements(
        By.XPATH, "//*[contains(text(), 'Next')]"
    )
    if next_page:
        page_no += 1
        driver.get(url + "-" + str(page_no))

# Fetch full descriptions from each job's detail page
for job in jobs:
    job["location"], job["description"] = get_job_details(driver, job["link"])
```

**Configuration:**
- `MIN_JOB_LIMIT` — Stop scraping after collecting this many jobs (e.g., 100)

---

### 2. Simply Hired Job Scraper

**File:** `simplyhired.py`

**Function signature:**
```python
def parse(job_name: str, driver: WebDriver) -> list[dict]:
    """
    Scrapes Simply Hired for jobs matching job_name.
    Returns list of job dicts with salary (parsed).
    """
```

**Usage:**
```python
from webdriver import get_web_driver
from scrapers.simplyhired import parse

driver = get_web_driver()
jobs = parse("Full Stack Developer", driver)
# Returns:
# [
#   {
#       "name": "Full Stack Developer",
#       "company": "Startup XYZ",
#       "location": "Bangalore",
#       "salary": 75000,  # Parsed from "₹75,000 a month"
#       "link": "https://www.simplyhired.co.in/job/...",
#       "description": "We are looking for...",
#       "time": "2026-01-15T12:00:00+00:00"
#   },
#   ...
# ]
driver.quit()
```

**Key features:**

**Salary parsing:**
```python
def get_salary(salary_text: str) -> int:
    """
    Converts "From ₹50,000 a month" or "Up to ₹1,20,000 a year" to monthly int.
    """
    # Remove "From" / "Up to"
    salary_text = salary_text.replace("From", "").replace("Up to", "")
    
    # Split "50,000 a month" → ("50,000", "month")
    salary_info, month_or_year = salary_text.split(" a ")
    
    # Parse salary "50,000" → 50000.0
    salary = float(salary_info.replace(",", "").replace("₹", ""))
    
    # Handle ranges: "50,000-60,000" → average
    if "-" in salary_info:
        salary = sum([float(sal) for sal in salary_info.split("-")]) / 2
    
    # Convert year to month
    if month_or_year == "year":
        salary /= 12
    
    return int(salary)
```

**Job element clicking with staleness wait:**
```python
for job in job_list:
    job.click()
    
    # Wait for old description to disappear (page dynamically updated)
    if prev_job_description:
        WebDriverWait(driver, 10).until(EC.staleness_of(prev_job_description))
    
    # Wait for new description to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "[data-testid='viewJobBodyJobFullDescriptionContent']"
        ))
    )
    
    # Extract details
    prev_job_description = driver.find_element(By.CSS_SELECTOR, "...")
```

---

### 3. EDX Course Scraper

**File:** `edx_scrape.py`

**Function signature:**
```python
def parse(driver: WebDriver, name: str) -> list[dict]:
    """
    Scrapes EDX courses for a given search query.
    Returns course metadata for skill recommendations.
    """
```

**Usage:**
```python
from webdriver import get_web_driver
from scrapers.edx_scrape import parse

driver = get_web_driver()
courses = parse(driver, "Python")
# Returns:
# [
#   {
#       "title": "Introduction to Python Programming",
#       "channel": "MIT",
#       "channel_link": "https://www.edx.org/school/mitx",
#       "duration": "12 weeks",
#       "level": "Beginner",
#       "link": "https://www.edx.org/course/..."
#   },
#   ...
# ]
driver.quit()
```

**Deduplication:**
```python
course_links = set()  # Track seen links

for card in cards:
    if card.find_element(By.TAG_NAME, "a").get_attribute("href") not in course_links:
        course_details = get_course_details(card)
        courses.append(course_details)
        course_links.add(course_details.get("link"))
```

---

### 4. YouTube Course Scraper (Async)

**File:** `youtube_video_scrape.py`

**Function signature:**
```python
async def scrape_youtube_videos(name: str) -> list[str]:
    """
    Async scrape YouTube videos (playlists).
    Returns list of embedded video links (top 4).
    """
```

**Usage:**
```python
import asyncio
from scrapers.youtube_video_scrape import scrape_youtube_videos

# Async usage
videos = await scrape_youtube_videos("Python tutorials")
# Returns: ["https://www.youtube.com/embed/...", ...]

# Or with asyncio.run()
videos = asyncio.run(scrape_youtube_videos("Python tutorials"))
```

**Why async?**
- Non-blocking — doesn't freeze the Flask/FastAPI app
- Can scrape multiple videos in parallel
- Returns embedded links ready for frontend display

---

## Integration with Antigravity

### Option 1: Replace BeautifulSoup Scraper

**Current (BeautifulSoup only):**
```python
# app/services/job_scraper.py
def search_jobs(keywords, location=''):
    jobs = []
    query = keywords.replace(' ', '+')
    url = f'https://www.indeed.com/jobs?q={query}&l={location}'
    
    response = requests.get(url, headers={'User-Agent': '...'})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Limited to static HTML
    cards = soup.select('div.job_seen_beacon')[:20]
    for card in cards:
        jobs.append({...})
    
    return jobs
```

**Updated (with Selenium):**
```python
# app/services/job_scraper.py
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from scrapers.naukri import parse as parse_naukri
from scrapers.simplyhired import parse as parse_simplyhired

def search_jobs(keywords, location='India', platforms=['naukri', 'simplyhired']):
    """
    Search jobs from multiple platforms.
    """
    all_jobs = []
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    driver = Chrome(options=options)
    
    try:
        if 'naukri' in platforms:
            naukri_jobs = parse_naukri(keywords, driver)
            all_jobs.extend(naukri_jobs)
        
        if 'simplyhired' in platforms:
            simplyhired_jobs = parse_simplyhired(keywords, driver)
            all_jobs.extend(simplyhired_jobs)
    
    finally:
        driver.quit()
    
    # Merge, deduplicate by link, sort by time
    unique_jobs = {job['link']: job for job in all_jobs}
    return list(unique_jobs.values())
```

### Option 2: Async with FastAPI

```python
# app/routes/jobs.py
from fastapi import APIRouter
from scrapers.youtube_video_scrape import scrape_youtube_videos

router = APIRouter()

@router.get('/jobs/search')
async def search_jobs(keywords: str, location: str = 'India'):
    """
    Async endpoint that scrapes jobs without blocking.
    """
    jobs = await search_jobs_async(keywords, location)
    return {'jobs': jobs, 'count': len(jobs)}

async def search_jobs_async(keywords, location):
    """
    Run Selenium scrapers in thread pool (doesn't block event loop).
    """
    from fastapi.concurrency import run_in_threadpool
    from scrapers.naukri import parse as parse_naukri
    
    jobs = await run_in_threadpool(
        parse_naukri,
        keywords
    )
    return jobs
```

### Option 3: Background Task with Celery

```python
# app/tasks.py
from celery import shared_task
from scrapers.naukri import parse as parse_naukri
from app.db import get_db
from bson import ObjectId
from datetime import datetime

@shared_task
def scrape_and_store_jobs(user_id, keywords):
    """
    Background task: scrape jobs and store in MongoDB.
    """
    from webdriver import get_web_driver
    
    driver = get_web_driver()
    try:
        jobs = parse_naukri(keywords, driver)
        
        # Store in MongoDB
        db = get_db()
        db.scraped_jobs.insert_many({
            'user_id': ObjectId(user_id),
            'job_data': job,
            'scraped_at': datetime.utcnow()
        } for job in jobs)
        
        return {'status': 'success', 'count': len(jobs)}
    
    finally:
        driver.quit()

# Call from Flask route
from app.tasks import scrape_and_store_jobs

@app.route('/jobs/scrape', methods=['POST'])
@login_required
def trigger_scrape():
    keywords = request.form.get('keywords')
    scrape_and_store_jobs.delay(current_user.id, keywords)
    return {'status': 'Scraping started in background'}
```

---

## Configuration

### Environment Variables (.env)

```
# Selenium
SELENIUM_HEADLESS=true
DEV_MODE=false

# Job scraping limits
MIN_JOB_LIMIT=100  # Stop after 100 jobs per platform

# Timeouts
SELENIUM_TIMEOUT=10  # seconds to wait for element

# Platforms to scrape
ACTIVE_JOB_PLATFORMS=naukri,simplyhired
```

### Docker Support

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install Chromium and dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

The webdriver detects `/.dockerenv` and automatically uses the system Chromium.

---

## Error Handling

### Common Issues & Solutions

| Issue | Cause | Solution |
|---|---|---|
| `TimeoutException` | Element not found within 10s | Increase `WebDriverWait(driver, 20)` timeout |
| `StaleElementReferenceException` | Element became stale after DOM update | Use `EC.staleness_of()` before re-querying |
| `NoSuchElementException` | Selector changed in website update | Update CSS selector in parser |
| Chromium not found in container | Missing `chromium` package | Install in Dockerfile |
| Memory exhaustion | Too many driver instances | Always call `driver.quit()` in finally block |
| CAPTCHA blocks scraping | Bot detection triggered | Add random delays, rotate User-Agent |

### Resilient Code Pattern

```python
def parse_with_retry(job_name: str, max_retries=3):
    """Retry scraping if it fails."""
    from webdriver import get_web_driver
    from scrapers.naukri import parse as parse_naukri
    
    for attempt in range(max_retries):
        driver = None
        try:
            driver = get_web_driver()
            jobs = parse_naukri(job_name, driver)
            return jobs
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            import time
            time.sleep(2 ** attempt)  # Exponential backoff
        
        finally:
            if driver:
                driver.quit()
```

---

## Performance Considerations

### Benchmarks

| Platform | Jobs/minute | Avg time/job | Memory |
|---|---|---|---|
| Naukri (100 jobs) | 5–10 | 6–12s | 150–200 MB |
| Simply Hired (100 jobs) | 8–15 | 4–8s | 120–180 MB |
| EDX (20 courses) | 20–40 | 1.5–3s | 80–120 MB |
| YouTube (4 videos) | 30–60 | 0.5–1s | 60–100 MB |

### Optimization Tips

**1. Parallel scraping (multiple drivers):**
```python
from concurrent.futures import ThreadPoolExecutor

def scrape_multiple(keywords):
    with ThreadPoolExecutor(max_workers=2) as executor:
        naukri_jobs = executor.submit(parse_naukri, keywords)
        simplyhired_jobs = executor.submit(parse_simplyhired, keywords)
        return naukri_jobs.result() + simplyhired_jobs.result()
```

**2. Request pooling (reuse single driver):**
```python
# Instead of creating driver per search, reuse
class JobScraper:
    def __init__(self):
        self.driver = get_web_driver()
    
    def search(self, keywords):
        return parse_naukri(keywords, self.driver)
    
    def __del__(self):
        self.driver.quit()
```

**3. Caching results:**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class JobCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, keywords):
        if keywords in self.cache:
            cached_jobs, timestamp = self.cache[keywords]
            if datetime.now() - timestamp < self.ttl:
                return cached_jobs
        return None
    
    def set(self, keywords, jobs):
        self.cache[keywords] = (jobs, datetime.now())

cache = JobCache(ttl_seconds=1800)

def search_jobs(keywords):
    # Check cache first
    if cached := cache.get(keywords):
        return cached
    
    # Scrape if not cached
    jobs = scrape_naukri(keywords)
    cache.set(keywords, jobs)
    return jobs
```

---

## Data Schema

### Job Scrape Schema (Pydantic)

```python
# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobScrape(BaseModel):
    name: str  # Job title
    company: str  # Company name
    location: Optional[str] = None
    salary: Optional[int] = None  # Monthly salary in rupees
    link: str  # Job posting URL
    description: Optional[str] = None
    time: datetime  # When scraped
    platform: Optional[str] = None  # "naukri", "simplyhired", etc.
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Senior Backend Developer",
                "company": "TCS",
                "location": "Bangalore, India",
                "salary": 150000,
                "link": "https://www.naukri.com/...",
                "description": "5+ years experience...",
                "time": "2026-01-15T12:00:00Z",
                "platform": "naukri"
            }
        }
```

### MongoDB Collection

```json
db.scraped_jobs = [
    {
        "_id": ObjectId("..."),
        "name": "Senior Backend Developer",
        "company": "TCS",
        "location": "Bangalore, India",
        "salary": 150000,
        "link": "https://www.naukri.com/...",
        "description": "Building microservices...",
        "time": ISODate("2026-01-15T12:00:00Z"),
        "platform": "naukri",
        "scraped_at": ISODate("2026-01-15T12:00:00Z")
    }
]
```

---

## Testing

### Unit Tests

```python
# tests/test_naukri_scraper.py
import pytest
from scrapers.naukri import parse, get_job_details
from webdriver import get_web_driver

@pytest.fixture
def driver():
    d = get_web_driver()
    yield d
    d.quit()

def test_parse_returns_list(driver):
    jobs = parse("Python Developer", driver)
    assert isinstance(jobs, list)
    assert len(jobs) > 0

def test_job_has_required_fields(driver):
    jobs = parse("Python Developer", driver)
    required = ['name', 'company', 'link', 'time']
    for job in jobs:
        for field in required:
            assert field in job
            assert job[field] is not None

def test_salary_parsing():
    from simplyhired import get_salary
    assert get_salary("₹50,000 a month") == 50000
    assert get_salary("₹6,00,000 a year") == 50000  # 600,000 / 12
    assert get_salary("₹50,000-60,000 a month") == 55000  # average
```

### Integration Test

```python
# tests/integration/test_job_search.py
async def test_antigravity_job_search():
    from app.routes.jobs import search_jobs_async
    
    jobs = await search_jobs_async("Backend Developer", "India")
    
    assert isinstance(jobs, list)
    assert len(jobs) >= 50  # Should find at least 50 jobs
    
    # Check data quality
    for job in jobs[:5]:
        assert 'name' in job
        assert 'company' in job
        assert 'link' in job
        assert job['link'].startswith('http')
```

---

## API Endpoints (for Antigravity)

```python
# app/routes/jobs.py

@app.route('/jobs/scrape', methods=['POST'])
@login_required
def trigger_scrape():
    """User-initiated job scraping."""
    keywords = request.form.get('keywords')
    location = request.form.get('location', 'India')
    platforms = request.form.getlist('platforms', ['naukri', 'simplyhired'])
    
    # Run async in background
    from celery import current_app
    current_app.send_task(
        'app.tasks.scrape_jobs',
        args=[current_user.id, keywords, location, platforms]
    )
    
    return {'status': 'Scraping started', 'job_id': task.id}

@app.route('/jobs/search')
@login_required
def search_jobs():
    """Fetch scraped jobs from database."""
    keywords = request.args.get('keywords', '')
    db = get_db()
    
    jobs = db.scraped_jobs.find({
        'name': {'$regex': keywords, '$options': 'i'}
    }).limit(50)
    
    return render_template('jobs.html', jobs=list(jobs))
```

---

## Future Enhancements

1. **More job boards:** LinkedIn, Indeed API, Glassdoor, AngelList
2. **Smart scheduling:** Scrape in background at regular intervals
3. **Job matching:** Use NLP to match user resume skills to scraped jobs
4. **Salary trends:** Track salary changes over time
5. **Alert system:** Notify user when matching jobs appear
6. **Geographic filtering:** Scrape jobs for multiple locations
7. **Proxy rotation:** Avoid IP bans with rotating proxies
8. **Rate limiting:** Respectful scraping with delays

---

## References

- **Selenium documentation:** https://www.selenium.dev/documentation/
- **Naukri.com:** https://www.naukri.com/
- **Simply Hired:** https://www.simplyhired.co.in/
- **WebDriver options:** https://chromedriver.chromium.org/capabilities
- **Container setup:** https://github.com/joyzoursky/docker-python-selenium