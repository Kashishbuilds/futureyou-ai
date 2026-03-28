"""
FutureYou AI – Roadmap Generator
===================================
Produces a structured, phase-based learning roadmap for any career path
given the user's current skill gaps.
"""

from __future__ import annotations

# ── Skill metadata: difficulty tier, estimated weeks, free resource ──────────
SKILL_META: dict[str, dict] = {
    # ── Programming languages ────────────────────────────────────────────────
    "python":           {"tier": 1, "weeks": 4,  "resource": "https://docs.python.org/3/tutorial/"},
    "javascript":       {"tier": 1, "weeks": 5,  "resource": "https://javascript.info/"},
    "typescript":       {"tier": 2, "weeks": 3,  "resource": "https://www.typescriptlang.org/docs/"},
    "java":             {"tier": 2, "weeks": 6,  "resource": "https://dev.java/learn/"},
    "kotlin":           {"tier": 2, "weeks": 4,  "resource": "https://kotlinlang.org/docs/getting-started.html"},
    "swift":            {"tier": 2, "weeks": 4,  "resource": "https://www.swift.org/getting-started/"},
    "go":               {"tier": 2, "weeks": 4,  "resource": "https://go.dev/tour/"},
    "rust":             {"tier": 3, "weeks": 8,  "resource": "https://doc.rust-lang.org/book/"},
    "c++":              {"tier": 3, "weeks": 8,  "resource": "https://www.learncpp.com/"},
    "c#":               {"tier": 2, "weeks": 5,  "resource": "https://learn.microsoft.com/en-us/dotnet/csharp/"},
    "scala":            {"tier": 3, "weeks": 6,  "resource": "https://docs.scala-lang.org/tour/tour-of-scala.html"},
    "r":                {"tier": 2, "weeks": 4,  "resource": "https://www.r-project.org/"},
    "ruby":             {"tier": 2, "weeks": 4,  "resource": "https://www.ruby-lang.org/en/documentation/"},
    "php":              {"tier": 1, "weeks": 4,  "resource": "https://www.php.net/manual/en/"},
    # ── Web ──────────────────────────────────────────────────────────────────
    "html":             {"tier": 1, "weeks": 2,  "resource": "https://developer.mozilla.org/en-US/docs/Learn/HTML"},
    "css":              {"tier": 1, "weeks": 3,  "resource": "https://developer.mozilla.org/en-US/docs/Learn/CSS"},
    "react":            {"tier": 2, "weeks": 5,  "resource": "https://react.dev/learn"},
    "vue":              {"tier": 2, "weeks": 4,  "resource": "https://vuejs.org/guide/"},
    "angular":          {"tier": 3, "weeks": 6,  "resource": "https://angular.io/tutorial"},
    "nodejs":           {"tier": 2, "weeks": 4,  "resource": "https://nodejs.org/en/learn"},
    "graphql":          {"tier": 2, "weeks": 3,  "resource": "https://graphql.org/learn/"},
    "rest api":         {"tier": 1, "weeks": 2,  "resource": "https://restfulapi.net/"},
    # ── Data / ML ────────────────────────────────────────────────────────────
    "machine learning": {"tier": 2, "weeks": 10, "resource": "https://www.coursera.org/learn/machine-learning"},
    "deep learning":    {"tier": 3, "weeks": 10, "resource": "https://www.deeplearning.ai/"},
    "nlp":              {"tier": 3, "weeks": 8,  "resource": "https://huggingface.co/learn/nlp-course/"},
    "computer vision":  {"tier": 3, "weeks": 8,  "resource": "https://cs231n.stanford.edu/"},
    "tensorflow":       {"tier": 2, "weeks": 5,  "resource": "https://www.tensorflow.org/tutorials"},
    "pytorch":          {"tier": 2, "weeks": 5,  "resource": "https://pytorch.org/tutorials/"},
    "scikit-learn":     {"tier": 1, "weeks": 3,  "resource": "https://scikit-learn.org/stable/tutorial/"},
    "pandas":           {"tier": 1, "weeks": 2,  "resource": "https://pandas.pydata.org/docs/getting_started/"},
    "numpy":            {"tier": 1, "weeks": 2,  "resource": "https://numpy.org/learn/"},
    "sql":              {"tier": 1, "weeks": 3,  "resource": "https://sqlzoo.net/"},
    "spark":            {"tier": 3, "weeks": 6,  "resource": "https://spark.apache.org/docs/latest/"},
    "hadoop":           {"tier": 3, "weeks": 6,  "resource": "https://hadoop.apache.org/docs/stable/"},
    "statistics":       {"tier": 2, "weeks": 5,  "resource": "https://www.khanacademy.org/math/statistics-probability"},
    "data analysis":    {"tier": 1, "weeks": 3,  "resource": "https://www.kaggle.com/learn/pandas"},
    "data visualization":{"tier":1, "weeks": 2,  "resource": "https://www.kaggle.com/learn/data-visualization"},
    "tableau":          {"tier": 1, "weeks": 2,  "resource": "https://www.tableau.com/learn/training"},
    "power bi":         {"tier": 1, "weeks": 2,  "resource": "https://learn.microsoft.com/en-us/power-bi/"},
    "a/b testing":      {"tier": 2, "weeks": 3,  "resource": "https://www.optimizely.com/optimization-glossary/ab-testing/"},
    # ── DevOps / Cloud ───────────────────────────────────────────────────────
    "docker":           {"tier": 2, "weeks": 3,  "resource": "https://docs.docker.com/get-started/"},
    "kubernetes":       {"tier": 3, "weeks": 5,  "resource": "https://kubernetes.io/docs/tutorials/"},
    "aws":              {"tier": 2, "weeks": 6,  "resource": "https://aws.amazon.com/getting-started/"},
    "azure":            {"tier": 2, "weeks": 6,  "resource": "https://learn.microsoft.com/en-us/azure/"},
    "gcp":              {"tier": 2, "weeks": 6,  "resource": "https://cloud.google.com/learn"},
    "terraform":        {"tier": 2, "weeks": 4,  "resource": "https://developer.hashicorp.com/terraform/tutorials"},
    "ci/cd":            {"tier": 2, "weeks": 3,  "resource": "https://www.atlassian.com/continuous-delivery"},
    "linux":            {"tier": 1, "weeks": 3,  "resource": "https://linuxjourney.com/"},
    "bash":             {"tier": 1, "weeks": 2,  "resource": "https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html"},
    "git":              {"tier": 1, "weeks": 1,  "resource": "https://git-scm.com/book/en/v2"},
    # ── Mobile ───────────────────────────────────────────────────────────────
    "android":          {"tier": 2, "weeks": 6,  "resource": "https://developer.android.com/courses"},
    "ios":              {"tier": 2, "weeks": 6,  "resource": "https://developer.apple.com/tutorials/"},
    "react native":     {"tier": 2, "weeks": 5,  "resource": "https://reactnative.dev/docs/getting-started"},
    "flutter":          {"tier": 2, "weeks": 5,  "resource": "https://docs.flutter.dev/get-started"},
    # ── Security ─────────────────────────────────────────────────────────────
    "cybersecurity":    {"tier": 2, "weeks": 8,  "resource": "https://www.cybrary.it/"},
    "penetration testing":{"tier":3,"weeks": 8,  "resource": "https://www.hackthebox.com/"},
    "cryptography":     {"tier": 3, "weeks": 6,  "resource": "https://www.coursera.org/learn/crypto"},
    "network security": {"tier": 2, "weeks": 6,  "resource": "https://www.cybrary.it/course/network-security-for-it-professionals"},
    # ── General ──────────────────────────────────────────────────────────────
    "algorithms":       {"tier": 2, "weeks": 6,  "resource": "https://www.khanacademy.org/computing/computer-science/algorithms"},
    "data structures":  {"tier": 2, "weeks": 4,  "resource": "https://www.geeksforgeeks.org/data-structures/"},
    "system design":    {"tier": 3, "weeks": 6,  "resource": "https://github.com/donnemartin/system-design-primer"},
    "agile":            {"tier": 1, "weeks": 1,  "resource": "https://www.atlassian.com/agile"},
    "scrum":            {"tier": 1, "weeks": 1,  "resource": "https://www.scrum.org/resources/what-is-scrum"},
    "leadership":       {"tier": 2, "weeks": 4,  "resource": "https://www.coursera.org/courses?query=leadership"},
    "project management":{"tier":2, "weeks": 4,  "resource": "https://www.pmi.org/learning/library"},
    "communication":    {"tier": 1, "weeks": 2,  "resource": "https://www.coursera.org/courses?query=communication+skills"},
}

