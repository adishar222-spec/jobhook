from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .driver import get_driver
from .sites.linkedin import LinkedInApplier
from ..tracker.models import ApplicationModel
from ..extensions import mongo
from bson import ObjectId
import threading
import os

apply_bp = Blueprint("apply", __name__)
app_model = ApplicationModel()

# Thread-local driver storage (one session per user ideally)
_sessions = {}


@apply_bp.route("/prepare", methods=["POST"])
@jwt_required()
def prepare_application():
    """
    Prepare application data and show preview to user
    before triggering Selenium.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    return jsonify({
        "preview": {
            "job_url": data.get("job_url"),
            "platform": data.get("platform", "LinkedIn"),
            "resume_name": data.get("resume_name"),
            "cover_letter_preview": data.get("cover_letter_text", "")[:300] + "...",
        },
        "message": "Please review the details above and confirm to proceed."
    }), 200


@apply_bp.route("/confirm", methods=["POST"])
@jwt_required()
def confirm_apply():
    """
    User has confirmed — trigger Selenium auto-apply in background thread.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    job_url = data.get("job_url")
    resume_path = data.get("resume_path")
    platform = data.get("platform", "linkedin").lower()
    application_id = data.get("application_id")

    # Resolve resume if not provided
    if not resume_path:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user and user.get("active_resume_id"):
            resume = mongo.db.resumes.find_one({"_id": user["active_resume_id"]})
            if resume:
                resume_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes", resume["storage_name"])

    applicant_data = {
        "phone": data.get("phone", ""),
        "name": user.get("name", "") if 'user' in locals() else data.get("name", ""),
        "email": user.get("email", "") if 'user' in locals() else data.get("email", "")
    }

    screenshot_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "screenshots")

    def run_apply():
        driver = get_driver(headless=False)
        try:
            if platform == "linkedin":
                applier = LinkedInApplier(driver)
                result = applier.apply(job_url, applicant_data, resume_path, screenshot_dir)
            else:
                result = {"success": False, "error": f"Platform '{platform}' not yet supported"}

            # Update application tracker
            if application_id:
                app_model.update_selenium_result(application_id, result)
        finally:
            driver.quit()

    thread = threading.Thread(target=run_apply, daemon=True)
    thread.start()

    return jsonify({
        "message": "Application submission started. Check your tracker for results.",
        "application_id": application_id
    }), 202
