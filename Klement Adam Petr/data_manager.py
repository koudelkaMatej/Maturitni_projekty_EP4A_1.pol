import sqlite3
import os
import json
from datetime import datetime

# Cesty k datovým souborům
DB_FILE = os.path.join("data", "fitness.db")
CONFIG_FILE = os.path.join("data", "config.json")

class DataManager:
    """
    Třída pro správu všech dat aplikace pomocí SQLite databáze.
    Splňuje požadavky na relační databázi (vztahy 1:N, M:N, JOINy).
    """
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self._ensure_data_dir()
        self._init_db()
        self.audit_file = os.path.join(os.path.dirname(self.db_file), "audit.log")

    def _ensure_data_dir(self):
        """Zajistí existenci složek pro data."""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    def _get_connection(self):
        """Vytvoří a vrátí připojení k SQLite databázi."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # Umožňuje přístup k výsledkům přes názvy sloupců
        return conn

    def _init_db(self):
        """Inicializuje schéma databáze, pokud neexistuje."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Povolení cizích klíčů (Foreign Keys)
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Tabulka UŽIVATELŮ
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                is_banned INTEGER DEFAULT 0,
                bodyweight REAL DEFAULT 0
            );
        """.replace("AUTO_INCREMENT", "AUTOINCREMENT")) # SQLite používá AUTOINCREMENT

        # Tabulka CVIKŮ (Globální seznam)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tabulka TRÉNINKŮ (Vztah 1:N s uživatelem)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                note TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # Tabulka POLOŽEK TRÉNINKU (Vztah M:N mezi tréninkem a cvikem)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL NOT NULL,
                FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
            );
        """)

        # Tabulka HISTORIE VÁHY (Vztah 1:N s uživatelem)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bodyweight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        conn.commit()
        conn.close()

    # --- Správa uživatelů ---

    def add_user(self, username, password, email):
        """Zaregistruje nového uživatele do SQL databáze."""
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
            conn.commit()
            return True, "Registrace úspěšná"
        except sqlite3.IntegrityError:
            return False, "Uživatel již existuje"
        finally:
            conn.close()

    def validate_login(self, username, password):
        """Ověří přihlašovací údaje pomocí SQL SELECT."""
        conn = self._get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ? AND is_banned = 0",
            (username, password)
        ).fetchone()
        conn.close()
        return user is not None

    def get_user_role(self, username):
        """Vrátí roli uživatele."""
        conn = self._get_connection()
        user = conn.execute("SELECT role FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        return user['role'] if user else 'user'

    def get_user_data(self, username):
        """
        Simuluje původní strukturu dat pro zpětnou kompatibilitu.
        Využívá JOINy pro sesbírání všech informací.
        """
        conn = self._get_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            conn.close()
            return None
        
        user_id = user['id']
        
        # Načtení tréninků (1:N)
        workouts_rows = conn.execute("SELECT * FROM workouts WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()
        workouts = []
        for w in workouts_rows:
            # Načtení položek tréninku přes JOIN s tabulkou cviků (M:N)
            items = conn.execute("""
                SELECT e.name, wi.sets, wi.reps, wi.weight 
                FROM workout_items wi
                JOIN exercises e ON wi.exercise_id = e.id
                WHERE wi.workout_id = ?
            """, (w['id'],)).fetchall()
            
            ex_list = [[i['name'], i['sets'], i['reps'], i['weight']] for i in items]
            summary = "\n".join([f"{i[0]} - {i[1]}x{i[2]}, {i[3]}kg" for i in ex_list])
            
            workouts.append({
                "id": w['id'],
                "date": w['date'],
                "note": w['note'],
                "exercises": ex_list,
                "summary": summary
            })

        # Osobní rekordy (Výpočet přes MAX a GROUP BY)
        pr_rows = conn.execute("""
            SELECT e.name, MAX(wi.weight) as max_weight
            FROM workout_items wi
            JOIN exercises e ON wi.exercise_id = e.id
            JOIN workouts w ON wi.workout_id = w.id
            WHERE w.user_id = ?
            GROUP BY e.name
        """, (user_id,)).fetchall()
        personal_records = {r['name']: r['max_weight'] for r in pr_rows}

        # Data pro grafy (Progres)
        progress_rows = conn.execute("""
            SELECT e.name, w.date, wi.sets, wi.reps, wi.weight, (wi.sets * wi.reps * wi.weight) as volume
            FROM workout_items wi
            JOIN exercises e ON wi.exercise_id = e.id
            JOIN workouts w ON wi.workout_id = w.id
            WHERE w.user_id = ?
            ORDER BY w.date ASC
        """, (user_id,)).fetchall()
        
        progress_data = {}
        for r in progress_rows:
            if r['name'] not in progress_data:
                progress_data[r['name']] = []
            progress_data[r['name']].append({
                'date': r['date'], 'sets': r['sets'], 'reps': r['reps'], 'weight': r['weight'], 'volume': r['volume']
            })

        # Historie váhy
        bw_rows = conn.execute("SELECT weight, date FROM bodyweight_history WHERE user_id = ? ORDER BY date ASC", (user_id,)).fetchall()
        bodyweight_history = [{'weight': r['weight'], 'date': r['date']} for r in bw_rows]

        conn.close()
        return {
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "is_banned": bool(user['is_banned']),
            "bodyweight": user['bodyweight'],
            "workouts": workouts,
            "personal_records": personal_records,
            "progress_data": progress_data,
            "bodyweight_history": bodyweight_history
        }

    # --- Záznamy tréninků a váhy ---

    def save_workout(self, username, workout_data, note, summary):
        """Uloží trénink do SQL tabulek (workouts a workout_items)."""
        conn = self._get_connection()
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            conn.close()
            return None
        
        user_id = user['id']
        cursor = conn.cursor()
        
        # 1. Vytvoření záznamu tréninku
        cursor.execute(
            "INSERT INTO workouts (user_id, note) VALUES (?, ?)",
            (user_id, note)
        )
        workout_id = cursor.lastrowid
        
        # 2. Vložení jednotlivých cviků (položek)
        for exercise_name, sets, reps, weight in workout_data:
            # Získání nebo vytvoření ID cviku
            ex = conn.execute("SELECT id FROM exercises WHERE name = ?", (exercise_name,)).fetchone()
            if not ex:
                cursor.execute("INSERT INTO exercises (name) VALUES (?)", (exercise_name,))
                ex_id = cursor.lastrowid
            else:
                ex_id = ex['id']
            
            cursor.execute(
                "INSERT INTO workout_items (workout_id, exercise_id, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
                (workout_id, ex_id, sets, reps, weight)
            )
            
        conn.commit()
        conn.close()
        return self.get_user_data(username)

    def log_bodyweight(self, username, weight):
        """Uloží váhu do historie pomocí SQL INSERT a aktualizuje profil."""
        conn = self._get_connection()
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            conn.close()
            return False, "Uživatel nenalezen"
        
        user_id = user['id']
        conn.execute("INSERT INTO bodyweight_history (user_id, weight) VALUES (?, ?)", (user_id, weight))
        conn.execute("UPDATE users SET bodyweight = ? WHERE id = ?", (weight, user_id))
        conn.commit()
        conn.close()
        return True, "Váha uložena"

    # --- Správa centrálního seznamu cviků ---

    def get_central_exercises(self):
        """Vrátí seznam všech cviků z SQL tabulky exercises."""
        conn = self._get_connection()
        rows = conn.execute("SELECT name FROM exercises ORDER BY name ASC").fetchall()
        conn.close()
        return [r['name'] for r in rows]

    def add_central_exercise(self, exercise_name, created_by):
        """Přidá nový cvik do tabulky exercises."""
        name = self._normalize_exercise_name(exercise_name)
        if not name: return False, "Prázdný název"
        
        conn = self._get_connection()
        try:
            conn.execute("INSERT INTO exercises (name) VALUES (?)", (name,))
            conn.commit()
            self._audit(created_by, "add_exercise", name, {})
            return True, "Cvik přidán"
        except sqlite3.IntegrityError:
            return False, "Cvik již existuje"
        finally:
            conn.close()

    def delete_central_exercise(self, exercise_name, actor):
        """Smaže cvik z globálního seznamu (díky ON DELETE CASCADE smaže i položky v trénincích)."""
        conn = self._get_connection()
        res = conn.execute("DELETE FROM exercises WHERE name = ?", (exercise_name,))
        conn.commit()
        success = res.rowcount > 0
        conn.close()
        if success:
            self._audit(actor, "delete_exercise_sql", exercise_name, {})
            return True, "Cvik smazán z celé databáze"
        return False, "Cvik nenalezen"

    # --- Administrace uživatelů ---

    def list_users(self):
        """Vrátí seznam uživatelů se statistikami pomocí SQL JOIN a COUNT."""
        conn = self._get_connection()
        rows = conn.execute("""
            SELECT u.username, u.email, u.role, u.is_banned, COUNT(w.id) as workouts_count
            FROM users u
            LEFT JOIN workouts w ON u.id = w.user_id
            GROUP BY u.id
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def ban_user(self, target_username, actor):
        """Zablokuje uživatele v DB."""
        if target_username == "admin": return False, "Nelze zabanovat admina"
        conn = self._get_connection()
        conn.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (target_username,))
        conn.commit()
        conn.close()
        self._audit(actor, "ban_user", target_username, {})
        return True, "Uživatel zabanován"

    def unban_user(self, target_username, actor):
        """Odblokuje uživatele v DB."""
        conn = self._get_connection()
        conn.execute("UPDATE users SET is_banned = 0 WHERE username = ?", (target_username,))
        conn.commit()
        conn.close()
        self._audit(actor, "unban_user", target_username, {})
        return True, "Ban zrušen"

    def delete_user(self, target_username, actor):
        """Smaže uživatele (díky ON DELETE CASCADE se smaže i celá jeho historie)."""
        if target_username == "admin": return False, "Nelze smazat admina"
        conn = self._get_connection()
        conn.execute("DELETE FROM users WHERE username = ?", (target_username,))
        conn.commit()
        conn.close()
        self._audit(actor, "delete_user", target_username, {})
        return True, "Uživatel i jeho historie smazána"

    # --- Pomocné funkce (Zůstávají stejné) ---

    def _normalize_exercise_name(self, name):
        try: return " ".join(name.strip().split()).title()
        except: return name

    def _audit(self, actor, action, target, details):
        entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "actor": actor, "action": action, "target": target, "details": details}
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except: pass

    def get_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        return {}

    def set_autologin(self, username, password, enabled=True):
        cfg = self.get_config()
        cfg["autologin"] = {"username": username, "password": password, "enabled": enabled}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=4)

    def get_autologin(self):
        cfg = self.get_config()
        al = cfg.get("autologin", {})
        if al.get("enabled"): return al.get("username", ""), al.get("password", "")
        return None

    def export_audit_csv(self, out_path=os.path.join("data", "audit.csv")):
        import csv
        rows = []
        if os.path.exists(self.audit_file):
            with open(self.audit_file, "r", encoding="utf-8") as f:
                for line in f:
                    try: rows.append(json.loads(line.strip()))
                    except: continue
        headers = ["timestamp", "actor", "action", "target", "details"]
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: (json.dumps(r.get(k, {}), ensure_ascii=False) if k == "details" else r.get(k, "")) for k in headers})
        return True, out_path

    def clear_central_exercises_and_cleanup(self, actor):
        """Vymaže všechny cviky a tréninky (SQL TRUNCATE simulace)."""
        conn = self._get_connection()
        conn.execute("DELETE FROM exercises")
        conn.execute("DELETE FROM workouts")
        conn.commit()
        conn.close()
        self._audit(actor, "clear_all_sql", "all", {})
        return True, "Celá databáze byla vyčištěna."

    def update_user_profile(self, username, new_password=None, new_email=None):
        conn = self._get_connection()
        if new_password and new_email:
            conn.execute("UPDATE users SET password = ?, email = ? WHERE username = ?", (new_password, new_email, username))
        elif new_password:
            conn.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        elif new_email:
            conn.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, username))
        conn.commit()
        conn.close()
        return True, "Profil aktualizován"
