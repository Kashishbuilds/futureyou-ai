"""
FutureYou AI – GitHub Analyzer
================================
Fetches a user's public repositories via the GitHub REST API,
extracts programming languages, and maps them to canonical skills.
"""

import requests
import json
import os
from collections import Counter

# GitHub REST API v3 base URL
GITHUB_API = "https://api.github.com"

# ── Language → skill mapping ─────────────────────────────────────────────────
LANGUAGE_TO_SKILL: dict[str, list[str]] = {
    "Python":       ["python"],
    "JavaScript":   ["javascript"],
    "TypeScript":   ["typescript"],
    "Java":         ["java"],
    "C++":          ["c++"],
    "C#":           ["c#"],
    "Go":           ["go"],
    "Rust":         ["rust"],
    "Kotlin":       ["kotlin"],
    "Swift":        ["swift"],
    "PHP":          ["php"],
    "Ruby":         ["ruby"],
    "Scala":        ["scala"],
    "R":            ["r"],
    "Shell":        ["bash", "linux"],
    "HCL":          ["terraform"],
    "Dockerfile":   ["docker"],
    "HTML":         ["html"],
    "CSS":          ["css"],
    "Vue":          ["vue"],
}

# ── Topic → skill mapping (GitHub repo topics) ───────────────────────────────
TOPIC_TO_SKILL: dict[str, str] = {
    "machine-learning":    "machine learning",
    "deep-learning":       "deep learning",
    "nlp":                 "nlp",
    "computer-vision":     "computer vision",
    "tensorflow":          "tensorflow",
    "pytorch":             "pytorch",
    "react":               "react",
    "angular":             "angular",
    "vuejs":               "vue",
    "nodejs":              "nodejs",
    "docker":              "docker",
    "kubernetes":          "kubernetes",
    "aws":                 "aws",
    "android":             "android",
    "ios":                 "ios",
    "flutter":             "flutter",
    "react-native":        "react native",
    "graphql":             "graphql",
    "ci-cd":               "ci/cd",
    "cybersecurity":       "cybersecurity",
    "data-science":        "data analysis",
    "data-visualization":  "data visualization",
}


def _headers(token: str | None = None) -> dict:
    h = {"Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_repos(username: str, token: str | None = None,
                max_repos: int = 30) -> list[dict]:
    """Return a list of repository dicts for *username*."""
    url    = f"{GITHUB_API}/users/{username}/repos"
    params = {"per_page": max_repos, "sort": "pushed", "type": "owner"}
    try:
        resp = requests.get(url, headers=_headers(token),
                            params=params, timeout=10)
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        print(f"[github_analyzer] Request failed: {exc}")
        return []


def analyze_github(username: str,
                   token: str | None = None) -> dict:
    """
    Analyse a GitHub user's public repositories.

    Returns
    -------
    {
        "username":     str,
        "repo_count":   int,
        "top_languages": [(lang, count), ...],
        "skills":       [str, ...],          # deduplicated, ranked
        "repos":        [{name, description, language, stars, topics}, ...]
    }
    """
    if not username or username.strip() == "":
        return _empty(username)

    repos = fetch_repos(username.strip(), token)
    if not repos:
        return _empty(username)

    lang_counter: Counter = Counter()
    skill_set: set[str]   = set()
    repo_summaries: list  = []

    for repo in repos:
        # Language
        lang = repo.get("language") or ""
        if lang:
            lang_counter[lang] += 1
            for skill in LANGUAGE_TO_SKILL.get(lang, []):
                skill_set.add(skill)

        # Topics
        for topic in repo.get("topics", []):
            if topic in TOPIC_TO_SKILL:
                skill_set.add(TOPIC_TO_SKILL[topic])

        repo_summaries.append({
            "name":        repo.get("name", ""),
            "description": (repo.get("description") or "")[:120],
            "language":    lang,
            "stars":       repo.get("stargazers_count", 0),
            "topics":      repo.get("topics", []),
        })

    # Sort repos by stars
    repo_summaries.sort(key=lambda r: r["stars"], reverse=True)

    return {
        "username":      username,
        "repo_count":    len(repos),
        "top_languages": lang_counter.most_common(10),
        "skills":        sorted(skill_set),
        "repos":         repo_summaries[:15],   # top 15 for display
    }


def _empty(username: str) -> dict:
    return {
        "username":      username,
        "repo_count":    0,
        "top_languages": [],
        "skills":        [],
        "repos":         [],
    }
