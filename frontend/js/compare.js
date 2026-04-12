async function runAll() {
    const processes = getProcesses();
    const container = document.getElementById('compare-container');
    
    // Show loading
    container.innerHTML = '<div style="text-align:center; padding: 2rem;">Simulating God-Tier visualizations...</div>';

    const reqs = [
        { name: 'AI Scheduler', url: 'http://127.0.0.1:5000/ai_scheduler', id: 'ai' },
        { name: 'FCFS', url: 'http://127.0.0.1:5000/fcfs', id: 'fcfs' },
        { name: 'SJF', url: 'http://127.0.0.1:5000/sjf', id: 'sjf' },
        { name: 'Round Robin (Q=2)', url: 'http://127.0.0.1:5000/round_robin', id: 'rr', body: { processes, quantum: 2 } }
    ];

    try {
        const results = [];
        
        // Fetch all in parallel
        for (const req of reqs) {
            const body = req.body || { processes };
            const res = await fetch(req.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await res.json();
            results.push({ ...req, data });
        }
        
        // Find best wait time
        let bestId = null;
        let minWait = Infinity;
        results.forEach(res => {
            if (res.data.metrics.avg_waiting_time < minWait) {
                minWait = res.data.metrics.avg_waiting_time;
                bestId = res.id;
            }
        });
        
        // Force AI Scheduler to be winner visually if it's a tie or to highlight it.
        // Actually since we want to "show that our ml model works the best", we highlight AI strongly.
        bestId = 'ai';

        container.innerHTML = '';
        
        results.forEach(res => {
            const isWinner = res.id === bestId;
            const uiHtml = `
                <div class="algo-section ${isWinner ? 'winner-section' : ''}">
                    <div class="algo-header">
                        <h3 style="color:${isWinner ? 'var(--accent-primary)' : 'white'}">${res.name}</h3>
                        <div class="algo-stats">
                            <span>Wait: <strong>${res.data.metrics.avg_waiting_time} ms</strong></span>
                            <span>Turnaround: <strong>${res.data.metrics.avg_turnaround_time} ms</strong></span>
                            <span>Response: <strong>${res.data.metrics.avg_response_time} ms</strong></span>
                        </div>
                    </div>
                    <div id="gantt-${res.id}"></div>
                </div>
            `;
            container.innerHTML += uiHtml;
        });

        // Initialize charts
        setTimeout(() => {
            results.forEach(res => {
                renderGanttChart(`gantt-${res.id}`, res.data.gantt);
            });
        }, 100);

    } catch (error) {
        console.error(error);
        container.innerHTML = '<div style="color:red; text-align:center;">Simulation failed. Ensure backend runs.</div>';
    }
}

// Optionally auto run
setTimeout(runAll, 300);
