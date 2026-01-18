// Configuration
const REFRESH_INTERVAL = 3000; // 3 seconds
const CHART_UPDATE_INTERVAL = 5000; // 5 seconds
const WARNING_THRESHOLDS = {
    cpu: 85,
    ram: 85,
    disk: 90
};

let historyData = [];

// Update current metrics
async function updateCurrentMetrics() {
    try {
        const response = await fetch('/api/current');
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            updateMetricsDisplay(data);
            updateAlerts(result.alerts);
            updateLastUpdated();
        }
    } catch (error) {
        console.error('Error fetching current metrics:', error);
    }
}

// Update metrics display on cards
function updateMetricsDisplay(data) {
    // CPU
    const cpuPercent = data.cpu_percent;
    document.getElementById('cpu-value').textContent = cpuPercent.toFixed(1) + '%';
    document.getElementById('cpu-bar').style.width = cpuPercent + '%';
    
    // RAM
    const ramPercent = data.ram_percent;
    document.getElementById('ram-value').textContent = ramPercent.toFixed(1) + '%';
    document.getElementById('ram-bar').style.width = ramPercent + '%';
    
    // Disk
    const diskPercent = data.disk_percent;
    document.getElementById('disk-value').textContent = diskPercent.toFixed(1) + '%';
    document.getElementById('disk-bar').style.width = diskPercent + '%';
    
    // Battery
    if (data.battery_percent !== null && data.battery_percent !== '') {
        document.getElementById('battery-value').textContent = data.battery_percent + '%';
        document.getElementById('battery-bar').style.width = data.battery_percent + '%';
    } else {
        document.getElementById('battery-value').textContent = 'N/A';
        document.getElementById('battery-bar').style.width = '0%';
    }
}

// Update alerts display
function updateAlerts(alerts) {
    const alertsContainer = document.getElementById('alerts-container');
    alertsContainer.innerHTML = '';
    
    if (alerts && alerts.length > 0) {
        alerts.forEach(alert => {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert';
            alertDiv.textContent = '⚠️ ' + alert.message;
            alertsContainer.appendChild(alertDiv);
        });
    }
}

// Update last updated time
function updateLastUpdated() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('last-updated').textContent = timeString;
}

// Fetch and update history data
async function updateHistoryData() {
    try {
        const response = await fetch('/api/history/1');
        const result = await response.json();
        
        if (result.success) {
            historyData = result.data;
            updateCharts();
        }
    } catch (error) {
        console.error('Error fetching history:', error);
    }
}

// Update all charts
function updateCharts() {
    if (historyData.length === 0) return;
    
    const timestamps = historyData.map(d => new Date(d.timestamp).toLocaleTimeString());
    const cpuValues = historyData.map(d => d.cpu_percent);
    const ramValues = historyData.map(d => d.ram_percent);
    const diskValues = historyData.map(d => d.disk_percent);
    const rxValues = historyData.map(d => d.net_rx_kbps);
    const txValues = historyData.map(d => d.net_tx_kbps);
    
    // CPU Chart
    plotChart('chart-cpu', timestamps, [cpuValues], ['CPU %'], '#FF9800', 'cpu');
    
    // RAM Chart
    plotChart('chart-ram', timestamps, [ramValues], ['RAM %'], '#2196F3', 'ram');
    
    // Disk Chart
    plotChart('chart-disk', timestamps, [diskValues], ['Disk %'], '#9C27B0', 'disk');
    
    // Network Chart
    plotChart('chart-network', timestamps, [rxValues, txValues], ['RX (Kbps)', 'TX (Kbps)'], 
              ['#4CAF50', '#FF5722'], 'network');
}

// Plot a chart
function plotChart(elementId, x, yArrays, labels, colors, type) {
    const traces = [];
    
    for (let i = 0; i < yArrays.length; i++) {
        traces.push({
            x: x,
            y: yArrays[i],
            name: labels[i],
            mode: 'lines+markers',
            line: { color: Array.isArray(colors) ? colors[i] : colors, width: 2 },
            fill: 'tozeroy',
            hovertemplate: '%{x}<br>' + labels[i] + ': %{y:.1f}<extra></extra>'
        });
    }
    
    const layout = {
        margin: { l: 50, r: 20, t: 20, b: 50 },
        hovermode: 'x unified',
        xaxis: { title: 'Time' },
        yaxis: { 
            title: type === 'network' ? 'Speed (Kbps)' : 'Percentage (%)',
            range: type === 'network' ? undefined : [0, 100]
        },
        plot_bgcolor: '#f9f9f9',
        paper_bgcolor: 'white',
        font: { family: 'Segoe UI, sans-serif', color: '#666' }
    };
    
    Plotly.newPlot(elementId, traces, layout, { responsive: true, displayModeBar: false });
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const result = await response.json();
        
        if (result.success) {
            displayStats(result.data);
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Display statistics
function displayStats(stats) {
    const statsGrid = document.getElementById('stats-grid');
    statsGrid.innerHTML = '';
    
    const statCategories = [
        { type: 'cpu', label: 'CPU' },
        { type: 'ram', label: 'Memory (RAM)' },
        { type: 'disk', label: 'Disk' }
    ];
    
    statCategories.forEach(cat => {
        const stat = stats[cat.type];
        const metrics = [
            { label: 'Current', value: stat.current.toFixed(1) + '%' },
            { label: 'Average', value: stat.avg.toFixed(1) + '%' },
            { label: 'Max', value: stat.max.toFixed(1) + '%' },
            { label: 'Min', value: stat.min.toFixed(1) + '%' }
        ];
        
        metrics.forEach(metric => {
            const item = document.createElement('div');
            item.className = `stat-item ${cat.type}`;
            item.innerHTML = `
                <div class="stat-label">${cat.label} - ${metric.label}</div>
                <div class="stat-value">${metric.value}</div>
            `;
            statsGrid.appendChild(item);
        });
    });
}

// Initialize
function init() {
    console.log('Dashboard initialized');
    updateCurrentMetrics();
    updateHistoryData();
    updateStats();
    
    // Set up intervals
    setInterval(updateCurrentMetrics, REFRESH_INTERVAL);
    setInterval(updateHistoryData, CHART_UPDATE_INTERVAL);
    setInterval(updateStats, CHART_UPDATE_INTERVAL);
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
