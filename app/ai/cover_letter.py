from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .groq_client import GroqClient
from ..resume.models import ResumeModel
from ..extensions import mongo
from bson import ObjectId
from datetime import datetime

cover_letter_bp = Blueprint("cover_letter", __name__)
groq = GroqClient()
resume_model = ResumeModel()


@cover_letter_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    user_id = get_jwt_identity()
    data = request.get_json()

    resume_id = data.get("resume_id")
    resume = resume_model.get_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    parsed = resume.get("parsed", {})
    achievements = [
        bullet
        for exp in parsed.get("experience", [])
        for bullet in exp.get("bullets", [])[:2]
    ]

    letter_text = groq.generate_cover_letter(
        name=parsed.get("name", ""),
        role=data.get("role", ""),
        company=data.get("company", ""),
        skills=parsed.get("skills", []),
        achievements=achievements,
        jd_text=data.get("job_description", "")
    )

    # Save to DB
    doc = {
        "user_id": ObjectId(user_id),
        "resume_id": ObjectId(resume_id),
        "company": data.get("company", ""),
        "role": data.get("role", ""),
        "content": letter_text,
        "version": 1,
        "created_at": datetime.utcnow()
    }
    result = mongo.db.cover_letters.insert_one(doc)

    return jsonify({
        "cover_letter_id": str(result.inserted_id),
        "content": letter_text
    }), 201


@cover_letter_bp.route("/", methods=["GET"])
@jwt_required()
def list_cover_letters():
    user_id = get_jwt_identity()
    letters = list(mongo.db.cover_letters.find({"user_id": ObjectId(user_id)}))
    for l in letters:
        l["_id"] = str(l["_id"])
        l["user_id"] = str(l["user_id"])
        l["resume_id"] = str(l["resume_id"])
    return jsonify(letters), 200