_DEFAULT_META = {"tier": 2, "weeks": 4, "resource": "https://www.google.com/search?q=learn+{}"}

PHASE_NAMES = {1: "🌱 Foundation",
               2: "🚀 Core Skills",
               3: "🔬 Advanced"}


def _get_meta(skill: str) -> dict:
    meta = SKILL_META.get(skill.lower(), _DEFAULT_META).copy()
    if "{}" in meta.get("resource", ""):
        meta["resource"] = meta["resource"].format(skill.replace(" ", "+"))
    return meta


def generate_roadmap(career: str,
                     missing_required: list[str],
                     missing_bonus:    list[str]) -> dict:
    """
    Build a phased roadmap.

    Returns
    -------
    {
        "career": str,
        "total_weeks": int,
        "phases": [
            {
                "phase":  int,
                "label":  str,
                "skills": [{"skill", "weeks", "resource", "tier"}]
            }
        ]
    }
    """
    phases: dict[int, list] = {1: [], 2: [], 3: []}

    for skill in missing_required:
        meta = _get_meta(skill)
        phases[meta["tier"]].append({
            "skill":    skill,
            "weeks":    meta["weeks"],
            "resource": meta["resource"],
            "tier":     meta["tier"],
            "priority": "required",
        })

    for skill in missing_bonus:
        meta = _get_meta(skill)
        phases[meta["tier"]].append({
            "skill":    skill,
            "weeks":    meta["weeks"],
            "resource": meta["resource"],
            "tier":     meta["tier"],
            "priority": "bonus",
        })

    # Sort each phase by weeks ascending (easier first)
    for p in phases.values():
        p.sort(key=lambda x: x["weeks"])

    total_weeks = sum(
        s["weeks"] for items in phases.values() for s in items
    )

    return {
        "career":      career,
        "total_weeks": total_weeks,
        "phases": [
            {
                "phase":  p,
                "label":  PHASE_NAMES[p],
                "skills": items,
            }
            for p, items in phases.items()
            if items
        ],
    }
