from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import threading
import logging

from .recommender import get_recommendations
from .models import ScrapedJobModel
from ..extensions import mongo
from ..scrapers.job_cache import job_cache, get_scrape_status, set_scrape_status

logger = logging.getLogger(__name__)
jobs_bp = Blueprint("jobs", __name__)
scraped_model = ScrapedJobModel()


# ── helpers ────────────────────────────────────────────────────────────────────

def _scrape_worker(role: str, platforms: list[str], cache_key: str):
    """
    Background thread: runs Selenium scrapers, stores results in MongoDB,
    updates the in-memory cache, then marks the scrape as done.
    """
    from ..scrapers.webdriver import get_driver
    from ..scrapers import naukri, simplyhired

    set_scrape_status(cache_key, "running")
    all_jobs: list[dict] = []
    driver = None
    try:
        driver = get_driver()

        if "naukri" in platforms:
            try:
                jobs = naukri.parse(role, driver)
                all_jobs.extend(jobs)
                logger.info(f"[scrape_worker] Naukri: {len(jobs)} jobs")
            except Exception as e:
                logger.error(f"[scrape_worker] Naukri failed: {e}")

        if "simplyhired" in platforms:
            try:
                jobs = simplyhired.parse(role, driver)
                all_jobs.extend(jobs)
                logger.info(f"[scrape_worker] SimplyHired: {len(jobs)} jobs")
            except Exception as e:
                logger.error(f"[scrape_worker] SimplyHired failed: {e}")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # Deduplicate by link before storing
    unique: dict[str, dict] = {j["link"]: j for j in all_jobs if j.get("link")}
    deduped = list(unique.values())

    if deduped:
        scraped_model.upsert_many(deduped)

    job_cache.set(cache_key, deduped)
    set_scrape_status(cache_key, "done")
    logger.info(f"[scrape_worker] Finished — {len(deduped)} unique jobs for key='{cache_key}'")


# ── endpoints ──────────────────────────────────────────────────────────────────

@jobs_bp.route("/scrape", methods=["POST"])
@jwt_required()
def scrape():
    """
    POST /api/jobs/scrape
    Body: { "role": "...", "platforms": ["naukri","simplyhired"] }

    If cache is fresh → returns cached jobs immediately.
    If cache is stale → launches background thread, returns DB results + scraping=true.
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    # Resolve role: request body → user profile fallback
    role = data.get("role", "").strip()
    if not role:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        role = (user or {}).get("profile", {}).get("target_role", "")
    if not role:
        return jsonify({"error": "Provide a role or set a target role in your profile."}), 400

    platforms = data.get("platforms", ["naukri", "simplyhired"])
    if not isinstance(platforms, list):
        platforms = ["naukri", "simplyhired"]

    cache_key = f"{role.lower()}::{','.join(sorted(platforms))}"

    # ── Cache hit ──────────────────────────────────────────────────────────────
    cached = job_cache.get(cache_key)
    if cached is not None:
        return jsonify({
            "jobs": cached,
            "count": len(cached),
            "role": role,
            "source": "cache",
            "scraping": False,
        }), 200

    # ── Cache miss — run scrape in MAIN THREAD for visibility ────────────
    _scrape_worker(role, platforms, cache_key)
    
    # After worker finishes, get the newly fetched jobs
    scraped_jobs = job_cache.get(cache_key) or []

    return jsonify({
        "jobs": scraped_jobs,
        "count": len(scraped_jobs),
        "role": role,
        "source": "live",
        "scraping": False,
    }), 200


@jobs_bp.route("/scrape-status", methods=["GET"])
@jwt_required()
def scrape_status():
    """
    GET /api/jobs/scrape-status?role=...&platforms=naukri,simplyhired

    Returns { status: "idle"|"running"|"done"|"error", jobs: [...] }
    Frontend polls this every 5 s after triggering a scrape.
    """
    role = request.args.get("role", "").strip()
    platforms_raw = request.args.get("platforms", "naukri,simplyhired")
    platforms = [p.strip() for p in platforms_raw.split(",")]
    cache_key = f"{role.lower()}::{','.join(sorted(platforms))}"

    status = get_scrape_status(cache_key)
    cached = job_cache.get(cache_key) if status == "done" else None

    return jsonify({
        "status": status,
        "jobs": cached or [],
        "count": len(cached) if cached else 0,
    }), 200


@jobs_bp.route("/search", methods=["GET"])
@jwt_required()
def search():
    """
    GET /api/jobs/search?q=...&platform=all|naukri|simplyhired&limit=20

    Merges results from static `jobs` collection + live `scraped_jobs` collection.
    """
    query = request.args.get("q", "")
    platform = request.args.get("platform", "all")
    limit = min(int(request.args.get("limit", 20)), 60)

    # Static jobs (seeded/admin)
    static_jobs = []
    if platform in ("all",):
        static_jobs = list(mongo.db.jobs.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ],
            "is_active": True
        }).limit(limit))
        for j in static_jobs:
            j["_id"] = str(j["_id"])
            j.setdefault("platform", "db")

    # Live scraped jobs
    scraped_jobs = scraped_model.search_scraped(query, platform=platform, limit=limit)

    # Merge, dedup by link
    seen_links: set[str] = set()
    merged = []
    for job in static_jobs + scraped_jobs:
        link = job.get("link", "") or job.get("apply_url", "")
        if link not in seen_links:
            seen_links.add(link)
            merged.append(job)

    return jsonify(merged[:limit]), 200


@jobs_bp.route("/recommend", methods=["GET"])
@jwt_required()
def recommend():
    user_id = get_jwt_identity()
    resume_id = request.args.get("resume_id")

    if not resume_id:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user and user.get("active_resume_id"):
            resume_id = str(user["active_resume_id"])
        else:
            return jsonify({"error": "resume_id is required"}), 400

    limit = int(request.args.get("limit", 10))
    recommendations = get_recommendations(user_id, resume_id, limit)
    return jsonify(recommendations), 200
