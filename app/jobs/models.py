from ..extensions import mongo
from bson import ObjectId
from datetime import datetime

class JobModel:
    @property
    def col(self):
        return mongo.db.jobs

    def get_by_id(self, job_id: str) -> dict:
        job = self.col.find_one({"_id": ObjectId(job_id)})
        if job:
            job["_id"] = str(job["_id"])
        return job

    def search(self, query: str, limit: int = 20) -> list:
        jobs = list(self.col.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ],
            "is_active": True
        }).limit(limit))
        
        for j in jobs:
            j["_id"] = str(j["_id"])
        return jobs


class ScrapedJobModel:
    @property
    def col(self):
        return mongo.db.scraped_jobs

    def ensure_indexes(self):
        """Call once at app startup to create unique index on link."""
        self.col.create_index("link", unique=True, background=True)
        self.col.create_index("platform", background=True)
        self.col.create_index("scraped_at", background=True)

    def upsert_many(self, jobs: list[dict]) -> int:
        """
        Upsert jobs by their `link` field to avoid duplicates.
        Returns count of inserted/updated documents.
        """
        count = 0
        for job in jobs:
            link = job.get("link")
            if not link:
                continue
            # Convert datetime for Mongo compatibility
            job["scraped_at"] = job.get("scraped_at", datetime.utcnow())
            try:
                self.col.update_one(
                    {"link": link},
                    {"$set": job},
                    upsert=True,
                )
                count += 1
            except Exception:
                pass
        return count

    def search_scraped(self, query: str, platform: str = "", limit: int = 40) -> list:
        """Search scraped_jobs by title or description, optionally filtered by platform."""
        filters: dict = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ]
        }
        if platform and platform != "all":
            filters["platform"] = platform

        jobs = list(self.col.find(filters).sort("scraped_at", -1).limit(limit))
        for j in jobs:
            j["_id"] = str(j["_id"])
        return jobs

    def get_by_role(self, role: str, limit: int = 40) -> list:
        """Get recently scraped jobs matching a role name."""
        jobs = list(self.col.find({
            "$or": [
                {"title": {"$regex": role, "$options": "i"}},
                {"name": {"$regex": role, "$options": "i"}},
            ]
        }).sort("scraped_at", -1).limit(limit))
        for j in jobs:
            j["_id"] = str(j["_id"])
        return jobs
