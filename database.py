import sqlite3
import bcrypt
import os
import json
from datetime import datetime

DB_PATH = "data/eduforge.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist and migrate schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            education_level TEXT NOT NULL,
            output_type TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT NOT NULL,
            created_at TEXT NOT NULL,
            evaluation_data TEXT,
            logs_data TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Automatic schema migration for existing databases
    try:
        cursor.execute("ALTER TABLE history ADD COLUMN evaluation_data TEXT")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE history ADD COLUMN logs_data TEXT")
    except Exception:
        pass

    conn.commit()
    conn.close()


# ── Auth functions ────────────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str) -> dict:
    """Register a new user. Returns success/error dict."""
    if len(username) < 3:
        return {"success": False, "error": "Username must be at least 3 characters."}
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}
    if "@" not in email:
        return {"success": False, "error": "Please enter a valid email address."}

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username.strip(), email.strip().lower(),
             password_hash, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return {"success": True}
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return {"success": False, "error": "Username already taken."}
        if "email" in str(e):
            return {"success": False, "error": "Email already registered."}
        return {"success": False, "error": "Registration failed. Please try again."}


def login_user(username: str, password: str) -> dict:
    """Authenticate a user. Returns user dict or error."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username.strip(),)
    ).fetchone()
    conn.close()

    if not user:
        return {"success": False, "error": "Username not found."}

    if not bcrypt.checkpw(password.encode("utf-8"),
                          user["password_hash"].encode("utf-8")):
        return {"success": False, "error": "Incorrect password."}

    return {
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
    }


# ── History functions ─────────────────────────────────────────────────────────

def save_to_history(user_id: int, topic: str, education_level: str,
                    output_type: str, content: str, sources: list,
                    evaluation_data: dict = None, logs_data: list = None) -> int:
    """Save a generation to history with full multi-metric evaluation & telemetry. Returns the new record ID."""
    conn = get_connection()
    eval_json = json.dumps(evaluation_data) if evaluation_data else None
    logs_json = json.dumps(logs_data) if logs_data else None
    cursor = conn.execute(
        """INSERT INTO history
           (user_id, topic, education_level, output_type, content, sources, created_at, evaluation_data, logs_data)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, topic, education_level, output_type,
         content, "\n".join(sources), datetime.now().isoformat(), eval_json, logs_json)
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_user_history(user_id: int) -> list:
    """Get all history records for a user, newest first."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, topic, education_level, output_type,
                  content, sources, created_at, evaluation_data, logs_data
           FROM history
           WHERE user_id = ?
           ORDER BY created_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_history_record(record_id: int, user_id: int):
    """Delete a history record (only if it belongs to the user)."""
    conn = get_connection()
    conn.execute(
        "DELETE FROM history WHERE id = ? AND user_id = ?",
        (record_id, user_id)
    )
    conn.commit()
    conn.close()


def get_history_record(record_id: int, user_id: int) -> dict:
    """Get a single history record."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM history WHERE id = ? AND user_id = ?",
        (record_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None