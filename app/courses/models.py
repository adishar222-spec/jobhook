from ..extensions import mongo
from bson import ObjectId
from datetime import datetime

class ScrapedCourseModel:
    @property
    def col(self):
        return mongo.db.scraped_courses

    def ensure_indexes(self):
        """Call once at app startup to create unique index on link."""
        self.col.create_index("link", unique=True, background=True)
        self.col.create_index("platform", background=True)
        self.col.create_index("scraped_at", background=True)

    def upsert_many(self, courses: list[dict]) -> int:
        """
        Upsert courses by their `link` field to avoid duplicates.
        Returns count of inserted/updated documents.
        """
        count = 0
        for course in courses:
            link = course.get("link")
            if not link:
                continue
            # Convert datetime for Mongo compatibility
            course["scraped_at"] = course.get("scraped_at", datetime.utcnow())
            try:
                self.col.update_one(
                    {"link": link},
                    {"$set": course},
                    upsert=True,
                )
                count += 1
            except Exception:
                pass
        return count

    def search_scraped(self, query: str, platform: str = "", limit: int = 40) -> list:
        """Search scraped_courses by title or description, optionally filtered by platform."""
        filters: dict = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ]
        }
        if platform and platform != "all":
            filters["platform"] = platform

        courses = list(self.col.find(filters).sort("scraped_at", -1).limit(limit))
        for c in courses:
            c["_id"] = str(c["_id"])
        return courses


class SavedCourseModel:
    @property
    def col(self):
        return mongo.db.saved_courses

    def get_by_user(self, user_id: str) -> list:
        records = list(self.col.find({"user_id": user_id}).sort("saved_at", -1))
        for r in records:
            r["_id"] = str(r["_id"])
            if "course_id" in r:
                r["course_id"] = str(r["course_id"])
        return records

    def create(self, user_id: str, course_id: str) -> str:
        record = {
            "user_id": user_id,
            "course_id": ObjectId(course_id) if course_id else None,
            "saved_at": datetime.utcnow()
        }
        # Avoid duplicate saves
        existing = self.col.find_one({"user_id": user_id, "course_id": ObjectId(course_id)})
        if existing:
            return str(existing["_id"])
            
        result = self.col.insert_one(record)
        return str(result.inserted_id)

    def delete(self, saved_id: str, user_id: str):
        self.col.delete_one({"_id": ObjectId(saved_id), "user_id": user_id})
