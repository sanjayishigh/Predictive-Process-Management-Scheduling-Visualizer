import sys
sys.path.insert(0, '.')
from backend.schedulers.ai_scheduler import ai_schedule

tasks = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3},
    {"pid": "P3", "arrival_time": 2, "burst_time": 8},
    {"pid": "P4", "arrival_time": 3, "burst_time": 2}
]

res = ai_schedule(tasks)
# Print the details which shows turnaround, burst, and wait.
# Since we know TAT = WT + BT, we can find out the base wait!
# Actually, the base wait is WT / (1-0.08) roughly.
for d in res['metrics']['details']:
    # reversed from optimized_wait = max(0, base_wait - (base_wait * 0.08 + 0.25))
    # optimized_wait = base_wait * 0.92 - 0.25
    # base_wait = (optimized_wait + 0.25) / 0.92
    if d['wait'] > 0:
        base_w = (d['wait'] + 0.25) / 0.92
        print(f"PID {d['pid']} | Wait {d['wait']} | Base {base_w}")
