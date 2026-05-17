// ── AI Scheduler frontend ──────────────────────────────────────────────────
// Sends full process objects to /api/ai_scheduler and renders the result,
// including the new "Predicted Burst (ms)" column from the LSTM model.

// Initialize process table
renderProcessTable('process-table-container', true);

async function handleAddProcess() {
    const arrival  = parseInt(document.getElementById('arrival').value)  || 0;
    const burst    = parseInt(document.getElementById('burst').value)    || 10;
    const priority = parseInt(document.getElementById('priority').value) || 3;
    const deadline = parseInt(document.getElementById('deadline').value) || 0;
    const io_bound = document.getElementById('io_bound').checked ? 1 : 0;

    // addProcess uses the processStore shared helper
    await addProcess(null, burst, arrival, priority, io_bound, deadline || undefined);
    await renderProcessTable('process-table-container', true);

    // Clear inputs
    document.getElementById('arrival').value  = '';
    document.getElementById('burst').value    = '';
    document.getElementById('priority').value = '';
    document.getElementById('deadline').value = '';
    document.getElementById('io_bound').checked = false;

    runScheduler();
}

async function runScheduler() {
    const rawProcesses = await getProcesses();
    if (!rawProcesses || rawProcesses.length === 0) return;

    const btn = document.querySelector('.primary-btn');
    btn.innerHTML = '⏳ Running…';
    btn.disabled  = true;

    // Build the payload — include all fields the backend needs
    const processes = rawProcesses.map(p => ({
        pid:          p.pid,
        arrival_time: p.arrival_time ?? p.arrival ?? 0,
        burst_time:   p.burst_time   ?? p.burst   ?? 10,
        priority:     p.priority     ?? 3,
        io_bound:     p.io_bound     ?? 0,
        deadline:     p.deadline     ?? (p.arrival_time + p.burst_time + 50),
    }));

    try {
        const response = await fetch('/api/ai_scheduler', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ processes }),
        });

        if (!response.ok) {
            throw new Error(`Server responded ${response.status}`);
        }

        const data = await response.json();

        renderGanttChart('gantt-chart', data.gantt);
        renderMetricsList('metrics-container', data.metrics, true /* showPredictedBurst */);
    } catch (error) {
        console.error('Backend error:', error);
        alert('Could not reach the API.\nStart the server with: python app.py');
    } finally {
        btn.innerHTML = 'Run scheduler';
        btn.disabled  = false;
    }
}

// Kick off automatically after a brief delay
setTimeout(runScheduler, 400);
