from flask import Flask, render_template, abort, request, jsonify
from data_manager import DataManager

app = Flask(__name__)
# CORS(app) # Enable if frontend/backend on different ports
dm = DataManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing fields'}), 400
        
    success, msg = dm.add_user(username, password, email)
    if success:
        return jsonify({'message': msg}), 201
    else:
        return jsonify({'error': msg}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if dm.validate_login(username, password):
        # In a real app, generate a signed JWT here.
        # For this demo, we just return the username as a token.
        return jsonify({'token': username, 'username': username}), 200
    else:
        return jsonify({'error': 'Neplatné jméno nebo heslo'}), 401

@app.route('/get_workouts', methods=['GET'])
def get_workouts():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # In this simple demo, token IS the username
    username = token
    user_data = dm.get_user_data(username)
    
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
        
    # Transform DataManager structure to Frontend structure
    # DataManager: workouts = [{date, note, exercises: [[ex, s, r, w], ...]}, ...]
    # Frontend expects: [{exercise, sets, reps, weight, date, note}, ...]
    
    frontend_workouts = []
    
    raw_workouts = user_data.get('workouts', [])
    for idx, w_session in enumerate(raw_workouts):
        date = w_session.get('date')
        note = w_session.get('note')
        # We return the summary info for the dashboard
        # and the ID (index) for the detail view
        
        # Calculate a simple "summary" string if not present
        # e.g. "Bench press + 2 others"
        exercises = w_session.get('exercises', [])
        ex_count = len(exercises)
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
            'bodyweight': w_session.get('bodyweight', '-') # Placeholder if we add bodyweight later
        })
    
    # Sort by date descending
    frontend_workouts.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({'workouts': frontend_workouts}), 200

@app.route('/get_workout_detail/<int:index>', methods=['GET'])
def get_workout_detail(index):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = token
    user_data = dm.get_user_data(username)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
        
    raw_workouts = user_data.get('workouts', [])
    if index < 0 or index >= len(raw_workouts):
        return jsonify({'error': 'Workout not found'}), 404
        
    workout = raw_workouts[index]
    return jsonify(workout), 200

@app.route('/get_user_stats', methods=['GET'])
def get_user_stats():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = token
    user_data = dm.get_user_data(username)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404

    # 1. Latest workout summary
    raw_workouts = user_data.get('workouts', [])
    latest_workout_info = {
        'title': 'Žádný trénink',
        'desc': 'Zatím nic',
        'note': 'Zde se zobrazí poznámka'
    }
    
    if raw_workouts:
        # Get last one
        last = raw_workouts[-1]
        
        # Format title
        exercises = last.get('exercises', [])
        ex_count = len(exercises)
        title = "Trénink dnes" # Or date
        
        # Simple date check (is it today?)
        import datetime
        try:
            w_date = datetime.datetime.strptime(last.get('date', ''), "%Y-%m-%d %H:%M:%S")
            if w_date.date() == datetime.date.today():
                title = "Trénink Dnes"
            else:
                title = w_date.strftime("%d. %m.")
        except:
            title = "Poslední trénink"
            
        # Format description
        desc = ""
        if ex_count > 0:
            # Show first exercise details
            # [name, sets, reps, weight]
            first = exercises[0]
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

    # 2. PRs
    prs = user_data.get('personal_records', {})
    # Pick top one or just list a few
    pr_text = "Zatím žádné PR"
    if prs:
        # Sort by weight desc just for fun, or just pick random
        # Let's just pick the "biggest" number found
        try:
            best_lift = max(prs.items(), key=lambda x: x[1])
            pr_text = f"PR: {best_lift[0]} {best_lift[1]} kg"
        except:
            pass

    # 3. Bodyweight (Placeholder)
    bw = user_data.get('bodyweight', '-') 
    bw_text = f"Váha: {bw} kg" if bw != '-' else "Váha: --"
    
    # 4. Total workouts
    total_workouts = len(raw_workouts)
    
    # Count unique days
    unique_days = set()
    for w in raw_workouts:
        d_str = w.get('date', '').split(' ')[0] # just YYYY-MM-DD
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

@app.route('/workout_detail')
def workout_detail_view():
    return render_template('workout_detail.html')

@app.route('/settings')
def settings_view():
    return render_template('settings.html')

@app.route('/all_workouts')
def all_workouts_view():
    return render_template('all_workouts.html')

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    new_pass = data.get('password')
    new_email = data.get('email')
    
    # Basic validation
    if not new_pass and not new_email:
        return jsonify({'message': 'No changes'}), 200
        
    success, msg = dm.update_user_profile(token, new_pass, new_email)
    if success:
        return jsonify({'message': msg}), 200
    else:
        return jsonify({'error': msg}), 400

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'}), 200

# Keep old route for compatibility if needed, or remove
@app.route('/user/<username>')
def user_profile(username):
    data = dm.get_user_data(username)
    if not data:
        abort(404)
    return render_template('user.html', username=username, data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
