import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash



BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "Shared", "data.sqlite"))

app = Flask(__name__)
app.secret_key = os.environ.get("COLOR_WARZ_SECRET", "dev-secret-change-me")


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


@app.post("/api/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if len(username) < 3 or len(password) < 4:
        return jsonify({"error": "Neplatné údaje"}), 400
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), datetime.utcnow().isoformat()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Uživatel již existuje"}), 409
    finally:
        conn.close()
    return jsonify({"ok": True})


@app.post("/api/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    conn = get_db()
    row = conn.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Špatné jméno nebo heslo"}), 401
    session["user_id"] = row["id"]
    session["username"] = username
    return jsonify({"ok": True, "username": username})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
def me():
    if "user_id" not in session:
        return jsonify({"user": None})
    return jsonify({"user": {"id": session["user_id"], "username": session.get("username")}})


@app.post("/api/score")
def score():
    if "user_id" not in session:
        return jsonify({"error": "Nepřihlášen"}), 401
    data = request.get_json(force=True, silent=True) or {}
    turns = data.get("turns")
    try:
        turns = int(turns)
    except (TypeError, ValueError):
        return jsonify({"error": "Počet tahů musí být číslo"}), 400
    if turns <= 0 or turns > 9999:
        return jsonify({"error": "Neplatný počet tahů"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO results (user_id, turns, created_at) VALUES (?, ?, ?)",
        (session["user_id"], turns, (datetime.utcnow() + timedelta(hours=1)).isoformat()),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.get("/api/stats")
def stats():
    if "user_id" not in session:
        return jsonify({"error": "Nepřihlášen"}), 401
    conn = get_db()
    rows = conn.execute(
        "SELECT turns, created_at FROM results WHERE user_id = ? ORDER BY id DESC LIMIT 50",
        (session["user_id"],),
    ).fetchall()
    agg = conn.execute(
        "SELECT COUNT(*) AS wins, AVG(turns) AS avg_turns FROM results WHERE user_id = ?",
        (session["user_id"],),
    ).fetchone()
    conn.close()
    return jsonify(
        {
            "wins": agg["wins"] or 0,
            "avg_turns": float(agg["avg_turns"]) if agg["avg_turns"] is not None else None,
            "results": [{"turns": r["turns"], "created_at": r["created_at"]} for r in rows],
        }
    )

@app.get("/api/leaderboard")
def leaderboard():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT u.username AS username,
               COUNT(r.id) AS wins,
               AVG(r.turns) AS avg_turns
        FROM users u
        LEFT JOIN results r ON r.user_id = u.id
        GROUP BY u.id
        ORDER BY wins DESC, avg_turns ASC NULLS LAST, username ASC
        LIMIT 50
        """
    ).fetchall()
    conn.close()
    return jsonify(
        {"items": [{"username": r["username"], "wins": int(r["wins"] or 0), "avg_turns": r["avg_turns"]} for r in rows]}
    )

@app.get("/")
def root():
    return send_from_directory(BASE_DIR, "index.html")

@app.get("/<path:filename>")
def static_files(filename: str):
    full = os.path.join(BASE_DIR, filename)
    if os.path.isfile(full):
        return send_from_directory(BASE_DIR, filename)
    return jsonify({"error": "Not Found"}), 404


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
