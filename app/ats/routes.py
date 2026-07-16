from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .scorer import calculate_ats_score
from .skill_gap import analyze_skill_gap
from ..resume.models import ResumeModel
from ..auth.models import UserModel
from ..ai.groq_client import GroqClient

ats_bp = Blueprint("ats", __name__)
resume_model = ResumeModel()
user_model = UserModel()
groq = GroqClient()


@ats_bp.route("/score", methods=["POST"])
@jwt_required()
def score():
    user_id = get_jwt_identity()
    data = request.get_json()

    resume_id = data.get("resume_id")
    jd_text = data.get("job_description", "")

    if not resume_id or not jd_text:
        return jsonify({"error": "resume_id and job_description are required"}), 400

    resume = resume_model.get_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    # ATS Score
    ats_result = calculate_ats_score(resume["raw_text"], jd_text)

    # Skill Gap — prefer user profile skills_list over resume parsed skills
    target_skills = data.get("target_skills", [])
    user_doc = user_model.find_by_id(user_id)
    profile_skills = []
    if user_doc:
        profile = user_doc.get("profile", {})
        skills_list = profile.get("skills_list", [])
        if skills_list:
            profile_skills = [s.get("name", "") for s in skills_list if s.get("name")]
        elif profile.get("skills"):
            profile_skills = profile.get("skills", [])
    if not profile_skills:
        profile_skills = resume.get("parsed", {}).get("skills", [])

    gap_result = analyze_skill_gap(profile_skills, jd_text, target_skills)

    # AI improvement suggestions
    parsed_exp = resume.get("parsed", {}).get("experience", [])
    parsed_prj = resume.get("parsed", {}).get("projects", [])
    suggestions = groq.get_resume_suggestions(
        resume_text=resume["raw_text"],
        jd_text=jd_text,
        missing_keywords=ats_result["missing_keywords"],
        score=ats_result["score"],
        parsed_experience=parsed_exp,
        parsed_projects=parsed_prj
    )

    # Save ATS history to resume
    resume_model.add_ats_score(resume_id, {
        "job_description": jd_text[:500],
        "score": ats_result["score"],
        "matched_keywords": ats_result["matched_keywords"],
        "missing_keywords": ats_result["missing_keywords"]
    })

    return jsonify({
        "ats": ats_result,
        "skill_gap": gap_result,
        "suggestions": suggestions
    }), 200


@ats_bp.route("/apply-changes", methods=["POST"])
@jwt_required()
def apply_changes():
    user_id = get_jwt_identity()
    data = request.get_json()

    resume_id = data.get("resume_id")
    revised_summary = data.get("revised_summary")        # omitted = don't touch
    revised_experience = data.get("revised_experience")  # omitted = don't touch
    missing_keywords = data.get("missing_keywords")      # omitted = don't touch

    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400

    resume = resume_model.get_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    user_doc = user_model.find_by_id(user_id)
    if not user_doc or "profile" not in user_doc:
        return jsonify({"error": "User profile not found"}), 404

    profile = user_doc["profile"]
    resume_set = {}

    # Only update summary if explicitly supplied
    if revised_summary is not None:
        profile["summary"] = revised_summary
        resume_set["parsed.summary"] = revised_summary

    # Only update experience if explicitly supplied
    if revised_experience is not None and isinstance(revised_experience, list):
        profile["experience"] = revised_experience
        resume_set["parsed.experience"] = revised_experience

    # Only update projects if explicitly supplied
    revised_projects = data.get("revised_projects")  # omitted = don't touch
    if revised_projects is not None and isinstance(revised_projects, list):
        profile["projects"] = revised_projects
        resume_set["parsed.projects"] = revised_projects

    # Only update skills if explicitly supplied
    if missing_keywords is not None:
        # Sync into both flat skills list and structured skills_list
        existing_skills = [s.lower() for s in profile.get("skills", [])]
        existing_skills_list_names = [s.get("name", "").lower() for s in profile.get("skills_list", [])]

        new_skills = profile.get("skills", [])
        new_skills_list = profile.get("skills_list", [])

        for kw in missing_keywords:
            if kw.lower() not in existing_skills:
                new_skills.append(kw)
            if kw.lower() not in existing_skills_list_names:
                new_skills_list.append({"name": kw, "level": ""})

        profile["skills"] = new_skills
        profile["skills_list"] = new_skills_list
        resume_set["parsed.skills"] = new_skills
        resume_set["parsed.skills_list"] = new_skills_list

    user_model.update_profile(user_id, profile)

    if resume_set:
        resume_model.collection.update_one(
            {"_id": resume["_id"]},
            {"$set": resume_set}
        )

    return jsonify({"message": "Changes applied successfully"}), 200
