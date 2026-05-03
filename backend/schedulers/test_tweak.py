import sys
sys.path.insert(0, '.')
from backend.schedulers.ai_scheduler import ai_schedule
from backend.schedulers.sjf import sjf_schedule

processes = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3},
    {"pid": "P3", "arrival_time": 2, "burst_time": 8},
    {"pid": "P4", "arrival_time": 3, "burst_time": 2}
]

print("--- SJF ---")
sjf_res = sjf_schedule([dict(p) for p in processes])
print("SJF Wait:", sjf_res['metrics']['avg_waiting_time'])

print("\n--- AI (Target 7% less than SJF) ---")
# Raw AI wait calculation
ai_res = ai_schedule([dict(p) for p in processes])
print("Current AI Wait:", ai_res['metrics']['avg_waiting_time'])

