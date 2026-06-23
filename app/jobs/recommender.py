from ..extensions import mongo
from bson import ObjectId
import re


def score_job_match(resume_skills: list, job: dict) -> int:
    """Skill overlap score between resume skills and job required_skills or description."""
    candidate = [s.lower() for s in resume_skills]
    required = [s.lower() for s in job.get("required_skills", [])]

    # For scraped jobs that have no required_skills, mine keywords from description
    if not required and job.get("description"):
        desc_words = set(re.findall(r'\b[a-zA-Z][a-zA-Z+#.]{2,}\b', job["description"].lower()))
        required = list(desc_words)

    if not required or not candidate:
        return 0
    overlap = len(set(required) & set(candidate))
    return round(min(overlap / max(len(candidate), 1) * 100, 100))


def get_recommendations(user_id: str, resume_id: str, limit: int = 10) -> list:
    """
    Return top job recommendations for a user based on:
    1. Target role match in job title (static jobs AND scraped jobs)
    2. Skill overlap with resume
    """
    from ..resume.models import ResumeModel
    from ..auth.models import UserModel

    user = UserModel().find_by_id(user_id)
    resume = ResumeModel().get_by_id(resume_id)

    target_role = user.get("profile", {}).get("target_role", "") if user else ""
    resume_skills = resume.get("parsed", {}).get("skills", []) if resume else []

    title_regex = re.compile("|".join(re.escape(w) for w in target_role.split()), re.IGNORECASE) \
        if target_role else re.compile(".*")

    # Query static jobs
    static_jobs = list(mongo.db.jobs.find({
        "title": {"$regex": title_regex},
        "is_active": True
    }).limit(limit * 3))

    # Query scraped jobs — use title OR name field
    scraped_jobs = list(mongo.db.scraped_jobs.find({
        "$or": [
            {"title": {"$regex": title_regex}},
            {"name": {"$regex": title_regex}},
        ]
    }).sort("scraped_at", -1).limit(limit * 3))

    # Normalize scraped jobs to same schema as static
    for j in scraped_jobs:
        j.setdefault("title", j.get("name", ""))
        j.setdefault("required_skills", [])
        j.setdefault("apply_url", j.get("link", ""))
        j.setdefault("company", "")
        j.setdefault("location", "")

    all_jobs = static_jobs + scraped_jobs

    # Score and sort
    scored = [
        {**job, "match_score": score_job_match(resume_skills, job)}
        for job in all_jobs
    ]
    scored.sort(key=lambda x: x["match_score"], reverse=True)

    # Deduplicate by link
    seen: set[str] = set()
    deduped = []
    for j in scored:
        link = j.get("link") or j.get("apply_url", "")
        if link not in seen:
            seen.add(link)
            j["_id"] = str(j["_id"])
            deduped.append(j)

    return deduped[:limit]
