def fcfs_schedule(processes):
    # Deep copy to avoid mutating original dictionary
    procs = []
    for p in processes:
        procs.append({
            'pid': p['pid'],
            'burst_time': p['burst_time'],
            'arrival_time': p.get('arrival_time', 0)
        })
        
    # Sort by arrival time
    procs.sort(key=lambda x: x['arrival_time'])
    
    current_time = 0
    gantt = []
    execution_order = []
    completed_processes = []
    
    for current in procs:
        start_time = max(current_time, current['arrival_time'])
        burst = current['burst_time']
        end_time = start_time + burst
        
        gantt.append({
            'pid': current['pid'],
            'start': start_time,
            'end': end_time,
            'duration': burst,
            'remaining': 0
        })
        
        execution_order.append({
            'pid': current['pid']
        })
        
        completion_time = end_time
        turnaround_time = completion_time - current['arrival_time']
        waiting_time = turnaround_time - burst
        
        completed_processes.append({
            'pid': current['pid'],
            'arrival': current['arrival_time'],
            'burst': current['burst_time'],
            'completion': completion_time,
            'wait': waiting_time,
            'turnaround': turnaround_time
        })
        
        current_time = end_time
        
    total_wait = sum(p['wait'] for p in completed_processes)
    total_turnaround = sum(p['turnaround'] for p in completed_processes)
    
    metrics = {
        'avg_waiting_time': round(total_wait / len(completed_processes), 2) if completed_processes else 0,
        'avg_turnaround_time': round(total_turnaround / len(completed_processes), 2) if completed_processes else 0,
        'details': completed_processes
    }
    
    return {
        'execution_order': execution_order,
        'gantt': gantt,
        'metrics': metrics
    }
