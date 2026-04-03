from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'mood_tracker.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                emoji TEXT NOT NULL,
                mood_score INTEGER NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                wellness_score REAL DEFAULT 50.0,
                streak_days INTEGER DEFAULT 0,
                last_entry_date DATE
            )
        ''')
        conn.commit()

# Mood mapping: emoji to numerical score (1-10)
MOOD_MAP = {
    '😄': {'score': 10, 'label': 'Excellent', 'color': '#22c55e'},
    '😊': {'score': 8, 'label': 'Good', 'color': '#84cc16'},
    '😐': {'score': 6, 'label': 'Okay', 'color': '#eab308'},
    '😔': {'score': 4, 'label': 'Low', 'color': '#f97316'},
    '😢': {'score': 2, 'label': 'Sad', 'color': '#ef4444'},
    '😰': {'score': 1, 'label': 'Anxious', 'color': '#dc2626'},
}

@app.route('/api/mood', methods=['POST'])
def log_mood():
    """Log a new mood entry"""
    data = request.json
    user_id = data.get('user_id')
    emoji = data.get('emoji')
    note = data.get('note', '')
    
    if not user_id or not emoji:
        return jsonify({'error': 'user_id and emoji are required'}), 400
    
    if emoji not in MOOD_MAP:
        return jsonify({'error': 'Invalid emoji'}), 400
    
    mood_score = MOOD_MAP[emoji]['score']
    
    with get_db() as conn:
        # Insert mood entry
        conn.execute(
            'INSERT INTO mood_entries (user_id, emoji, mood_score, note) VALUES (?, ?, ?, ?)',
            (user_id, emoji, mood_score, note)
        )
        
        # Update user wellness score and streak
        update_user_stats(conn, user_id, mood_score)
        conn.commit()
    
    return jsonify({
        'message': 'Mood logged successfully',
        'mood_score': mood_score,
        'label': MOOD_MAP[emoji]['label']
    })

def update_user_stats(conn, user_id, new_mood_score):
    """Update wellness score using exponential moving average"""
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    today = datetime.now().date()
    
    if user:
        old_score = user['wellness_score']
        # Exponential moving average (weight recent entries more)
        new_wellness = (old_score * 0.7) + (new_mood_score * 10 * 0.3)
        new_wellness = max(0, min(100, new_wellness))  # Clamp to 0-100
        
        # Update streak
        last_entry = user['last_entry_date']
        if last_entry:
            last_date = datetime.strptime(last_entry, '%Y-%m-%d').date()
            if (today - last_date).days == 1:
                streak = user['streak_days'] + 1
            elif (today - last_date).days == 0:
                streak = user['streak_days']
            else:
                streak = 1
        else:
            streak = 1
        
        conn.execute(
            'UPDATE users SET wellness_score = ?, streak_days = ?, last_entry_date = ? WHERE id = ?',
            (new_wellness, streak, today.isoformat(), user_id)
        )
    else:
        # Create new user
        conn.execute(
            'INSERT INTO users (id, wellness_score, streak_days, last_entry_date) VALUES (?, ?, ?, ?)',
            (user_id, new_mood_score * 10, 1, today.isoformat())
        )

@app.route('/api/mood/history/<user_id>', methods=['GET'])
def get_mood_history(user_id):
    """Get mood history for a user"""
    days = request.args.get('days', 30, type=int)
    
    with get_db() as conn:
        entries = conn.execute('''
            SELECT emoji, mood_score, note, created_at 
            FROM mood_entries 
            WHERE user_id = ? AND created_at >= datetime('now', ?)
            ORDER BY created_at DESC
        ''', (user_id, f'-{days} days')).fetchall()
        
        history = [{
            'emoji': e['emoji'],
            'mood_score': e['mood_score'],
            'note': e['note'],
            'created_at': e['created_at'],
            'label': MOOD_MAP.get(e['emoji'], {}).get('label', 'Unknown')
        } for e in entries]
    
    return jsonify({'history': history})

@app.route('/api/mood/stats/<user_id>', methods=['GET'])
def get_mood_stats(user_id):
    """Get aggregated mood statistics"""
    with get_db() as conn:
        # Get user info
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
        # Get weekly average
        weekly_avg = conn.execute('''
            SELECT AVG(mood_score) as avg_score
            FROM mood_entries 
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
        ''', (user_id,)).fetchone()
        
        # Get mood distribution
        distribution = conn.execute('''
            SELECT emoji, COUNT(*) as count
            FROM mood_entries 
            WHERE user_id = ? AND created_at >= datetime('now', '-30 days')
            GROUP BY emoji
        ''', (user_id,)).fetchall()
        
        # Get daily data for chart (last 7 days)
        daily_data = conn.execute('''
            SELECT DATE(created_at) as date, AVG(mood_score) as avg_score
            FROM mood_entries 
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (user_id,)).fetchall()
    
    return jsonify({
        'wellness_score': user['wellness_score'] if user else 50,
        'streak_days': user['streak_days'] if user else 0,
        'weekly_average': round(weekly_avg['avg_score'] * 10, 1) if weekly_avg['avg_score'] else 50,
        'distribution': {d['emoji']: d['count'] for d in distribution},
        'daily_data': [{'date': d['date'], 'score': round(d['avg_score'] * 10, 1)} for d in daily_data]
    })

@app.route('/api/mood/today/<user_id>', methods=['GET'])
def check_today_entry(user_id):
    """Check if user has logged mood today"""
    with get_db() as conn:
        entry = conn.execute('''
            SELECT * FROM mood_entries 
            WHERE user_id = ? AND DATE(created_at) = DATE('now')
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,)).fetchone()
    
    if entry:
        return jsonify({
            'logged_today': True,
            'emoji': entry['emoji'],
            'mood_score': entry['mood_score']
        })
    return jsonify({'logged_today': False})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
