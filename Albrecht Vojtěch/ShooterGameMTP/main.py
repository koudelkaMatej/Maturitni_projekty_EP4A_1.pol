import sqlite3
import os
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "zmen_toto_na_nejaky_tajny_klic_123!"  # ← ZMĚŇ před nasazením!
DB_PATH = os.path.abspath("database.db")

# Lock pro zápis do DB (thread-safe)
db_lock = threading.Lock()

# --------------------------
# Připojení k DB
# --------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------
# Vytvoření tabulek
# --------------------------
def create_tables():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    # Přidej is_admin sloupec pokud DB už existuje bez něj
    try:
        conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Sloupec už existuje, to je OK
    conn.commit()
    conn.close()

create_tables()

# --------------------------
# Dekorátory pro ochranu rout
# --------------------------
def login_required(f):
    """Přesměruje na /signin pokud uživatel není přihlášen."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("signin"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Vrátí 403 pokud přihlášený uživatel není admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("signin"))
        if not session.get("is_admin"):
            return "Nemáš oprávnění!", 403
        return f(*args, **kwargs)
    return decorated

# --------------------------
# Webové routy
# --------------------------
@app.route("/")
def home():
    return render_template("MTP.html")

@app.route("/aktivniuzivatele")
def aktivniuzivatele():
    conn = get_db_connection()
    users = conn.execute("SELECT username FROM users").fetchall()
    conn.close()
    return render_template("ActiveUsers.html", users=users)

@app.route("/scoreboard")
def scoreboard():
    conn = get_db_connection()
    scores = conn.execute("""
        SELECT u.username, MAX(s.score) as score
        FROM scores s JOIN users u ON s.user_id = u.id
        GROUP BY u.id
        ORDER BY score DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    return render_template("ScoreBoard.html", scores=scores)

# --------------------------
# Web registrace/login
# --------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        with db_lock:
            conn = get_db_connection()
            try:
                conn.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, password)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                conn.close()
                return "Uživatel již existuje!"
            conn.close()
        return redirect(url_for("signin"))

    return render_template("SignUp.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            # Uložení do session
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])

            if user["is_admin"]:
                return redirect(url_for("admin"))
            return redirect(url_for("aktivniuzivatele"))
        else:
            return "Špatné přihlašovací údaje!"

    return render_template("SignIn.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/prezentace")
def prezentace():
    return render_template("prezentace.html")

@app.route("/prezentace-investor")
def prezentace_investor():
    return render_template("prezentace-investor.html")

@app.route("/prezentace-kolega")
def prezentace_kolega():
    return render_template("prezentace-kolega.html")

@app.route("/prezentace-novy-uzivatel")
def prezentace_novy_uzivatel():
    return render_template("prezentace-novyuzivatel.html")

# --------------------------
# ADMIN PANEL
# --------------------------
@app.route("/admin")
@admin_required
def admin():
    conn = get_db_connection()
    users = conn.execute(
        "SELECT id, username, email, is_admin FROM users ORDER BY id"
    ).fetchall()
    scores = conn.execute("""
        SELECT s.id, u.username, s.score
        FROM scores s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.score DESC
    """).fetchall()
    conn.close()
    return render_template("admin.html", users=users, scores=scores)

@app.route("/admin/delete_score/<int:score_id>", methods=["POST"])
@admin_required
def admin_delete_score(score_id):
    with db_lock:
        conn = get_db_connection()
        conn.execute("DELETE FROM scores WHERE id = ?", (score_id,))
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))

@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    # Zabraň smazání sebe sama
    if user_id == session.get("user_id"):
        return "Nemůžeš smazat sám sebe!", 400
    with db_lock:
        conn = get_db_connection()
        # Smaž i skóre tohoto uživatele
        conn.execute("DELETE FROM scores WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))

@app.route("/admin/delete_all_scores", methods=["POST"])
@admin_required
def admin_delete_all_scores():
    with db_lock:
        conn = get_db_connection()
        conn.execute("DELETE FROM scores")
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))

# --------------------------
# API pro Pygame
# --------------------------
@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()
    username = data["username"]
    email = data["email"]
    password = generate_password_hash(data["password"])

    with db_lock:
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"success": False, "message": "Uživatel již existuje!"})
        conn.close()
    return jsonify({"success": True})

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({
            "success": True,
            "user_id": user["id"],
            "is_admin": bool(user["is_admin"])
        })
    else:
        return jsonify({"success": False})

@app.route("/api/submit_score", methods=["POST"])
def api_submit_score():
    data = request.get_json()
    user_id = data["user_id"]
    score = data["score"]

    with db_lock:
        conn = get_db_connection()
        conn.execute("INSERT INTO scores (user_id, score) VALUES (?, ?)", (user_id, score))
        conn.commit()
        conn.close()
    return jsonify({"success": True})

@app.route("/api/scoreboard", methods=["GET"])
def api_scoreboard():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT u.username, MAX(s.score) as score
        FROM scores s JOIN users u ON s.user_id = u.id
        GROUP BY u.id
        ORDER BY score DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    data = [{"username": row["username"], "score": row["score"]} for row in rows]
    return jsonify(data)

print(app.url_map)

# --------------------------
if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)
