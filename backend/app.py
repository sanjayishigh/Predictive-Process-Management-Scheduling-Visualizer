from flask import Flask, request, jsonify
from schedulers.ai_scheduler import ai_schedule
from schedulers.fcfs import fcfs_schedule
from schedulers.sjf import sjf_schedule
from schedulers.round_robin import round_robin_schedule

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/ai_scheduler', methods=['POST'])
def run_ai_scheduler():
    data = request.json
    processes = data['processes']
    result = ai_schedule(processes)
    return jsonify(result)

@app.route('/fcfs', methods=['POST'])
def run_fcfs():
    data = request.json
    processes = data['processes']
    result = fcfs_schedule(processes)
    return jsonify(result)

@app.route('/sjf', methods=['POST'])
def run_sjf():
    data = request.json
    processes = data['processes']
    result = sjf_schedule(processes)
    return jsonify(result)

@app.route('/round_robin', methods=['POST'])
def run_round_robin():
    data = request.json
    processes = data['processes']
    quantum = int(data.get('quantum', 2))
    result = round_robin_schedule(processes, quantum)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)