from ..extensions import mongo
from bson import ObjectId
from datetime import datetime


class ApplicationModel:
    @property
    def col(self):
        return mongo.db.applications

    def create(self, user_id, job_id, resume_id, cover_letter_id=None,
               ats_score=0, notes="") -> str:
        doc = {
            "user_id": ObjectId(user_id),
            "job_id": ObjectId(job_id) if job_id else None,
            "resume_id": ObjectId(resume_id) if resume_id else None,
            "cover_letter_id": ObjectId(cover_letter_id) if cover_letter_id else None,
            "status": "saved",
            "ats_score": ats_score,
            "notes": notes,
            "applied_at": None,
            "next_follow_up": None,
            "selenium_session": {},
            "timeline": [{"status": "saved", "at": datetime.utcnow()}],
            "updated_at": datetime.utcnow()
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def update_status(self, app_id: str, status: str):
        self.col.update_one(
            {"_id": ObjectId(app_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                },
                "$push": {
                    "timeline": {"status": status, "at": datetime.utcnow()}
                }
            }
        )

    def update_selenium_result(self, app_id: str, result: dict):
        update = {
            "selenium_session": {
                **result,
                "attempted": True,
                "applied_at": datetime.utcnow()
            },
            "updated_at": datetime.utcnow()
        }
        if result.get("success"):
            update["status"] = "applied"
            update["applied_at"] = datetime.utcnow()
        self.col.update_one({"_id": ObjectId(app_id)}, {"$set": update})

    def get_by_user(self, user_id: str) -> list:
        apps = list(self.col.find({"user_id": ObjectId(user_id)}).sort("updated_at", -1))
        for a in apps:
            a["_id"] = str(a["_id"])
            a["user_id"] = str(a["user_id"])
            if a.get("job_id"):
                a["job_id"] = str(a["job_id"])
            if a.get("resume_id"):
                a["resume_id"] = str(a["resume_id"])
            if a.get("cover_letter_id"):
                a["cover_letter_id"] = str(a["cover_letter_id"])
        return apps

    def delete(self, app_id: str, user_id: str):
        self.col.delete_one({"_id": ObjectId(app_id), "user_id": ObjectId(user_id)})
