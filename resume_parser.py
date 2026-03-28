"""
FutureYou AI – Resume Parser
==============================
Extracts skills from raw resume text using keyword matching + TF-IDF scoring.
Works with plain text or text extracted from a PDF.
"""

import re
import json
import os
import math
from collections import Counter

# ── Load skill master list from model metadata (if available) ────────────────
_META_PATH = os.path.join(os.path.dirname(__file__),
                          "..", "model", "model_meta.json")

if os.path.exists(_META_PATH):
    with open(_META_PATH) as f:
        _meta = json.load(f)
    KNOWN_SKILLS: list[str] = _meta["all_skills"]
else:
    # Fallback: inline minimal list so the module is importable before training
    KNOWN_SKILLS = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go",
        "rust", "kotlin", "swift", "php", "ruby", "scala", "r",
        "react", "vue", "angular", "html", "css", "nodejs", "graphql",
        "rest api", "machine learning", "deep learning", "nlp",
        "computer vision", "tensorflow", "pytorch", "scikit-learn",
        "pandas", "numpy", "sql", "spark", "hadoop",
        "data visualization", "tableau", "power bi", "statistics",
        "data analysis", "a/b testing", "docker", "kubernetes",
        "aws", "azure", "gcp", "terraform", "ci/cd", "linux", "bash",
        "git", "android", "ios", "react native", "flutter",
        "cybersecurity", "penetration testing", "cryptography",
        "network security", "agile", "scrum", "system design",
        "algorithms", "data structures", "communication",
        "leadership", "project management",
    ]


# ── Helper ───────────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lower-case, collapse whitespace, strip punctuation noise."""
    text = text.lower()
    text = re.sub(r"[^\w\s\+#\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract raw text from a Streamlit UploadedFile (PDF).
    Falls back to empty string if PyPDF2 is unavailable.
    """
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        pages  = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception as exc:
        print(f"[resume_parser] PDF extraction error: {exc}")
        return ""


def extract_skills_from_text(text: str,
                              top_n: int = 25,
                              min_score: float = 0.0) -> list[str]:
    """
    Return a ranked list of skills found in *text*.

    Strategy
    --------
    1. Exact phrase match for each canonical skill.
    2. TF-IDF-style score: skill frequency × log(1 + len(skill.split())).
       Multi-word skills are rewarded more heavily.
    3. Return top_n skills ordered by score (descending).
    """
    normalised = _normalise(text)
    scores: dict[str, float] = {}

    for skill in KNOWN_SKILLS:
        # Use word-boundary-aware matching for single words;
        # simple substring for multi-word phrases.
        skill_lower = skill.lower()
        if " " in skill_lower:
            count = normalised.count(skill_lower)
        else:
            pattern = r"\b" + re.escape(skill_lower) + r"\b"
            count   = len(re.findall(pattern, normalised))

        if count > 0:
            # Multi-word skills carry a natural length bonus
            idf_boost = math.log(1 + len(skill_lower.split()))
            scores[skill] = count * idf_boost

    # Filter by minimum score and sort
    filtered = {k: v for k, v in scores.items() if v >= min_score}
    ranked   = sorted(filtered, key=lambda k: filtered[k], reverse=True)
    return ranked[:top_n]


def parse_resume(uploaded_file=None, raw_text: str = "") -> dict:
    """
    Main entry point.

    Parameters
    ----------
    uploaded_file : Streamlit UploadedFile (PDF)  [optional]
    raw_text      : plain text to parse directly  [optional]

    Returns
    -------
    {
        "skills":       [...],    # extracted skills
        "word_count":   int,
        "text_preview": str       # first 300 chars for debug
    }
    """
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
    elif raw_text:
        text = raw_text
    else:
        text = ""

    skills = extract_skills_from_text(text)

    return {
        "skills":       skills,
        "word_count":   len(text.split()),
        "text_preview": text[:300],
    }
