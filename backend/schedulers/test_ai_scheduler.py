import os
import joblib
import pandas as pd
import torch
import torch.nn as nn

class ConstraintPredictor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
    def forward(self, x):
        return self.network(x)

models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
scaler_path = os.path.join(models_dir, 'feature_scaler.pkl')
model_path = os.path.join(models_dir, 'constraint_predictor.pth')

scaler = joblib.load(scaler_path)
model = ConstraintPredictor(input_dim=7)
model.load_state_dict(torch.load(model_path))
model.eval()

def ai_schedule(processes):
    tasks = processes
    current_time = 0
    completed_tasks = []
    gantt_chart = []
    
    # Initialize remaining times
    for t in tasks:
        t['remaining'] = t['burst_time']
        t['start_time'] = -1
        
    while len(completed_tasks) < len(tasks):
        # Find tasks that have arrived and are not finished
        ready_queue = [t for t in tasks if t['arrival_time'] <= current_time and t['remaining'] > 0]
        
        if not ready_queue:
            # CPU is idle, jump to the arrival of the next task
            future_tasks = [t for t in tasks if t['arrival_time'] > current_time]
            if not future_tasks:
                break
            current_time = min([t['arrival_time'] for t in future_tasks])
            continue
            
        # If only one task is ready, just run it
        if len(ready_queue) == 1:
            selected_task = ready_queue[0]
        else:
            # --- AI PREDICTION LOGIC ---
            df = pd.DataFrame(ready_queue)
            
            # Feature engineering for the model
            df['queue_length'] = len(df) - 1
            df['avg_burst_in_queue'] = df['burst_time'].mean()
            df['time_since_last_task'] = current_time - df['arrival_time']
            df['load_factor'] = df['queue_length'] * df['avg_burst_in_queue']
            df['urgency'] = df['burst_time'] / (df['time_since_last_task'] + 1)
            
            features = ['burst_time', 'arrival_time', 'queue_length', 'avg_burst_in_queue', 'time_since_last_task', 'load_factor', 'urgency']
            X_input = df[features].values
            
            X_scaled = scaler.transform(X_input)
            with torch.no_grad():
                predictions = model(torch.FloatTensor(X_scaled)).numpy().flatten()
            
            df['ai_score'] = predictions
            # Sort by lowest bottleneck score
            best_idx = df['ai_score'].idxmin()
            selected_task = next(t for t in ready_queue if t['pid'] == df.iloc[best_idx]['pid'])

        # --- EXECUTE TASK (1 Time Unit / Quantum) ---
        if selected_task['start_time'] == -1:
            selected_task['start_time'] = current_time
            
        # Log for Gantt Chart (Combine contiguous blocks)
        if len(gantt_chart) > 0 and gantt_chart[-1]['pid'] == selected_task['pid']:
            gantt_chart[-1]['end'] = current_time + 1
            gantt_chart[-1]['duration'] += 1
            gantt_chart[-1]['remaining'] = selected_task['remaining'] - 1
        else:
            gantt_chart.append({
                "pid": selected_task['pid'],
                "start": current_time,
                "end": current_time + 1,
                "duration": 1,
                "remaining": selected_task['remaining'] - 1
            })
            
        selected_task['remaining'] -= 1
        current_time += 1
        
        # Check if finished
        if selected_task['remaining'] == 0:
            selected_task['completion_time'] = current_time
            selected_task['turnaround_time'] = selected_task['completion_time'] - selected_task['arrival_time']
            selected_task['waiting_time'] = selected_task['turnaround_time'] - selected_task['burst_time']
            selected_task['response_time'] = selected_task['start_time'] - selected_task['arrival_time']
            completed_tasks.append(selected_task)

    # Calculate overall metrics
    avg_waiting = sum(t['waiting_time'] for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0
    avg_turnaround = sum(t['turnaround_time'] for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0
    avg_response = sum(t.get('response_time', 0) for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0
    
    # Format details for frontend
    details = []
    for t in completed_tasks:
        details.append({
            'pid': t['pid'],
            'arrival': t['arrival_time'],
            'burst': t['burst_time'],
            'completion': t['completion_time'],
            'turnaround': t['turnaround_time'],
            'wait': t['waiting_time'],
            'response': t.get('response_time', 0)
        })

    return {
        "gantt": gantt_chart,
        "metrics": {
            "avg_waiting_time": round(avg_waiting, 2),
            "avg_turnaround_time": round(avg_turnaround, 2),
            "avg_response_time": round(avg_response, 2),
            "details": details
        },
        "execution_order": []
    }

processes = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3}
]
print(ai_schedule(processes))
