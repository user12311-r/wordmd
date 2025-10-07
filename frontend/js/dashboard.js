// 仪表盘功能

let trendChart = null;
let categoryChart = null;
let rankChart = null;

// 加载仪表盘
async function loadDashboard() {
    try {
        await Promise.all([
            loadTrendChart(),
            loadCategoryChart(),
            loadRankChart(),
            loadAnomalies()
        ]);
    } catch (error) {
        console.error('加载仪表盘失败:', error);
    }
}

// 加载消费趋势图
async function loadTrendChart() {
    try {
        const data = await analyticsAPI.getTrend('month');
        
        const ctx = document.getElementById('trend-chart');
        if (!ctx) return;
        
        // 销毁旧图表
        if (trendChart) {
            trendChart.destroy();
        }
        
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.data.map(d => d.date),
                datasets: [{
                    label: '消费金额',
                    data: data.data.map(d => d.amount),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('加载趋势图失败:', error);
    }
}

// 加载类别占比图
async function loadCategoryChart() {
    try {
        const data = await analyticsAPI.getCategoryShare();
        
        const ctx = document.getElementById('category-chart');
        if (!ctx) return;
        
        // 销毁旧图表
        if (categoryChart) {
            categoryChart.destroy();
        }
        
        categoryChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.data.map(d => d.category),
                datasets: [{
                    data: data.data.map(d => d.amount),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    } catch (error) {
        console.error('加载类别图失败:', error);
    }
}

// 加载排行榜图
async function loadRankChart() {
    try {
        const data = await analyticsAPI.getRank('category', 10);
        
        const ctx = document.getElementById('rank-chart');
        if (!ctx) return;
        
        // 销毁旧图表
        if (rankChart) {
            rankChart.destroy();
        }
        
        rankChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.data.map(d => d.name),
                datasets: [{
                    label: '消费金额',
                    data: data.data.map(d => d.value),
                    backgroundColor: 'rgba(54, 162, 235, 0.8)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('加载排行榜失败:', error);
    }
}

// 加载异常检测
async function loadAnomalies() {
    try {
        const data = await forecastAPI.detectAnomaly('isolation_forest');
        
        const container = document.getElementById('anomaly-list');
        if (!container) return;
        
        if (data.anomalies.length === 0) {
            container.innerHTML = '<p style="color: #27ae60;">未检测到异常消费</p>';
            return;
        }
        
        container.innerHTML = data.anomalies.slice(0, 5).map(anomaly => `
            <div class="anomaly-item">
                <div><strong>金额:</strong> ¥${anomaly.amount}</div>
                <div><strong>时间:</strong> ${new Date(anomaly.time).toLocaleString()}</div>
                <div><strong>类别:</strong> ${anomaly.category || '未分类'}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载异常检测失败:', error);
        const container = document.getElementById('anomaly-list');
        if (container) {
            container.innerHTML = '<p style="color: #e74c3c;">加载失败</p>';
        }
    }
}

// 刷新仪表盘
function refreshDashboard() {
    loadDashboard();
}

