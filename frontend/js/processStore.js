// Default workload for demos and comparison
let processes = [
    { pid: "P1", burst_time: 10, arrival_time: 0, waiting_time: 2, task_type: 1 },
    { pid: "P2", burst_time: 2, arrival_time: 1, waiting_time: 4, task_type: 0 },
    { pid: "P3", burst_time: 3, arrival_time: 2, waiting_time: 1, task_type: 2 },
    { pid: "P4", burst_time: 5, arrival_time: 4, waiting_time: 3, task_type: 1 },
    { pid: "P5", burst_time: 1, arrival_time: 5, waiting_time: 2, task_type: 0 }
];

function getProcesses() {
    const saved = localStorage.getItem('os_processes');
    if (saved) {
        try {
            processes = JSON.parse(saved);
        } catch(e) {}
    }
    return processes;
}

function saveProcesses(new_processes) {
    processes = new_processes;
    localStorage.setItem('os_processes', JSON.stringify(processes));
}

function addProcess(pid, burst, arrival) {
    const list = getProcesses();
    list.push({
        pid: pid || `P${list.length + 1}`,
        burst_time: burst || Math.floor(Math.random() * 8) + 2,
        arrival_time: arrival || Math.floor(Math.random() * 10),
        waiting_time: Math.floor(Math.random() * 5),
        task_type: Math.floor(Math.random() * 3)
    });
    saveProcesses(list);
    return list;
}

function deleteProcess(pid) {
    let list = getProcesses();
    list = list.filter(p => p.pid !== pid);
    saveProcesses(list);
    
    // Re-render the table dynamically
    const containerId = 'process-table-container';
    const isAI = window.location.pathname.includes('ai_scheduler');
    renderProcessTable(containerId, isAI);
    
    // Trigger dynamic chart refresh across any scheduler page
    if (typeof window.runScheduler === 'function') {
        window.runScheduler();
    } else if (typeof window.runAll === 'function') {
        window.runAll();
    }
}

function renderProcessTable(containerId, isAI = false) {
    const list = getProcesses();
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>PID</th>
                    <th>Arrival</th>
                    <th>Burst</th>
                    ${isAI ? '<th>Task Type</th>' : ''}
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    list.forEach(p => {
        html += `
            <tr>
                <td><strong>${p.pid}</strong></td>
                <td>${p.arrival_time}</td>
                <td>${p.burst_time}</td>
                ${isAI ? `<td>${p.task_type || 0}</td>` : ''}
                <td>
                    <button class="btn secondary-btn" style="padding: 4px 8px; font-size: 0.8rem; background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2);" onclick="deleteProcess('${p.pid}')">Delete</button>
                </td>
            </tr>
        `;
    });
    
    html += `</tbody></table>`;
    container.innerHTML = html;
}
