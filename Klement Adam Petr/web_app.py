from flask import Flask, render_template, abort, request, jsonify
from data_manager import DataManager

# Inicializace Flask aplikace a správce dat
app = Flask(__name__)
dm = DataManager()

@app.route('/')
def index():
    """Hlavní vstupní stránka (Landing Page)."""
    return render_template('index.html')

# --- Autentizační API ---

@app.route('/register', methods=['POST'])
def register():
    """Endpoint pro registraci nového uživatele přes web."""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Chybějící povinná pole'}), 400
        
    success, msg = dm.add_user(username, password, email)
    if success:
        return jsonify({'message': msg}), 201
    else:
        return jsonify({'error': msg}), 409

@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint pro přihlášení. 
    Vrací uživatelské jméno jako jednoduchý token pro účely dema.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Podpora pro výchozího admina i standardní uživatele
    if dm.validate_login(username, password) or (username == "admin" and password == "1234"):
        return jsonify({'token': username, 'username': username}), 200
    else:
        return jsonify({'error': 'Neplatné jméno nebo heslo'}), 401

# --- API pro Tréninky ---

@app.route('/get_workouts', methods=['GET'])
def get_workouts():
    """Vrátí seznam všech tréninků přihlášeného uživatele pro dashboard."""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Neautorizovaný přístup'}), 401
    
    username = token
    user_data = dm.get_user_data(username)
    
    if not user_data:
        return jsonify({'error': 'Uživatel nenalezen'}), 404
        
    # Transformace dat ze struktury DataManageru pro potřeby frontendu
    frontend_workouts = []
    raw_workouts = user_data.get('workouts', [])
    
    for idx, w_session in enumerate(raw_workouts):
        date = w_session.get('date')
        note = w_session.get('note')
        exercises = w_session.get('exercises', [])
        ex_count = len(exercises)
        
        # Vytvoření krátkého shrnutí (např. "Bench press + 2 další")
        summary_text = ""
        if ex_count > 0:
            first_ex = exercises[0][0]
            if ex_count > 1:
                summary_text = f"{first_ex} + {ex_count - 1} další"
            else:
                summary_text = first_ex
        else:
            summary_text = "Žádné cviky"

        frontend_workouts.append({
            'id': idx,
            'date': date,
            'note': note,
            'summary_text': summary_text,
            'bodyweight': w_session.get('bodyweight', '-')
        })
    
    # Seřazení od nejnovějšího
    frontend_workouts.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({'workouts': frontend_workouts}), 200

@app.route('/get_workout_detail/<int:index>', methods=['GET'])
def get_workout_detail(index):
    """Vrátí detailní data o konkrétním tréninku podle jeho indexu."""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Neautorizovaný přístup'}), 401
    
    username = token
    user_data = dm.get_user_data(username)
    if not user_data:
        return jsonify({'error': 'Uživatel nenalezen'}), 404
        
    raw_workouts = user_data.get('workouts', [])
    if index < 0 or index >= len(raw_workouts):
        return jsonify({'error': 'Trénink nenalezen'}), 404
        
    workout = raw_workouts[index]
    return jsonify(workout), 200

# --- API pro Statistiky a Dashboard ---

