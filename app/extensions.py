from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId
from datetime import datetime

class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

mongo = PyMongo()
jwt = JWTManager()
cors = CORS()
