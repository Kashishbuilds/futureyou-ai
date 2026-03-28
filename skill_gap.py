"""
FutureYou AI – Skill Gap Analyzer
====================================
Compares a user's current skills against the requirements of predicted roles
and surfaces the delta (missing skills) for each career path.
"""

import json
import os

# ── Load career profiles from model metadata ─────────────────────────────────
_META_PATH = os.path.join(os.path.dirname(__file__),
                          "..", "model", "model_meta.json")

if os.path.exists(_META_PATH):
    with open(_META_PATH) as f:
        _meta = json.load(f)
    CAREER_PROFILES: dict = _meta["career_profiles"]
else:
    # Minimal fallback (mirrors train_model.py)
    CAREER_PROFILES = {
        "Data Scientist": {
            "required": ["python","machine learning","statistics","pandas",
                         "numpy","sql","data visualization","scikit-learn",
                         "data analysis","a/b testing"],
            "bonus":    ["deep learning","tensorflow","pytorch","spark",
                         "tableau","r"],
        },
        "Machine Learning Engineer": {
            "required": ["python","machine learning","deep learning",
                         "tensorflow","pytorch","scikit-learn","docker",
                         "git","algorithms","data structures"],
            "bonus":    ["kubernetes","aws","scala","spark","system design"],
        },
        "Full Stack Developer": {
            "required": ["javascript","react","nodejs","html","css",
                         "rest api","sql","git","python","typescript"],
            "bonus":    ["graphql","docker","aws","vue","angular",
                         "system design","agile"],
        },
        "DevOps Engineer": {
            "required": ["docker","kubernetes","aws","linux","bash",
                         "git","ci/cd","terraform","python","system design"],
            "bonus":    ["azure","gcp"],
        },
        "Cybersecurity Analyst": {
            "required": ["cybersecurity","network security","linux",
                         "penetration testing","python","bash","cryptography",
                         "git","system design"],
            "bonus":    ["aws","docker","kubernetes","c++"],
        },
        "Android Developer": {
            "required": ["android","kotlin","java","git","rest api",
                         "sql","algorithms","data structures"],
            "bonus":    ["react native","firebase","ci/cd","agile"],
        },
        "iOS Developer": {
            "required": ["ios","swift","git","rest api","sql",
                         "algorithms","data structures"],
            "bonus":    ["react native","firebase","ci/cd","agile"],
        },
        "Data Engineer": {
            "required": ["python","sql","spark","hadoop","aws",
                         "docker","git","data analysis","linux","bash"],
            "bonus":    ["scala","kubernetes","airflow","kafka","terraform"],
        },
        "NLP Engineer": {
            "required": ["python","nlp","machine learning","deep learning",
                         "tensorflow","pytorch","pandas","numpy",
                         "scikit-learn","git"],
            "bonus":    ["transformers","docker","aws","statistics","r"],
        },
        "Cloud Architect": {
            "required": ["aws","azure","gcp","terraform","docker",
                         "kubernetes","system design","linux","ci/cd","python"],
            "bonus":    ["networking","security","leadership"],
        },
    }


def analyse_skill_gap(user_skills: list[str],
                      career: str) -> dict:
    """
    For a given *career*, identify:
      - missing required skills  (must-have)
      - missing bonus skills     (nice-to-have)
      - matched skills           (already have)
      - readiness score          (0–100)

    Returns
    -------
    {
        "career":          str,
        "matched":         [str],
        "missing_required":[str],
        "missing_bonus":   [str],
        "readiness":       float   # percentage
    }
    """
    profile = CAREER_PROFILES.get(career, {})
    required = [s.lower() for s in profile.get("required", [])]
    bonus    = [s.lower() for s in profile.get("bonus", [])]
    user_set = {s.lower() for s in user_skills}

    matched          = [s for s in required if s in user_set]
    missing_required = [s for s in required if s not in user_set]
    missing_bonus    = [s for s in bonus    if s not in user_set]

    total     = len(required) or 1
    readiness = round(len(matched) / total * 100, 1)

    return {
        "career":           career,
        "matched":          matched,
        "missing_required": missing_required,
        "missing_bonus":    missing_bonus,
        "readiness":        readiness,
    }


def analyse_all_gaps(user_skills: list[str],
                     top_careers: list[str]) -> dict[str, dict]:
    """
    Run gap analysis for every career in *top_careers*.

    Returns  {career_name: gap_dict}
    """
    return {career: analyse_skill_gap(user_skills, career)
            for career in top_careers}


def get_priority_skills(gap: dict, max_skills: int = 5) -> list[str]:
    """
    Return the highest-priority skills to learn next.
    Required gaps come first, then bonus gaps.
    """
    return (gap["missing_required"] + gap["missing_bonus"])[:max_skills]
