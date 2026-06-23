from datetime import datetime, timedelta
import threading

class CourseCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
        self.ttl = timedelta(hours=24)
        
        self.status = {}

    def get(self, key: str):
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if datetime.utcnow() < item["expires"]:
                    return item["courses"]
                else:
                    del self.cache[key]
            return None

    def set(self, key: str, courses: list):
        with self.lock:
            self.cache[key] = {
                "courses": courses,
                "expires": datetime.utcnow() + self.ttl
            }

course_cache = CourseCache()

def set_scrape_status(key: str, status: str):
    course_cache.status[key] = status

def get_scrape_status(key: str) -> str:
    return course_cache.status.get(key, "idle")
