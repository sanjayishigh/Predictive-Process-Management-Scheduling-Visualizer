def round_robin_schedule(processes, time_quantum=2):
    # Deep copy
    procs = []
    for p in processes:
        procs.append({
            'pid': p['pid'],
            'burst_time': p['burst_time'],
            'remaining_time': p['burst_time'],
            'arrival_time': p.get('arrival_time', 0),
            'first_start_time': -1
        })
        
    procs.sort(key=lambda x: x['arrival_time'])
    
    current_time = 0
    gantt = []
    execution_order = []
    completed_processes = []
    
    queue = []
    idx = 0
    n = len(procs)
    
    # Push the first arrived processes to queue
    if n > 0:
        current_time = procs[0]['arrival_time']
        while idx < n and procs[idx]['arrival_time'] <= current_time:
            queue.append(procs[idx])
            idx += 1
            
    while queue:
        current = queue.pop(0)
        
        start_time = max(current_time, current['arrival_time'])
        
        if current['first_start_time'] == -1:
            current['first_start_time'] = start_time
            
        # Execute for time quantum or remaining time, whichever is smaller
        execution_time = min(time_quantum, current['remaining_time'])
        end_time = start_time + execution_time
        current['remaining_time'] -= execution_time
        
        gantt.append({
            'pid': current['pid'],
            'start': start_time,
            'end': end_time,
            'duration': execution_time,
            'remaining': current['remaining_time']
        })
        
        execution_order.append({
            'pid': current['pid']
        })
        
        current_time = end_time
        
        # Check if any new processes arrived while this was executing
        while idx < n and procs[idx]['arrival_time'] <= current_time:
            queue.append(procs[idx])
            idx += 1
            
        if current['remaining_time'] > 0:
            queue.append(current)
        else:
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
            
        # If queue is empty but there are still processes that will arrive later
        if not queue and idx < n:
            current_time = procs[idx]['arrival_time']
            while idx < n and procs[idx]['arrival_time'] <= current_time:
                queue.append(procs[idx])
                idx += 1

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
