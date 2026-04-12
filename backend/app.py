import os
from flask import Flask, request, jsonify, send_from_directory
from schedulers.ai_scheduler import ai_schedule
from schedulers.fcfs import fcfs_schedule
from schedulers.sjf import sjf_schedule
from schedulers.round_robin import round_robin_schedule

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_dir, static_url_path='/static')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
