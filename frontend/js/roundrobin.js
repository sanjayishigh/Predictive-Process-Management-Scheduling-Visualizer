// Initialize
renderProcessTable('process-table-container');

function handleAddProcess() {
    const arrival = document.getElementById('arrival').value;
    const burst = document.getElementById('burst').value;
    addProcess(null, parseInt(burst) || 0, parseInt(arrival) || 0);
    renderProcessTable('process-table-container');
    
    // Clear inputs
    document.getElementById('arrival').value = '';
    document.getElementById('burst').value = '';
}

async function runScheduler() {
    const processes = getProcesses();
    const quantum = document.getElementById('quantum').value || 2;
    const btn = document.querySelector('.primary-btn');
    btn.innerHTML = 'Running...';
    btn.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:5000/round_robin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ processes, quantum: parseInt(quantum) })
        });

        const data = await response.json();

        // Render God-Tier Visuals
        renderGanttChart('gantt-chart', data.gantt);
        renderMetricsList('metrics-container', data.metrics);

    } catch (error) {
        console.error("Backend error:", error);
        alert('Failed to connect to backend. Is the server running?');
    } finally {
        btn.innerHTML = 'Run Round Robin';
        btn.disabled = false;
    }
}

// Auto-run on load to show demo
setTimeout(runScheduler, 500);
