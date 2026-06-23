from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from .parser import extract_resume_text, extract_email, extract_phone
from .models import ResumeModel
from ..ai.groq_client import GroqClient
import os
import uuid

resume_bp = Blueprint("resume", __name__)
resume_model = ResumeModel()
groq = GroqClient()

ALLOWED = {"pdf", "docx", "doc"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PDF or DOCX"}), 400

    filename = secure_filename(file.filename)
    extension = os.path.splitext(filename)[1]
    storage_name = f"{uuid.uuid4()}{extension}"
    
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes")
    upload_path = os.path.join(upload_dir, storage_name)
    file.save(upload_path)

    # Extract text
    raw_text = extract_resume_text(upload_path)

    # AI-assisted parsing: ask Groq to return structured JSON
    parsed = groq.parse_resume(raw_text)

    resume_id = resume_model.create(
        user_id=user_id,
        file_name=filename,
        storage_name=storage_name,
        raw_text=raw_text,
        parsed=parsed
    )

    return jsonify({
        "message": "Resume uploaded successfully",
        "resume_id": str(resume_id),
        "storage_name": storage_name,
        "parsed": parsed
    }), 201


@resume_bp.route("/view/<filename>", methods=["GET"])
def view_resume(filename):
    """Serve the resume file."""
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes")
    return send_from_directory(upload_dir, filename)


@resume_bp.route("/", methods=["GET"])
@jwt_required()
def get_resumes():
    user_id = get_jwt_identity()
    resumes = resume_model.get_by_user(user_id)
    return jsonify(resumes), 200


@resume_bp.route("/<resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id):
    user_id = get_jwt_identity()
    resume_model.delete(resume_id, user_id)
    return jsonify({"message": "Resume deleted"}), 200
