import json
import os
from datetime import datetime

DATA_FILE = os.path.join("data", "users.json")

class DataManager:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_data(self, data):
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_user_data(self, username):
        data = self.load_data()
        return data.get(username, {
            "workouts": [],
            "personal_records": {},
            "progress_data": {},
            "password": "", # Default for existing users
            "email": ""
        })

    def add_user(self, username, password, email):
        data = self.load_data()
        if username in data:
            return False, "Uživatel již existuje"
        
        data[username] = {
            "workouts": [],
            "personal_records": {},
            "progress_data": {},
            "password": password,
            "email": email
        }
        self.save_data(data)
        return True, "Registrace úspěšná"

    def validate_login(self, username, password):
        data = self.load_data()
        if username not in data:
            return False
        # Simple plaintext check for now (in production use hashing!)
        stored_password = data[username].get("password", "")
        return stored_password == password

    def save_workout(self, username, workout_data, note, summary):
        data = self.load_data()
        
        if username not in data:
            data[username] = {
                "workouts": [],
                "personal_records": {},
                "progress_data": {}
            }
        
        user_data = data[username]
        
        # Create workout entry
        workout_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exercises": workout_data,
            "note": note,
            "summary": summary
        }
        user_data["workouts"].append(workout_entry)
        
        # Update progress and records
        current_date = datetime.now().strftime("%Y-%m-%d")
        for exercise, sets, reps, weight in workout_data:
            # Update Personal Records
            if exercise not in user_data["personal_records"] or weight > user_data["personal_records"][exercise]:
                user_data["personal_records"][exercise] = weight
            
            # Update Progress Data
            if exercise not in user_data["progress_data"]:
                user_data["progress_data"][exercise] = []
            
            user_data["progress_data"][exercise].append({
                'date': current_date,
                'sets': sets,
                'reps': reps,
                'weight': weight,
                'volume': sets * reps * weight
            })
            
        self.save_data(data)
        return user_data

    def update_user_profile(self, username, new_password=None, new_email=None):
        data = self.load_data()
        if username not in data:
            return False, "Uživatel nenalezen"
        
        if new_password:
            data[username]["password"] = new_password
        if new_email:
            data[username]["email"] = new_email
            
        self.save_data(data)
        return True, "Profil aktualizován"

    def log_bodyweight(self, username, weight):
        data = self.load_data()
        if username not in data:
            return False, "Uživatel nenalezen"
            
        # Update current 'bodyweight' field
        data[username]["bodyweight"] = weight
        
        # Add to history if not present
        if "bodyweight_history" not in data[username]:
            data[username]["bodyweight_history"] = []
            
        current_date = datetime.now().strftime("%Y-%m-%d")
        data[username]["bodyweight_history"].append({
            "date": current_date,
            "weight": weight
        })
        
        self.save_data(data)
        return True, "Váha uložena"

    def get_all_users(self):
        return list(self.load_data().keys())
