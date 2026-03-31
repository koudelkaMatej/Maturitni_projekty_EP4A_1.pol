import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "data.sqlite"))


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            turns INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


def get_user_id(username: str):
    username = (username or "").strip()
    if not username:
        return None
    conn = get_db()
    try:
        row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        return row["id"] if row else None
    finally:
        conn.close()

def verify_login(username: str, password: str) -> bool:
    username = (username or "").strip()
    if not username or not password:
        return False
    conn = get_db()
    try:
        row = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return False
        return check_password_hash(row["password_hash"], password)
    finally:
        conn.close()


def save_result(username: str, turns: int) -> bool:
    uid = get_user_id(username)
    if uid is None or turns <= 0:
        return False
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO results (user_id, turns, created_at) VALUES (?, ?, ?)",
            (uid, int(turns), (datetime.utcnow() + timedelta(hours=1)).isoformat()),
        )
        conn.commit()
        return True
    finally:
        conn.close()
