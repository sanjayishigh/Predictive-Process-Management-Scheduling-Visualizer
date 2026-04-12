/**
 * Gantt chart and metrics rendering
 */

const colors = [
    'color-p1', 'color-p2', 'color-p3', 'color-p4', 
    'color-p5', 'color-p6', 'color-p7', 'color-p8'
];

function getProcessColorClass(pid) {
    // Extract number from PID string (e.g. "P1" -> 1)
    const match = pid.match(/\d+/);
    let index = 0;
    if (match) {
        index = (parseInt(match[0]) - 1) % colors.length;
    } else {
        // Fallback: hash the string
        let hash = 0;
        for (let i = 0; i < pid.length; i++) hash += pid.charCodeAt(i);
        index = hash % colors.length;
    }
    return colors[index];
}

function renderGanttChart(containerId, ganttData) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (!ganttData || ganttData.length === 0) {
        container.innerHTML = '<p style="color:var(--text-secondary); text-align:center; padding: 2rem;">No data to display.</p>';
        return;
    }
    
    // Find absolute total time
    const maxEnd = Math.max(...ganttData.map(b => b.end));
    
    const wrapper = document.createElement('div');
    wrapper.className = 'gantt-wrapper';
    
    const chart = document.createElement('div');
    chart.className = 'gantt-chart-container';
    
    // For staggered animations
    let delayCounter = 0;

    ganttData.forEach(block => {
        // If there's idle time before this block, create a transparent gap block
        // Assuming Gantt blocks are sorted by start time.
        // For simplicity, we use flex-grow based on duration.
        // Wait, Flexbox based on width percentage is better.
        
        const blockDiv = document.createElement('div');
        blockDiv.className = `gantt-block ${getProcessColorClass(block.pid)}`;
        
        const widthPercent = (block.duration / maxEnd) * 100;
        blockDiv.style.width = widthPercent + '%';
        // Add animation delay for stagger
        blockDiv.style.animationDelay = `${delayCounter * 0.1}s`;
        
        // Hide text if block is too small
        if (widthPercent > 3) {
            blockDiv.textContent = block.pid;
        }
        
        const endLabel = document.createElement('span');
        if (block.remaining !== undefined) {
            endLabel.innerHTML = `${block.end} <span style="font-size:0.5rem; opacity:0.6;">(R:${block.remaining})</span>`;
        } else {
            endLabel.textContent = block.end;
        }
        endLabel.style.position = 'absolute';
        endLabel.style.right = '4px';
        endLabel.style.bottom = '2px';
        endLabel.style.fontSize = '0.7rem';
        endLabel.style.opacity = '0.75';
        endLabel.style.pointerEvents = 'none';

        if (widthPercent > 2) {
            blockDiv.appendChild(endLabel);
        }

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.innerHTML = `<strong>${block.pid}</strong><br>Start: ${block.start} | End: ${block.end}<br>Duration: ${block.duration}`;
        
        blockDiv.appendChild(tooltip);
        chart.appendChild(blockDiv);
        
        delayCounter++;
    });
    
    wrapper.appendChild(chart);
    
    // Render timeline labels
    const timeline = document.createElement('div');
    timeline.className = 'gantt-timeline-labels';
    
    const steps = 5;
    for (let i = 0; i <= steps; i++) {
        const tick = document.createElement('div');
        tick.className = 'gantt-time-tick';
        tick.style.left = `${(i / steps) * 100}%`;
        tick.textContent = Math.round((i / steps) * maxEnd);
        timeline.appendChild(tick);
    }
    
    wrapper.appendChild(timeline);
    container.appendChild(wrapper);
}

