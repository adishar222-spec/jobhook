"""
YouTubeProvider — fetches course playlists via the YouTube Data API v3.

Requires YOUTUBE_API_KEY in .env / environment.
Returns a list of course dicts with the standard schema.
"""
import logging
import os
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
LIMIT = 20


class YouTubeProvider:
    name = "youtube"
    label = "YouTube"

    @staticmethod
    def fetch(keyword: str, driver=None) -> list[dict]:
        """
        Search YouTube for playlists matching `keyword` using the Data API.
        `driver` is accepted but not used (Selenium not needed).
        """
        api_key = os.getenv("YOUTUBE_API_KEY", "")
        if not api_key:
            logger.error("[YouTubeProvider] YOUTUBE_API_KEY not set in environment.")
            return []

        courses: list[dict] = []

        try:
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "playlist",
                "maxResults": LIMIT,
                "key": api_key,
            }
            resp = requests.get(f"{YOUTUBE_API_BASE}/search", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"[YouTubeProvider] API error: {e}")
            return []

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            playlist_id = item.get("id", {}).get("playlistId", "")
            if not playlist_id:
                continue

            title = snippet.get("title", "Untitled")
            channel = snippet.get("channelTitle", "YouTube")
            description = snippet.get("description", "")
            thumbnail = (
                snippet.get("thumbnails", {})
                .get("high", snippet.get("thumbnails", {}).get("default", {}))
                .get("url", "")
            )
            link = f"https://www.youtube.com/playlist?list={playlist_id}"

            courses.append({
                "title": title,
                "name": title,
                "provider": "YouTube",
                "company": channel,
                "instructor": channel,
                "link": link,
                "description": description,
                "thumbnail": thumbnail,
                "platform": "youtube",
                "scraped_at": datetime.now(timezone.utc),
            })

        logger.info(f"[YouTubeProvider] Done — {len(courses)} playlists fetched via API")
        return courses
