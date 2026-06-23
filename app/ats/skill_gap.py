import re

# Curated tech skill vocabulary (extend as needed)
TECH_SKILLS_VOCAB = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "Redis",
    "React", "Vue", "Angular", "Next.js", "Node.js", "Flask", "Django", "FastAPI",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform",
    "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "scikit-learn",
    "Spark", "Kafka", "Airflow", "Hadoop", "dbt", "Tableau", "Power BI",
    "Git", "CI/CD", "Jenkins", "GitHub Actions", "Linux", "REST API", "GraphQL"
]


def extract_skills_from_text(text: str, vocab: list = TECH_SKILLS_VOCAB) -> list:
    """Case-insensitive match of known skills in text."""
    text_lower = text.lower()
    return [skill for skill in vocab if skill.lower() in text_lower]


def analyze_skill_gap(
    resume_skills: list,
    jd_text: str,
    target_skills: list = None
) -> dict:
    """
    Compare resume skills against job description and optional target list.

    Returns:
        matched: Skills user already has that are required
        missing: Skills required but absent from resume
        recommended_learning: Top 5 skills to learn with priority score
    """
    jd_skills = extract_skills_from_text(jd_text)
    if target_skills:
        jd_skills = list(set(jd_skills + target_skills))

    resume_skills_lower = [s.lower() for s in resume_skills]

    matched = [s for s in jd_skills if s.lower() in resume_skills_lower]
    missing = [s for s in jd_skills if s.lower() not in resume_skills_lower]

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": round(
            len(matched) / max(len(jd_skills), 1) * 100
        ),
        "recommended_learning": missing[:5]  # Prioritize first 5 gaps
    }
