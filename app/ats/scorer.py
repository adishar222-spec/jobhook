import re
from collections import Counter
from typing import Tuple


COMMON_STOP_WORDS = {
    # Basic conjunctions, prepositions, and articles
    "the", "and", "for", "with", "you", "are", "our", "this", "will", "have",
    "your", "that", "from", "all", "can", "more", "is", "or", "in", "to", "of",
    "at", "by", "an", "be", "as", "if", "on", "it", "its", "which", "who", "whom",
    "whose", "they", "them", "their", "we", "us", "i", "me", "my", "mine",

    # Common auxiliary and modal verbs
    "do", "does", "did", "done", "doing", "was", "were", "been", "being",
    "has", "had", "having", "should", "could", "would", "may", "might", "must",
    "can", "shall",

    # Generic Job Description words (low information content for role)
    "requirements", "responsibility", "qualified", "role", "candidate", "successful",
    "ability", "experience", "work", "job", "company", "team", "strong", "excellent",
    "skills", "knowledge", "desired", "preferred", "required", "including", "using",
    "plus", "years", "within", "ideal"
}


def tokenize(text: str) -> set:
    """Lowercase, remove punctuation, split into unique meaningful words."""
    # Matches words, allowing special chars like C++, .NET, C#
    # We use a more permissive regex and then clean up trailing punctuation
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#\.]*", text.lower())
    
    cleaned = set()
    for t in tokens:
        # Strip trailing dots unless they seem to be part of a tech name (e.g., .js)
        if t.endswith('.') and not t.endswith('.js') and not t.endswith('.net'):
            t = t.rstrip('.')
        
        if len(t) > 1 and t not in COMMON_STOP_WORDS:
            cleaned.add(t)
    return cleaned


def extract_keywords(jd_text: str, top_n: int = 40) -> list:
    """
    Frequency-rank keywords from a job description.
    Returns top N meaningful keywords.
    """
    # Use the same logic as tokenize but preserve frequency
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#\.]*", jd_text.lower())
    filtered = []
    for t in tokens:
        if t.endswith('.') and not t.endswith('.js') and not t.endswith('.net'):
            t = t.rstrip('.')
        if len(t) > 1 and t not in COMMON_STOP_WORDS:
            filtered.append(t)
            
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
