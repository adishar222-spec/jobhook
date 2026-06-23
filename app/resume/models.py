from ..extensions import mongo
from bson import ObjectId
from datetime import datetime


class ResumeModel:
    @property
    def collection(self):
        return mongo.db.resumes

    def create(self, user_id, file_name, storage_name, raw_text, parsed):
        resume = {
            "user_id": ObjectId(user_id),
            "file_name": file_name,
            "storage_name": storage_name,
            "raw_text": raw_text,
            "parsed": parsed,
            "ats_scores": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.collection.insert_one(resume)
        
        # Sync parsed resume data to user profile
        profile_update = {
            "profile.location": parsed.get("location", ""),
            "profile.summary": parsed.get("summary", ""),
            "profile.skills": parsed.get("skills", []),
            "profile.experience": parsed.get("experience", []),
            "profile.education": parsed.get("education", []),
            "profile.projects": parsed.get("projects", []),
            "profile.certificates": parsed.get("certificates", []),
            "profile.courses": parsed.get("courses", []),
            "profile.languages": parsed.get("languages", []),
            "profile.interests": parsed.get("interests", []),
            "profile.linkedin": parsed.get("linkedin", ""),
            "profile.portfolio": parsed.get("portfolio", ""),
            "active_resume_id": result.inserted_id,
            "updated_at": datetime.utcnow()
        }

        # If name is present and user doesn't have a name or it's just a generic one, update it
        if parsed.get("name"):
            profile_update["name"] = parsed["name"]

        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": profile_update}
        )
        
        return result.inserted_id

    def get_by_user(self, user_id):
        resumes = list(self.collection.find({"user_id": ObjectId(user_id)}))
        for r in resumes:
            r["_id"] = str(r["_id"])
            r["user_id"] = str(r["user_id"])
            for score in r.get("ats_scores", []):
                if "_id" in score:
                    score["_id"] = str(score["_id"])
        return resumes

    def get_by_id(self, resume_id):
        return self.collection.find_one({"_id": ObjectId(resume_id)})

    def delete(self, resume_id, user_id):
        self.collection.delete_one({
            "_id": ObjectId(resume_id),
            "user_id": ObjectId(user_id)
        })

    def add_ats_score(self, resume_id, score_data):
        score_data["checked_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$push": {"ats_scores": score_data}}
        )
