from ..extensions import mongo
from bson import ObjectId
from datetime import datetime
import bcrypt


class UserModel:
    @property
    def collection(self):
        return mongo.db.users

    def create(self, name, email, password, target_role=""):
        password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()
        user = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "profile": {
                "target_role": target_role,
                "target_industry": "",
                "location": "",
                "experience_years": 0
            },
            "active_resume_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.collection.insert_one(user)
        return result.inserted_id

    def find_by_email(self, email):
        return self.collection.find_one({"email": email})

    def find_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def update_profile(self, user_id, profile_data):
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile": profile_data, "updated_at": datetime.utcnow()}}
        )
