import sys
import os

# Ensure the backend directory is in the path
backend_dir = os.path.dirname(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from schedulers.ai_scheduler import ai_schedule
import json

def test_ai_scheduler():
    print("Testing PPO + LSTM AI Scheduler with User Example...")
    processes = [
        {"pid": "P1", "arrival_time": 1, "burst_time": 7, "priority": 5, "io_bound": 0, "deadline": 11},
        {"pid": "P2", "arrival_time": 0, "burst_time": 4, "priority": 1, "io_bound": 1, "deadline": 6},
        {"pid": "P3", "arrival_time": 2, "burst_time": 7, "priority": 5, "io_bound": 0, "deadline": 17},
        {"pid": "P4", "arrival_time": 2, "burst_time": 8, "priority": 4, "io_bound": 0, "deadline": 16},
        {"pid": "P5", "arrival_time": 1, "burst_time": 7, "priority": 2, "io_bound": 0, "deadline": 21}
    ]
    
    result = ai_schedule(processes)
    print("AI Scheduler result:")
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    test_ai_scheduler()
