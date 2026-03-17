import json
import os
from datetime import datetime

# Cesty k datovým souborům
DATA_FILE = os.path.join("data", "users.json")
CONFIG_FILE = os.path.join("data", "config.json")

class DataManager:
    """
    Třída pro správu všech dat aplikace (uživatelé, cviky, tréninky, konfigurace).
    Zajišťuje čtení a zápis do JSON souborů.
    """
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self._ensure_data_dir()
        self.audit_file = os.path.join(os.path.dirname(self.data_file), "audit.log")

    def _ensure_data_dir(self):
        """Zajistí existenci složek pro data."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    def load_data(self):
        """Načte data ze souboru users.json. Pokud neexistuje, vytvoří prázdnou strukturu."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    if "__central" not in data:
                        data["__central"] = {
                            "exercises": [],
                            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    return data
            except json.JSONDecodeError:
                return {"__central": {"exercises": [], "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        return {}

    def save_data(self, data):
        """Uloží data do souboru users.json."""
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    # --- Správa uživatelů ---

    def get_user_data(self, username):
        """Vrátí data konkrétního uživatele nebo výchozí strukturu."""
        data = self.load_data()
        return data.get(username, {
            "workouts": [],
            "personal_records": {},
            "progress_data": {},
            "password": "",
            "email": "",
            "role": "user",
            "is_banned": False,
            "bodyweight": 0,
            "bodyweight_history": []
        })

    def add_user(self, username, password, email):
        """Zaregistruje nového uživatele do systému."""
        data = self.load_data()
        if username in data:
            return False, "Uživatel již existuje"
        
        data[username] = {
            "workouts": [],
            "personal_records": {},
            "progress_data": {},
            "password": password,
            "email": email,
            "role": "user",
            "is_banned": False,
            "bodyweight": 0,
            "bodyweight_history": []
        }
        self.save_data(data)
        return True, "Registrace úspěšná"

    def validate_login(self, username, password):
        """
        Ověří přihlašovací údaje uživatele.
        POZNÁMKA: V produkční verzi by se hesla měla hašovat (např. pomocí bcrypt).
        """
        data = self.load_data()
        if username not in data:
            return False
        
        # Kontrola, zda uživatel nemá zakázaný přístup
        if data[username].get("is_banned", False):
            return False
            
        stored_password = data[username].get("password", "")
        return stored_password == password

    def update_user_profile(self, username, new_password=None, new_email=None):
        """Aktualizuje citlivé údaje v profilu uživatele (heslo nebo email)."""
        data = self.load_data()
        if username not in data:
            return False, "Uživatel nenalezen"
        
        if new_password:
            data[username]["password"] = new_password
        if new_email:
            data[username]["email"] = new_email
            
        self.save_data(data)
        return True, "Profil aktualizován"

    # --- Záznamy tréninků a tělesné váhy ---

    def save_workout(self, username, workout_data, note, summary):
        """
        Uloží kompletní záznam o tréninku.
        Zároveň aktualizuje osobní rekordy a data pro grafy progresu.
        """
        data = self.load_data()
        
        if username not in data:
            # Automatické vytvoření profilu, pokud náhodou neexistuje
            data[username] = self.get_user_data(username)
        
        user_data = data[username]
        
        # Vytvoření objektu tréninku s časovým razítkem
        workout_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exercises": workout_data,
            "note": note,
            "summary": summary
        }
        user_data["workouts"].append(workout_entry)
        
        # Zpracování jednotlivých cviků z tréninku
        current_date = datetime.now().strftime("%Y-%m-%d")
        for exercise, sets, reps, weight in workout_data:
            # Aktualizace osobních rekordů (PR)
            if exercise not in user_data["personal_records"] or weight > user_data["personal_records"][exercise]:
                user_data["personal_records"][exercise] = weight
            
            # Příprava dat pro vykreslování grafů (historie váhy u cviku)
            if exercise not in user_data["progress_data"]:
                user_data["progress_data"][exercise] = []
            
            user_data["progress_data"][exercise].append({
                'date': current_date,
                'sets': sets,
                'reps': reps,
                'weight': weight,
                'volume': sets * reps * weight
            })
            
            # Automatická synchronizace s centrálním seznamem cviků
            central = data.get("__central", {"exercises": []})
            if exercise not in central["exercises"]:
                central["exercises"].append(exercise)
                central["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data["__central"] = central
                # Zápis do auditního logu o automatickém přidání cviku
                self._audit("system", "add_exercise_auto", exercise, {"by_user": username})
            
        self.save_data(data)
        return user_data

    def log_bodyweight(self, username, weight):
        """Uloží aktuální tělesnou váhu uživatele a uchová ji v historii pro grafy."""
        data = self.load_data()
        if username not in data:
            return False, "Uživatel nenalezen"
            
        data[username]["bodyweight"] = weight
        
        if "bodyweight_history" not in data[username]:
            data[username]["bodyweight_history"] = []
            
        current_date = datetime.now().strftime("%Y-%m-%d")
        data[username]["bodyweight_history"].append({
            "date": current_date,
            "weight": weight
        })
        
        self.save_data(data)
        return True, "Váha uložena"

    # --- Správa centrálního seznamu cviků ---

    def get_central_exercises(self):
        """Vrátí seřazený seznam všech dostupných cviků v aplikaci."""
        data = self.load_data()
        central = data.get("__central", {"exercises": []})
        return list(sorted(set(central.get("exercises", []))))

    def add_central_exercise(self, exercise_name, created_by):
        """
        Přidá nový cvik do globální databáze.
        Provádí normalizaci názvu a kontrolu duplicit.
        """
        name = self._normalize_exercise_name(exercise_name)
        if not name:
            return False, "Název cviku je prázdný"
        data = self.load_data()
        central = data.get("__central", {"exercises": [], "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        
        # Kontrola existence bez ohledu na velikost písmen (case-insensitive)
        lower_set = {e.lower(): e for e in central.get("exercises", [])}
        if name.lower() in lower_set:
            return False, "Cvik již existuje"
            
        central["exercises"].append(name)
        central["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["__central"] = central
        self.save_data(data)
        # Zápis do auditního logu o manuálním přidání cviku
        self._audit(created_by, "add_exercise", name, {})
        return True, "Cvik přidán"

    def delete_central_exercise(self, exercise_name, actor):
        """
        TRVALÉ SMAZÁNÍ: Odstraní cvik z centrálního seznamu 
        a okamžitě ho vymaže ze všech tréninkových historií všech uživatelů.
        """
        data = self.load_data()
        central = data.get("__central", {"exercises": []})
        if exercise_name not in central.get("exercises", []):
            return False, "Cvik nenalezen"
            
        central["exercises"] = [e for e in central["exercises"] if e != exercise_name]
        central["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["__central"] = central
        
        # Procházení všech uživatelů a čištění jejich tréninků
        for user, udata in list(data.items()):
            if user == "__central":
                continue
            workouts = udata.get("workouts", [])
            for w in workouts:
                ex_list = w.get("exercises", [])
                new_ex_list = []
                for ex in ex_list:
                    try:
                        name = ex[0]
                        if name != exercise_name:
                            new_ex_list.append(ex)
                    except Exception:
                        new_ex_list.append(ex)
                w["exercises"] = new_ex_list
        
        self.save_data(data)
        self._audit(actor, "delete_exercise_hard", exercise_name, {})
        return True, "Cvik trvale odstraněn"

    def clear_central_exercises_and_cleanup(self, actor):
        """
        ÚPLNÁ ČISTKA: Vymaže celý globální seznam cviků 
        a vyčistí historii od všech záznamů, které neexistují.
        """
        data = self.load_data()
        
        data["__central"] = {
            "exercises": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for user, udata in data.items():
            if user == "__central":
                continue
            workouts = udata.get("workouts", [])
            for w in workouts:
                ex_list = w.get("exercises", [])
                new_ex_list = []
                for ex in ex_list:
                    try:
                        name = ex[0]
                        # Zachováme pouze platné názvy, které nezačínají starým prefixem 'DELETED:'
                        if isinstance(name, str) and not name.startswith("DELETED:"):
                            new_ex_list.append(ex)
                        elif not isinstance(name, str):
                            new_ex_list.append(ex)
                    except Exception:
                        new_ex_list.append(ex)
                w["exercises"] = new_ex_list
        
        self.save_data(data)
        self._audit(actor, "clear_central_cleanup", "all", {})
        return True, "Centrální seznam vyčištěn a 'DELETED:' záznamy smazány."

    def reset_central_to_defaults(self, actor):
        """Obnoví centrální seznam cviků na základní sadu (pro testovací účely)."""
        data = self.load_data()
        defaults = ["Bench press", "Dřepy", "Mrtvý tah", "Biceps curl", "Kliky"]
        central = data.get("__central", {"exercises": [], "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        central["exercises"] = defaults
        central["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["__central"] = central
        self.save_data(data)
        self._audit(actor, "reset_central_defaults", ",".join(defaults), {})
        return True, f"Nastaveno {len(defaults)} výchozích cviků"

    # --- Pomocné funkce pro administraci ---

    def _collect_all_exercises(self, data):
        """Sesbírá všechny názvy cviků, které se vyskytují v trénincích uživatelů."""
        names = set()
        for user, udata in data.items():
            if user == "__central":
                continue
            for w in udata.get("workouts", []):
                for ex in w.get("exercises", []):
                    try:
                        n = ex[0]
                        if isinstance(n, str):
                            names.add(n)
                    except Exception:
                        continue
        return names

    def _sync_central(self, data):
        """Synchronizuje centrální seznam s cviky nalezenými v trénincích."""
        if "__central" not in data:
            data["__central"] = {"exercises": [], "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        central = data["__central"]
        existing_list = central.get("exercises", [])
        existing_map = {e.lower(): e for e in existing_list}
        discovered = {self._normalize_exercise_name(n).lower(): self._normalize_exercise_name(n) for n in self._collect_all_exercises(data)}
        
        merged = {}
        for k, v in existing_map.items():
            merged[k] = v
        for k, v in discovered.items():
            if k not in merged:
                merged[k] = v
        union = sorted(merged.values())
        if existing_list != union:
            central["exercises"] = union
            central["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["__central"] = central
            return True
        return False

    # --- Konfigurace a Automatické přihlášení ---

    def get_config(self):
        """Načte konfigurační soubor."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except json.JSONDecodeError:
            pass
        return {}

    def set_autologin(self, username, password, enabled=True):
        """Uloží nebo zruší údaje pro automatické přihlášení."""
        cfg = self.get_config()
        if enabled:
            cfg["autologin"] = {"username": username, "password": password, "enabled": True}
        else:
            cfg["autologin"] = {"enabled": False}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        return True

    def get_autologin(self):
        """Vrátí údaje pro automatické přihlášení, pokud je aktivní."""
        cfg = self.get_config()
        al = cfg.get("autologin", {})
        if al.get("enabled"):
            return al.get("username", ""), al.get("password", "")
        return None

    # --- Audit a Export ---

    def export_audit_csv(self, out_path=os.path.join("data", "audit.csv")):
        """Exportuje auditní záznamy do CSV souboru."""
        rows = []
        if os.path.exists(self.audit_file):
            with open(self.audit_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        rows.append(obj)
                    except Exception:
                        continue
        
        import csv
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        headers = ["timestamp", "actor", "action", "target", "details"]
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow({
                    "timestamp": r.get("timestamp", ""),
                    "actor": r.get("actor", ""),
                    "action": r.get("action", ""),
                    "target": r.get("target", ""),
                    "details": json.dumps(r.get("details", {}), ensure_ascii=False)
                })
        return True, out_path

    def _audit(self, actor, action, target, details):
        """Zapíše akci do auditního logu."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actor": actor,
            "action": action,
            "target": target,
            "details": details
        }
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    # --- Správa uživatelů pro admina ---

    def list_users(self):
        """Vrátí seznam všech uživatelů a jejich základní statistiky."""
        data = self.load_data()
        users = []
        for user, udata in data.items():
            if user == "__central":
                continue
            users.append({
                "username": user,
                "email": udata.get("email", ""),
                "role": udata.get("role", "user"),
                "is_banned": udata.get("is_banned", False),
                "workouts_count": len(udata.get("workouts", []))
            })
        return users

    def get_user_role(self, username):
        """Vrátí roli uživatele (admin/user)."""
        data = self.load_data()
        if username in data:
            return data[username].get("role", "user")
        return "user"

    def ban_user(self, target_username, actor):
        """Zablokuje uživatele."""
        data = self.load_data()
        if target_username not in data:
            return False, "Uživatel nenalezen"
        if target_username == "admin":
            return False, "Nelze zabanovat administrátora"
        data[target_username]["is_banned"] = True
        self.save_data(data)
        self._audit(actor, "ban_user", target_username, {})
        return True, "Uživatel zabanován"

    def unban_user(self, target_username, actor):
        """Odblokuje uživatele."""
        data = self.load_data()
        if target_username not in data:
            return False, "Uživatel nenalezen"
        data[target_username]["is_banned"] = False
        self.save_data(data)
        self._audit(actor, "unban_user", target_username, {})
        return True, "Ban zrušen"

    def delete_user(self, target_username, actor):
        """Smaže uživatelský účet."""
        data = self.load_data()
        if target_username not in data:
            return False, "Uživatel nenalezen"
        if target_username == "admin":
            return False, "Nelze smazat administrátora"
        del data[target_username]
        self.save_data(data)
        self._audit(actor, "delete_user", target_username, {})
        return True, "Uživatel smazán"

    def _normalize_exercise_name(self, name):
        """Normalizuje název cviku (odstraní mezery, nastaví Title Case)."""
        try:
            return " ".join(name.strip().split()).title()
        except Exception:
            return name