@app.route('/get_user_stats', methods=['GET'])
def get_user_stats():
    """Vrátí souhrnné statistiky uživatele pro zobrazení na 'telefonu' na webu."""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Neautorizovaný přístup'}), 401
    
    username = token
    user_data = dm.get_user_data(username)
    if not user_data:
        return jsonify({'error': 'Uživatel nenalezen'}), 404

    # 1. Informace o posledním tréninku
    raw_workouts = user_data.get('workouts', [])
    latest_workout_info = {
        'title': 'Žádný trénink',
        'desc': 'Zatím nic',
        'note': 'Zde se zobrazí poznámka'
    }
    
    if raw_workouts:
        last = raw_workouts[-1]
        exercises = last.get('exercises', [])
        ex_count = len(exercises)
        
        # Dynamický název (Dnes / Datum)
        import datetime
        try:
            w_date = datetime.datetime.strptime(last.get('date', ''), "%Y-%m-%d %H:%M:%S")
            if w_date.date() == datetime.date.today():
                title = "Trénink Dnes"
            else:
                title = w_date.strftime("%d. %m.")
        except:
            title = "Poslední trénink"
            
        # Formátování popisku (První cvik + počet dalších)
        desc = ""
        if ex_count > 0:
            first = exercises[0] # [název, série, opakování, váha]
            if len(first) >= 4:
                desc = f"{first[0]} • {first[1]}×{first[2]} • {first[3]}kg"
                if ex_count > 1:
                    desc += f" (+{ex_count-1})"
            else:
                desc = first[0]
        else:
            desc = "Bez cviků"
            
        latest_workout_info = {
            'title': title,
            'desc': desc,
            'note': last.get('note', '') or 'Bez poznámky'
        }

    # 2. Osobní rekordy (PR)
    prs = user_data.get('personal_records', {})
    pr_text = "Zatím žádné PR"
    if prs:
        try:
            best_lift = max(prs.items(), key=lambda x: x[1])
            pr_text = f"PR: {best_lift[0]} {best_lift[1]} kg"
        except:
            pass

    # 3. Tělesná váha
    bw = user_data.get('bodyweight', '-') 
    bw_text = f"Váha: {bw} kg" if bw != '-' else "Váha: --"
    
    # 4. Celkový počet tréninků a aktivních dní
    total_workouts = len(raw_workouts)
    unique_days = set()
    for w in raw_workouts:
        d_str = w.get('date', '').split(' ')[0]
        if d_str:
            unique_days.add(d_str)
    days_count = len(unique_days)

    return jsonify({
        'latest_workout': latest_workout_info,
        'stats': {
            'pr_text': pr_text,
            'bw_text': bw_text,
            'total_workouts': total_workouts,
            'days_active': days_count
        }
    }), 200

# --- Cesty pro vykreslování šablon (Views) ---

@app.route('/workout_detail')
def workout_detail_view():
    """Zobrazení detailu tréninku."""
    return render_template('workout_detail.html')

@app.route('/settings')
def settings_view():
    """Zobrazení nastavení profilu."""
    return render_template('settings.html')

@app.route('/all_workouts')
def all_workouts_view():
    """Zobrazení kompletní historie tréninků."""
    return render_template('all_workouts.html')

# --- Ostatní API ---

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    """API pro změnu hesla nebo emailu z webového rozhraní."""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Neautorizovaný přístup'}), 401
    
    data = request.get_json()
    new_pass = data.get('password')
    new_email = data.get('email')
    
    if not new_pass and not new_email:
        return jsonify({'message': 'Žádné změny k uložení'}), 200
        
    success, msg = dm.update_user_profile(token, new_pass, new_email)
    if success:
        return jsonify({'message': msg}), 200
    else:
        return jsonify({'error': msg}), 400

@app.route('/ping', methods=['GET'])
def ping():
    """Jednoduchý test dostupnosti serveru."""
    return jsonify({'status': 'ok'}), 200

# --- API pro centrální správu cviků (pro web) ---

@app.route('/api/central_exercises', methods=['GET'])
def central_exercises():
    """Vrátí seznam všech cviků v systému."""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Neautorizovaný přístup'}), 401
    return jsonify({'exercises': dm.get_central_exercises()}), 200

# --- Administrátorské API ---

def _is_admin(token_username):
    """Pomocná funkce pro ověření práv administrátora."""
    role = dm.get_user_role(token_username)
    return token_username == "admin" or role == "admin"

@app.route('/api/admin/delete_exercise', methods=['POST'])
def admin_delete_exercise():
    """Smaže cvik ze systému (pouze pro adminy)."""
    token = request.headers.get('Authorization')
    if not token or not _is_admin(token):
        return jsonify({'error': 'Přístup odepřen'}), 403
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    ok, msg = dm.delete_central_exercise(name, token)
    status = 200 if ok else 400
    return jsonify({'message': msg}), status

@app.route('/api/admin/ban_user', methods=['POST'])
def admin_ban_user():
    """Zablokuje uživatele (pouze pro adminy)."""
    token = request.headers.get('Authorization')
    if not token or not _is_admin(token):
        return jsonify({'error': 'Přístup odepřen'}), 403
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    ok, msg = dm.ban_user(username, token)
    status = 200 if ok else 400
    return jsonify({'message': msg}), status

@app.route('/api/admin/delete_user', methods=['POST'])
def admin_delete_user():
    """Smaže uživatelský účet (pouze pro adminy)."""
    token = request.headers.get('Authorization')
    if not token or not _is_admin(token):
        return jsonify({'error': 'Přístup odepřen'}), 403
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    ok, msg = dm.delete_user(username, token)
    status = 200 if ok else 400
    return jsonify({'message': msg}), status

# Spuštění Flask serveru
if __name__ == '__main__':
    app.run(debug=True, port=5000)
