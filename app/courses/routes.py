from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import logging

from .models import ScrapedCourseModel, SavedCourseModel
from ..extensions import mongo
from ..scrapers.course_cache import course_cache, get_scrape_status, set_scrape_status

logger = logging.getLogger(__name__)
courses_bp = Blueprint("courses", __name__)
scraped_model = ScrapedCourseModel()
saved_model = SavedCourseModel()

# ── helpers ────────────────────────────────────────────────────────────────────

def _scrape_worker(keyword: str, platforms: list[str], cache_key: str):
    """
    Runs Selenium scrapers, stores results in MongoDB,
    updates the in-memory cache, then marks the scrape as done.
    """
    from ..scrapers.webdriver import get_driver
    from ..scrapers import edx, youtube

    set_scrape_status(cache_key, "running")
    all_courses: list[dict] = []
    driver = None
    try:
        driver = get_driver()

        if "edx" in platforms:
            try:
                courses = edx.parse(keyword, driver)
                all_courses.extend(courses)
                logger.info(f"[scrape_worker] EDX: {len(courses)} courses")
            except Exception as e:
                logger.error(f"[scrape_worker] EDX failed: {e}")

        if "youtube" in platforms:
            try:
                courses = youtube.parse(keyword, driver)
                all_courses.extend(courses)
                logger.info(f"[scrape_worker] YouTube: {len(courses)} courses")
            except Exception as e:
                logger.error(f"[scrape_worker] YouTube failed: {e}")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # Deduplicate by link before storing
    unique: dict[str, dict] = {c["link"]: c for c in all_courses if c.get("link")}
    deduped = list(unique.values())

    if deduped:
        scraped_model.upsert_many(deduped)

    course_cache.set(cache_key, deduped)
    set_scrape_status(cache_key, "done")
    logger.info(f"[scrape_worker] Finished — {len(deduped)} unique courses for key='{cache_key}'")


# ── endpoints ──────────────────────────────────────────────────────────────────

@courses_bp.route("/scrape", methods=["POST"])
@jwt_required()
def scrape():
    data = request.get_json(silent=True) or {}
    keyword = data.get("keyword", "").strip()
    
    if not keyword:
        return jsonify({"error": "Provide a keyword to search for courses."}), 400

    platforms = data.get("platforms", ["edx", "youtube"])
    if not isinstance(platforms, list):
        platforms = ["edx", "youtube"]

    cache_key = f"{keyword.lower()}::{','.join(sorted(platforms))}"

    # Cache hit
    cached = course_cache.get(cache_key)
    if cached is not None:
        return jsonify({
            "courses": cached,
            "count": len(cached),
            "keyword": keyword,
            "source": "cache",
            "scraping": False,
        }), 200

    # Cache miss
    _scrape_worker(keyword, platforms, cache_key)
    
    scraped_courses = course_cache.get(cache_key) or []

    return jsonify({
        "courses": scraped_courses,
        "count": len(scraped_courses),
        "keyword": keyword,
        "source": "live",
        "scraping": False,
    }), 200


@courses_bp.route("/scrape-status", methods=["GET"])
@jwt_required()
def scrape_status():
    keyword = request.args.get("keyword", "").strip()
    platforms_raw = request.args.get("platforms", "edx,youtube")
    platforms = [p.strip() for p in platforms_raw.split(",")]
    cache_key = f"{keyword.lower()}::{','.join(sorted(platforms))}"

    status = get_scrape_status(cache_key)
    cached = course_cache.get(cache_key) if status == "done" else None

    return jsonify({
        "status": status,
        "courses": cached or [],
        "count": len(cached) if cached else 0,
    }), 200


@courses_bp.route("/search", methods=["GET"])
@jwt_required()
def search():
    query = request.args.get("q", "")
    platform = request.args.get("platform", "all")
    limit = min(int(request.args.get("limit", 20)), 60)

    # Live scraped courses
    scraped_courses = scraped_model.search_scraped(query, platform=platform, limit=limit)

    return jsonify(scraped_courses[:limit]), 200


# ── Saved Courses API ─────────────────────────────────────────────────────────

@courses_bp.route("/saved", methods=["GET"])
@jwt_required()
def get_saved_courses():
    user_id = get_jwt_identity()
    saved_records = saved_model.get_by_user(user_id)
    
    # Enrich with course details
    for record in saved_records:
        if record.get("course_id"):
            course = mongo.db.scraped_courses.find_one({"_id": ObjectId(record["course_id"])})
            if course:
                course["_id"] = str(course["_id"])
                record["course"] = course
                
    return jsonify(saved_records), 200


@courses_bp.route("/save", methods=["POST"])
@jwt_required()
def save_course():
    user_id = get_jwt_identity()
    data = request.get_json()
    course_id = data.get("course_id")
    
    if not course_id:
        return jsonify({"error": "course_id is required"}), 400
        
    saved_id = saved_model.create(user_id, course_id)
    return jsonify({"message": "Course saved", "saved_id": saved_id}), 201


@courses_bp.route("/saved/<saved_id>", methods=["DELETE"])
@jwt_required()
def delete_saved_course(saved_id):
    user_id = get_jwt_identity()
    saved_model.delete(saved_id, user_id)
    return jsonify({"message": "Saved course removed"}), 200
