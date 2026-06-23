from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .groq_client import GroqClient
from ..resume.models import ResumeModel

suggestions_bp = Blueprint("suggestions", __name__)
groq = GroqClient()
resume_model = ResumeModel()

@suggestions_bp.route("/improve", methods=["POST"])
@jwt_required()
def improve_resume():
    """Endpoint to get targeted improvements for a specific job."""
    data = request.get_json()
    resume_id = data.get("resume_id")
    job_description = data.get("job_description", "")
    
    if not resume_id or not job_description:
        return jsonify({"error": "resume_id and job_description required"}), 400
        
    resume = resume_model.get_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
        
    # Get general suggestions
    suggestions = groq.get_resume_suggestions(
        resume_text=resume.get("raw_text", ""),
        jd_text=job_description,
        missing_keywords=[],
        score=0
    )
    
    return jsonify({"suggestions": suggestions}), 200