// Global metric rendering utility
function renderMetricsList(containerId, metricsData) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div style="display:flex; flex-wrap:wrap; gap: 1rem; margin-bottom: 1rem;">
            <div class="glass-panel" style="flex:1; min-width:140px; text-align:center;">
                <div style="font-size:0.8rem; color:var(--text-secondary)">Avg waiting</div>
                <div style="font-size:1.35rem; font-weight:700; color:var(--accent); font-family:var(--font-mono)">${metricsData.avg_waiting_time} ms</div>
            </div>
            <div class="glass-panel" style="flex:1; min-width:140px; text-align:center;">
                <div style="font-size:0.8rem; color:var(--text-secondary)">Avg turnaround</div>
                <div style="font-size:1.35rem; font-weight:700; color:var(--chart-p4); font-family:var(--font-mono)">${metricsData.avg_turnaround_time} ms</div>
            </div>
            <div class="glass-panel" style="flex:1; min-width:140px; text-align:center;">
                <div style="font-size:0.8rem; color:var(--text-secondary)">Avg response</div>
                <div style="font-size:1.35rem; font-weight:700; color:var(--chart-p5); font-family:var(--font-mono)">${metricsData.avg_response_time} ms</div>
            </div>
        </div>
    `;

    if (metricsData.details && metricsData.details.length > 0) {
        let tableHtml = `
            <div style="overflow-x:auto; margin-top: 20px;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>PID</th>
                            <th>Arrival (AT)</th>
                            <th>Burst (BT)</th>
                            <th>Completion (CT)</th>
                            <th>TAT (CT-AT)</th>
                            <th>WT (TAT-BT)</th>
                            <th>RT (1st_Start-AT)</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        metricsData.details.forEach(d => {
            tableHtml += `
                <tr>
                    <td><strong>${d.pid}</strong></td>
                    <td>${d.arrival !== undefined ? d.arrival : '-'}</td>
                    <td>${d.burst !== undefined ? d.burst : '-'}</td>
                    <td>${d.completion !== undefined ? d.completion : '-'}</td>
                    <td>${d.turnaround !== undefined ? d.turnaround : '-'}</td>
                    <td>${(typeof d.wait === 'number' && !Number.isInteger(d.wait)) ? d.wait.toFixed(2) : (d.wait !== undefined ? d.wait : '-')}</td>
                    <td>${d.response !== undefined ? d.response : '-'}</td>
                </tr>
            `;
        });
        
        tableHtml += `</tbody></table></div>`;
        
        // Add explicit mathematical steps for Average calculations
        let waitValues = metricsData.details.map(d => (typeof d.wait === 'number' && !Number.isInteger(d.wait)) ? d.wait.toFixed(2) : (d.wait || 0));
        let turnValues = metricsData.details.map(d => d.turnaround || 0);
        let totalWait = waitValues.reduce((a, b) => parseFloat(a) + parseFloat(b), 0);
        let totalTurn = turnValues.reduce((a, b) => parseFloat(a) + parseFloat(b), 0);
        
        let mathStepsHtml = `
            <div class="glass-panel" style="margin-top: 25px; margin-bottom: 5px; padding: 20px; border-left: 4px solid var(--accent); background: rgba(0,0,0,0.2);">
                <h4 style="margin-top:0; margin-bottom:15px; color:var(--text-primary); font-size: 0.95rem;">Average calculation</h4>
                <div style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-secondary); line-height: 1.8; display: flex; flex-direction: column; gap: 15px;">
                    <div>
                        <span style="display:inline-block; min-width: 260px; color: var(--text-primary);">Waiting (WT = TAT − BT)</span> = ${waitValues.join(' + ')} = ${totalWait.toFixed ? totalWait.toFixed(2) : totalWait} ms<br>
                        <span style="display:inline-block; min-width: 260px; color: var(--text-primary);">Avg waiting</span> = ${totalWait.toFixed ? totalWait.toFixed(2) : totalWait} / ${metricsData.details.length} = <span style="color:var(--accent); font-weight:bold;">${metricsData.avg_waiting_time} ms</span>
                    </div>
                    <div>
                        <span style="display:inline-block; min-width: 260px; color: var(--text-primary);">Turnaround (TAT = CT − AT)</span> = ${turnValues.join(' + ')} = ${totalTurn.toFixed ? totalTurn.toFixed(2) : totalTurn} ms<br>
                        <span style="display:inline-block; min-width: 260px; color: var(--text-primary);">Avg turnaround</span> = ${totalTurn.toFixed ? totalTurn.toFixed(2) : totalTurn} / ${metricsData.details.length} = <span style="color:var(--chart-p4); font-weight:bold;">${metricsData.avg_turnaround_time} ms</span>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML += tableHtml + mathStepsHtml;
    }
}
