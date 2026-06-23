"""
In-memory TTL cache for scraped jobs.
Avoids hitting Selenium on every request within the TTL window.
"""
import threading
from datetime import datetime, timedelta


class JobCache:
    def __init__(self, ttl_seconds: int = 1800):
        self._cache: dict[str, tuple[list, datetime]] = {}
        self._lock = threading.Lock()
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> list | None:
        """Return cached jobs if still fresh, else None."""
        with self._lock:
            if key in self._cache:
                jobs, ts = self._cache[key]
                if datetime.utcnow() - ts < self.ttl:
                    return jobs
        return None

    def set(self, key: str, jobs: list) -> None:
        """Store jobs in cache with current timestamp."""
        with self._lock:
            self._cache[key] = (jobs, datetime.utcnow())

    def is_fresh(self, key: str) -> bool:
        """Check if cache entry exists and is within TTL."""
        with self._lock:
            if key in self._cache:
                _, ts = self._cache[key]
                return datetime.utcnow() - ts < self.ttl
        return False

    def invalidate(self, key: str) -> None:
        """Force-expire a cache entry."""
        with self._lock:
            self._cache.pop(key, None)


# Singleton — shared across the entire Flask app process
job_cache = JobCache(ttl_seconds=1800)

# Track in-flight scrape tasks per role key
_scrape_status: dict[str, str] = {}  # key -> "running" | "done" | "error"
_scrape_lock = threading.Lock()


def get_scrape_status(key: str) -> str:
    """Returns 'idle', 'running', 'done', or 'error'."""
    with _scrape_lock:
        return _scrape_status.get(key, "idle")


def set_scrape_status(key: str, status: str) -> None:
    with _scrape_lock:
        _scrape_status[key] = status
