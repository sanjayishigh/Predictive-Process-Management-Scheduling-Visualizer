// Fetch processes from backend database instead of localStorage
async function getProcesses() {
    try {
        const response = await fetch('/api/processes');
        if (response.ok) {
            return await response.json();
        }
    } catch (e) {
        console.error("Failed to fetch processes:", e);
    }
    return [];
}

/**
 * addProcess — async. Inserts into database.
 */
async function addProcess(pid, burst, arrival, priority, io_bound, deadline) {
    // Generate a default PID by counting current processes
    const list = await getProcesses();
    const generatedPid = `P${list.length + 1}`;
    
    const newProcess = {
        pid:          pid || generatedPid,
        burst_time:   burst || Math.floor(Math.random() * 8) + 2,
        arrival_time: arrival || 0,
        priority:     priority !== undefined ? priority : 3,
        io_bound:     io_bound !== undefined ? io_bound : 0,
        deadline:     deadline || ((arrival || 0) + (burst || 0) + 50)
    };

    try {
        await fetch('/api/processes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newProcess)
        });
    } catch (e) {
        console.error("Failed to add process:", e);
    }
}

async function deleteProcess(pid) {
    try {
        await fetch(`/api/processes/${pid}`, { method: 'DELETE' });
    } catch (e) {
        console.error("Failed to delete process:", e);
    }

    // Re-render the table dynamically
    const containerId = 'process-table-container';
    const isAI = window.location.pathname.includes('ai_scheduler');
    await renderProcessTable(containerId, isAI);

    // Trigger dynamic chart refresh across any scheduler page
    if (typeof window.runScheduler === 'function') {
        window.runScheduler();
    } else if (typeof window.runAll === 'function') {
        window.runAll();
    }
}

async function renderProcessTable(containerId, isAI = false) {
    const list = await getProcesses();
    const container = document.getElementById(containerId);
    if (!container) return;

    const aiHeaders = isAI
        ? `<th>Priority</th><th>I/O</th><th>Deadline</th>`
        : '';

    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>PID</th>
                    <th>Arrival</th>
                    <th>Burst</th>
                    ${aiHeaders}
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;

    list.forEach(p => {
        const aiCells = isAI ? `
            <td>${p.priority ?? 3}</td>
            <td>${p.io_bound ? '<span style="color:var(--accent)">Yes</span>' : 'No'}</td>
            <td>${p.deadline ?? '—'}</td>
        ` : '';

        html += `
            <tr>
                <td><strong>${p.pid}</strong></td>
                <td>${p.arrival_time}</td>
                <td>${p.burst_time}</td>
                ${aiCells}
                <td>
                    <button
                        class="btn secondary-btn"
                        style="padding:4px 8px;font-size:0.8rem;background:rgba(239,68,68,0.1);color:#ef4444;border:1px solid rgba(239,68,68,0.2);"
                        onclick="deleteProcess('${p.pid}')">Delete</button>
                </td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}
