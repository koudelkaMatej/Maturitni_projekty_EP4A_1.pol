# -*- coding: utf-8 -*-
"""Jednoduchý Flask backend pro registraci, přihlášení a žebříčky.

Endpointy (prefix /api):
- POST /register {email, username, password}
- POST /login {identifier, password}  # identifier = username nebo email
- GET /me (Auth: Bearer <token>)
- GET /scores (Auth: Bearer <token>) -> {scores: {mode: [{username, score}]}}
- POST /scores (Auth: Bearer <token>) {mode, score}

Token je jen jednoduchý řetězec uložený v DB (není to JWT).
Databáze: sqlite3 soubor vedle app.py (db.sqlite3).
"""
import os
import sqlite3
import secrets
from datetime import datetime
from typing import Dict, Any

from flask import Flask, jsonify, request
from flask_cors import CORS

APP_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(APP_DIR, "db.sqlite3")

# Herni mody dostupne v aplikaci (mapovani kod -> popisek)
MODE_LABELS = {
    "classic": "Classic",
    "poison": "Poison",
    "pillars": "Pillars",
    "hardcore": "Hardcore",
}

app = Flask(__name__)
CORS(app)


# -----------------------------
# Databáze
# -----------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            token TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mode TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


# -----------------------------
# Pomocné funkce
# -----------------------------

def make_token() -> str:
    return secrets.token_hex(16)


def auth_user(req) -> Dict[str, Any]:
    auth = req.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]
    else:
        token = None
    if not token:
        return None
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# -----------------------------
# Endpointy
# -----------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not username or not password:
        return jsonify({"error": "Vyplň všechna pole"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, username, password, created_at) VALUES (?, ?, ?, ?)",
            (email, username, password, datetime.utcnow().isoformat()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Uživatel už existuje"}), 400

    conn.close()
    return jsonify({"message": "Registrace úspěšná"}), 200


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    ident = (data.get("identifier") or "").strip()
    password = (data.get("password") or "").strip()
    if not ident or not password:
        return jsonify({"error": "Vyplň všechna pole"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE (email = ? OR username = ?) AND password = ?",
        (ident, ident, password),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Špatné přihlašovací údaje"}), 401

    token = make_token()
    cur.execute("UPDATE users SET token = ? WHERE id = ?", (token, row["id"]))
    conn.commit()
    conn.close()
    return jsonify({"token": token}), 200


@app.route("/api/me", methods=["GET"])
def me():
    user = auth_user(request)
    if not user:
        return jsonify({"error": "Nejste přihlášen."}), 401
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT mode, MAX(score) AS best_score FROM scores WHERE user_id = ? GROUP BY mode",
        (user["id"],),
    )
    rows = cur.fetchall()
    conn.close()

    best_lookup = {row["mode"]: int(row["best_score"] or 0) for row in rows}
    best_scores = [
        {"mode": code, "label": label, "score": best_lookup.get(code, 0)}
        for code, label in MODE_LABELS.items()
    ]

    return jsonify(
        {
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"],
            "best_scores": best_scores,
        }
    )


@app.route("/api/scores", methods=["GET", "POST"])
def scores():
    user = auth_user(request)
    if not user:
        return jsonify({"error": "Nejste přihlášen."}), 401

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        mode = (data.get("mode") or "").strip()
        try:
            score = int(data.get("score"))
        except Exception:
            score = None
        if not mode or score is None:
            conn.close()
            return jsonify({"error": "Chybí mód nebo skóre"}), 400
        cur.execute(
            "SELECT id, score FROM scores WHERE user_id = ? AND mode = ? ORDER BY score DESC LIMIT 1",
            (user["id"], mode),
        )
        best_row = cur.fetchone()
        now = datetime.utcnow().isoformat()
        if best_row and score <= best_row["score"]:
            conn.close()
            return jsonify({"message": "Skóre se nezapsalo, není vyšší než dosavadní."}), 200
        if best_row:
            cur.execute(
                "UPDATE scores SET score = ?, created_at = ? WHERE id = ?",
                (score, now, best_row["id"]),
            )
        else:
            cur.execute(
                "INSERT INTO scores (user_id, mode, score, created_at) VALUES (?, ?, ?, ?)",
                (user["id"], mode, score, now),
            )
        conn.commit()

    # GET nebo po POST vrátíme top 10 na mód
    cur.execute("SELECT DISTINCT mode FROM scores")
    modes = [r[0] for r in cur.fetchall()]
    scores_resp: Dict[str, Any] = {}
    for m in modes:
        cur.execute(
            """
            SELECT u.username, s.score
            FROM scores s
            JOIN users u ON u.id = s.user_id
            WHERE s.mode = ?
            ORDER BY s.score DESC, s.created_at ASC
            LIMIT 10
            """,
            (m,),
        )
        scores_resp[m] = [dict(username=r[0], score=r[1]) for r in cur.fetchall()]

    conn.close()
    return jsonify({"scores": scores_resp})


@app.route("/api/scores/public", methods=["GET"])
def public_scores():
    conn = get_db()
    cur = conn.cursor()
    scores_resp: Dict[str, Any] = {}
    for mode in MODE_LABELS.keys():
        cur.execute(
            """
            SELECT u.username, s.score
            FROM scores s
            JOIN users u ON u.id = s.user_id
            WHERE s.mode = ?
            ORDER BY s.score DESC, s.created_at ASC
            LIMIT 10
            """,
            (mode,),
        )
        scores_resp[mode] = [dict(username=r[0], score=r[1]) for r in cur.fetchall()]
    conn.close()
    return jsonify({"scores": scores_resp})


if __name__ == "__main__":
    app.run(debug=True)
