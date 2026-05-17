def sjf_schedule(processes):
    # Preemptive Shortest Job First (SRTF)
    procs = []
    for p in processes:
        procs.append({
            'pid': p['pid'],
            'burst_time': p['burst_time'],
            'remaining_time': p['burst_time'],
            'arrival_time': p.get('arrival_time', 0),
            'first_start_time': -1
        })
        
    current_time = 0
    gantt = []
    execution_order = []
    completed_processes = []
    
    while procs:
        available = [p for p in procs if p['arrival_time'] <= current_time]
        
        if not available:
            current_time += 1
            continue
            
        # SJF preemptive: pick the one with shortest remaining time
        # Break ties using arrival_time
        available.sort(key=lambda x: (x['remaining_time'], x['arrival_time']))
        current = available[0]
        
        if current['first_start_time'] == -1:
            current['first_start_time'] = current_time
            
        start_time = current_time
        current_time += 1
        current['remaining_time'] -= 1
        
        # Compress Gantt blocks
        if not gantt or gantt[-1]['pid'] != current['pid']:
            gantt.append({
                'pid': current['pid'],
                'start': start_time,
                'end': current_time,
                'duration': 1,
                'remaining': current['remaining_time']
            })
            execution_order.append({
                'pid': current['pid']
            })
        else:
            gantt[-1]['end'] = current_time
            gantt[-1]['duration'] += 1
            gantt[-1]['remaining'] = current['remaining_time']
            
        if current['remaining_time'] == 0:
            completion_time = current_time
            turnaround_time = completion_time - current['arrival_time']
            waiting_time = turnaround_time - current['burst_time']
            
            completed_processes.append({
                'pid': current['pid'],
                'arrival': current['arrival_time'],
                'burst': current['burst_time'],
                'completion': completion_time,
                'wait': waiting_time,
                'turnaround': turnaround_time
            })
            procs.remove(current)

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
