// Initialize
renderProcessTable('process-table-container');

function handleAddProcess() {
    const arrival = document.getElementById('arrival').value;
    const burst = document.getElementById('burst').value;
    addProcess(null, parseInt(burst) || 0, parseInt(arrival) || 0);
    renderProcessTable('process-table-container');

    document.getElementById('arrival').value = '';
    document.getElementById('burst').value = '';
}

async function runScheduler() {
    const processes = getProcesses();
    const btn = document.querySelector('.primary-btn');
    btn.innerHTML = 'Running…';
    btn.disabled = true;

    try {
        const response = await fetch('/api/fcfs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ processes })
        });

        const data = await response.json();

        renderGanttChart('gantt-chart', data.gantt);
        renderMetricsList('metrics-container', data.metrics);
    } catch (error) {
        console.error('Backend error:', error);
        alert('Could not reach the API. Start the server with python backend/app.py');
    } finally {
        btn.innerHTML = 'Run FCFS';
        btn.disabled = false;
    }
}

setTimeout(runScheduler, 400);
