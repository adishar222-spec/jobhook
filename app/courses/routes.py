from flask import Blueprint, request, jsonify
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

ALL_PROVIDERS = ["edx", "youtube"]

# ── helpers ────────────────────────────────────────────────────────────────────

def _run_provider(name: str, keyword: str, driver) -> list[dict]:
    """Instantiate the correct provider and call fetch()."""
    from ..scrapers.providers import PROVIDERS
    cls = PROVIDERS.get(name)
    if not cls:
        logger.warning(f"[courses] Unknown provider: {name}")
        return []
    try:
        results = cls.fetch(keyword, driver)
        logger.info(f"[courses] {cls.label}: {len(results)} courses")
        return results
    except Exception as e:
        logger.error(f"[courses] Provider '{name}' failed: {e}")
        return []


def _scrape_worker(keyword: str, platforms: list[str], cache_key: str):
    """
    Runs each requested provider, stores results in MongoDB,
    then marks scrape as done in cache.
    """
    set_scrape_status(cache_key, "running")
    all_courses: list[dict] = []

    # EDX needs Selenium; YouTube uses the Data API
    selenium_providers = [p for p in platforms if p == "edx"]
    api_providers = [p for p in platforms if p != "edx"]

    driver = None
    try:
        if selenium_providers:
            from ..scrapers.webdriver import get_driver
            driver = get_driver()

        for p in selenium_providers:
            all_courses.extend(_run_provider(p, keyword, driver))

        for p in api_providers:
            all_courses.extend(_run_provider(p, keyword, None))

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # Deduplicate by link
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

    platforms = data.get("platforms", ALL_PROVIDERS)
    if not isinstance(platforms, list):
        platforms = ALL_PROVIDERS
    # Sanitize — only accept known providers
    platforms = [p for p in platforms if p in ALL_PROVIDERS] or ALL_PROVIDERS

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

    # Cache miss — run synchronously (Chrome opens for edX if in list)
    _scrape_worker(keyword, platforms, cache_key)
    scraped_courses = course_cache.get(cache_key) or []

    return jsonify({
        "courses": scraped_courses,
        "count": len(scraped_courses),
        "keyword": keyword,
        "source": "live",
        "scraping": False,
    }), 200


@courses_bp.route("/providers", methods=["GET"])
@jwt_required()
def list_providers():
    """Return available provider names and labels."""
    from ..scrapers.providers import PROVIDERS
    return jsonify([
        {"name": name, "label": cls.label}
        for name, cls in PROVIDERS.items()
    ]), 200


@courses_bp.route("/search", methods=["GET"])
@jwt_required()
def search():
    query = request.args.get("q", "")
    platform = request.args.get("platform", "all")
    limit = min(int(request.args.get("limit", 20)), 60)
    scraped_courses = scraped_model.search_scraped(query, platform=platform, limit=limit)
    return jsonify(scraped_courses[:limit]), 200


# ── Saved Courses API ─────────────────────────────────────────────────────────

@courses_bp.route("/saved", methods=["GET"])
@jwt_required()
def get_saved_courses():
    user_id = get_jwt_identity()
    saved_records = saved_model.get_by_user(user_id)
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
