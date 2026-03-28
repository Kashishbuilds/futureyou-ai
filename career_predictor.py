"""
FutureYou AI – Career Predictor (Inference)
=============================================
Loads the trained RandomForest model and exposes clean prediction APIs.
"""

import os
import json
import joblib
import numpy as np

_MODEL_DIR = os.path.dirname(__file__)

def _load_artifacts():
    model_path = os.path.join(_MODEL_DIR, "model", "career_model.pkl")
    encoder_path = os.path.join(_MODEL_DIR, "model", "label_encoder.pkl")
    meta_path = os.path.join(_MODEL_DIR, "model", "model_meta.json")

    clf = joblib.load(model_path)
    le = joblib.load(encoder_path)

    with open(meta_path, "r") as f:
        meta = json.load(f)

    return clf, le, meta


# Cache so we only read from disk once per process
_clf, _le, _meta = None, None, None


def _get_model():
    global _clf, _le, _meta
    if _clf is None:
        _clf, _le, _meta = _load_artifacts()
    return _clf, _le, _meta


def skills_to_vector(skills: list[str]) -> np.ndarray:
    clf, le, meta = _get_model()
    all_skills = meta["all_skills"]
    skill_set  = {s.lower().strip() for s in skills}

    return np.array(
        [1 if s in skill_set else 0 for s in all_skills],
        dtype=np.float32
    ).reshape(1, -1)


def predict_careers(skills: list[str], top_n: int = 3) -> list[dict]:
    clf, le, meta = _get_model()
    vec = skills_to_vector(skills)
    probs = clf.predict_proba(vec)[0]

    top_indices = np.argsort(probs)[::-1][:top_n]

    return [
        {
            "career": le.classes_[i],
            "probability": round(float(probs[i]), 4),
            "rank": rank + 1,
        }
        for rank, i in enumerate(top_indices)
    ]


def predict_all_probabilities(skills: list[str]) -> dict[str, float]:
    clf, le, meta = _get_model()
    vec = skills_to_vector(skills)
    probs = clf.predict_proba(vec)[0]

    return {
        le.classes_[i]: round(float(probs[i]), 4)
        for i in range(len(le.classes_))
    }


def simulate_skill_addition(base_skills: list[str], new_skill: str) -> dict:
    before = predict_all_probabilities(base_skills)
    after = predict_all_probabilities(base_skills + [new_skill])

    delta = {
        c: round(after[c] - before[c], 4)
        for c in before
    }

    return {
        "before": before,
        "after": after,
        "delta": delta
    }