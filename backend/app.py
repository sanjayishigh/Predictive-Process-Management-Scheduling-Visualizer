import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from schedulers.ai_scheduler import ai_schedule
from schedulers.fcfs import fcfs_schedule
from schedulers.sjf import sjf_schedule
from schedulers.round_robin import round_robin_schedule

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_dir, static_url_path='/static')

# --- Database Setup ---
DB_PATH = os.path.join(os.path.dirname(__file__), 'processes.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pid TEXT UNIQUE,
            burst_time INTEGER,
            arrival_time INTEGER,
            priority INTEGER,
            io_bound INTEGER,
            deadline INTEGER
        )
    ''')
    # If the table is completely empty, we can optionally seed it here, 
    # but the frontend usually provides defaults if none exist.
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- Process CRUD Routes ---
@app.route('/api/processes', methods=['GET'])
def get_processes():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM processes')
    rows = c.fetchall()
    conn.close()
    
    processes = []
    for row in rows:
        processes.append({
            'pid': row['pid'],
            'burst_time': row['burst_time'],
            'arrival_time': row['arrival_time'],
            'priority': row['priority'],
            'io_bound': row['io_bound'],
            'deadline': row['deadline']
        })
    return jsonify(processes)

@app.route('/api/processes', methods=['POST'])
def add_process():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO processes (pid, burst_time, arrival_time, priority, io_bound, deadline)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('pid'),
            data.get('burst_time', 10),
            data.get('arrival_time', 0),
            data.get('priority', 3),
            data.get('io_bound', 0),
            data.get('deadline', 0)
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Process with this PID already exists'}), 400
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/api/processes/<pid>', methods=['DELETE'])
def delete_process(pid):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM processes WHERE pid = ?', (pid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 200

# API routes must be registered before the catch-all static handler so /api/* always hits these.
@app.route('/api/ai_scheduler', methods=['POST'])
def run_ai_scheduler():
    data = request.json
    processes = data['processes']
    result = ai_schedule(processes)
    return jsonify(result)

@app.route('/api/fcfs', methods=['POST'])
def run_fcfs():
    data = request.json
    processes = data['processes']
    result = fcfs_schedule(processes)
    return jsonify(result)

@app.route('/api/sjf', methods=['POST'])
def run_sjf():
    data = request.json
    processes = data['processes']
    result = sjf_schedule(processes)
    return jsonify(result)

@app.route('/api/round_robin', methods=['POST'])
def run_round_robin():
    data = request.json
    processes = data['processes']
    quantum = int(data.get('quantum', 2))
    result = round_robin_schedule(processes, quantum)
    return jsonify(result)

@app.route('/')
def route_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def route_static(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404

    full = os.path.join(app.static_folder, path)
    if os.path.isfile(full):
        return send_from_directory(app.static_folder, path)

    html_candidate = os.path.join(app.static_folder, f'{path}.html')
    if os.path.isfile(html_candidate):
        return send_from_directory(app.static_folder, f'{path}.html')

    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
