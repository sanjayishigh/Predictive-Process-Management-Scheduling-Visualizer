async function runAll() {
    const processes = await getProcesses();
    const container = document.getElementById('compare-container');

    container.innerHTML = '<div class="compare-placeholder">Running simulations…</div>';

    const reqs = [
        { name: 'AI scheduler', url: '/api/ai_scheduler', id: 'ai' },
        { name: 'FCFS', url: '/api/fcfs', id: 'fcfs' },
        { name: 'SJF', url: '/api/sjf', id: 'sjf' },
        { name: 'Round Robin (Q = 2)', url: '/api/round_robin', id: 'rr', body: { processes, quantum: 2 } }
    ];

    try {
        const results = await Promise.all(reqs.map(async (req) => {
            const body = req.body || { processes };
            const res = await fetch(req.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!res.ok) {
                throw new Error(`${req.name}: ${res.status}`);
            }
            const data = await res.json();
            return { ...req, data };
        }));

        let bestId = null;
        let minWait = Infinity;
        results.forEach((res) => {
            const w = res.data.metrics.avg_waiting_time;
            if (w < minWait) {
                minWait = w;
                bestId = res.id;
            }
        });

        container.innerHTML = '';

        results.forEach((res) => {
            const isWinner = res.id === bestId;
            const badge = isWinner
                ? '<span class="winner-badge">Lowest avg. wait</span>'
                : '';
            container.innerHTML += `
                <div class="algo-section ${isWinner ? 'winner-section' : ''}">
                    ${badge}
                    <div class="algo-header">
                        <h3>${res.name}</h3>
                        <div class="algo-stats">
                            <span>Wait: <strong>${res.data.metrics.avg_waiting_time}</strong></span>
                            <span>Turnaround: <strong>${res.data.metrics.avg_turnaround_time}</strong></span>
                        </div>
                    </div>
                    <div id="gantt-${res.id}"></div>
                </div>
            `;
        });

        requestAnimationFrame(() => {
            results.forEach((res) => {
                renderGanttChart(`gantt-${res.id}`, res.data.gantt);
            });
        });
    } catch (error) {
        console.error(error);
        container.innerHTML = '<p class="compare-placeholder" style="color:#f87171">Request failed. Start the app with <code>python backend/app.py</code> and try again.</p>';
    }
}
