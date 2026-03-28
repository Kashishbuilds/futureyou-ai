"""
FutureYou AI – SQLite Database Layer
=====================================
Handles all persistent storage: user sessions, predictions, and skill history.
"""

import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "futureyou.db")


@contextmanager
def get_conn():
    """Context-manager that yields an auto-committing connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                email       TEXT,
                github_user TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      INTEGER,
                skills_input    TEXT,          -- JSON list
                top_careers     TEXT,          -- JSON list of {career, prob}
                skill_gaps      TEXT,          -- JSON dict {career: [skills]}
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES user_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS simulations (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      INTEGER,
                base_skills     TEXT,          -- JSON list
                added_skill     TEXT,
                before_probs    TEXT,          -- JSON
                after_probs     TEXT,          -- JSON
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES user_sessions(id)
            );
        """)


def save_session(name: str, email: str, github_user: str = "") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO user_sessions (name, email, github_user) VALUES (?,?,?)",
            (name, email, github_user),
        )
        return cur.lastrowid


def save_prediction(session_id: int, skills: list,
                    top_careers: list, skill_gaps: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO predictions
               (session_id, skills_input, top_careers, skill_gaps)
               VALUES (?,?,?,?)""",
            (session_id,
             json.dumps(skills),
             json.dumps(top_careers),
             json.dumps(skill_gaps)),
        )


def save_simulation(session_id: int, base_skills: list, added_skill: str,
                    before_probs: dict, after_probs: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO simulations
               (session_id, base_skills, added_skill, before_probs, after_probs)
               VALUES (?,?,?,?,?)""",
            (session_id,
             json.dumps(base_skills),
             added_skill,
             json.dumps(before_probs),
             json.dumps(after_probs)),
        )


def get_recent_predictions(limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT p.*, u.name, u.email
               FROM predictions p
               JOIN user_sessions u ON u.id = p.session_id
               ORDER BY p.created_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


# Initialise on import
init_db()

def clear_predictions():
    """Delete all history records"""
    with get_conn() as conn:
        conn.execute("DELETE FROM predictions")
        conn.execute("DELETE FROM simulations")
        conn.execute("DELETE FROM user_sessions")