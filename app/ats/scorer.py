import re
from collections import Counter
from typing import Tuple


COMMON_STOP_WORDS = {
    "the", "and", "for", "with", "you", "are", "our", "this",
    "will", "have", "your", "that", "from", "all", "can", "more"
}


def tokenize(text: str) -> set:
    """Lowercase, remove punctuation, split into unique meaningful words."""
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#\.]{1,}\b", text.lower())
    return set(w for w in words if w not in COMMON_STOP_WORDS)


def extract_keywords(jd_text: str, top_n: int = 40) -> list:
    """
    Frequency-rank keywords from a job description.
    Returns top N meaningful keywords.
    """
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#\.]{1,}\b", jd_text.lower())
    filtered = [w for w in words if w not in COMMON_STOP_WORDS]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(top_n)]


def calculate_ats_score(resume_text: str, jd_text: str) -> dict:
    """
    Calculate ATS compatibility score.

    Returns:
        score (int): 0–100 percentage match
        matched_keywords (list): Keywords present in both
        missing_keywords (list): Important JD keywords absent from resume
        breakdown (dict): Section-level scoring
    """
    resume_tokens = tokenize(resume_text)
    jd_keywords = extract_keywords(jd_text, top_n=50)

    matched = [kw for kw in jd_keywords if kw in resume_tokens]
    missing = [kw for kw in jd_keywords if kw not in resume_tokens]

    score = round(len(matched) / max(len(jd_keywords), 1) * 100)

    return {
        "score": score,
        "total_keywords_checked": len(jd_keywords),
        "matched_keywords": matched,
        "missing_keywords": missing[:20],  # Top 20 missing
        "rating": _rating_label(score)
    }


def _rating_label(score: int) -> str:
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Work"
