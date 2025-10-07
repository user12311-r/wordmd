// 数据分析功能

let timeRadarChart = null;
let amountHistChart = null;
let scatterChart = null;

// 加载分析页面
async function loadAnalytics() {
    try {
        await Promise.all([
            loadTimeRadarChart(),
            loadAmountHistChart(),
            loadHeatmap(),
            loadScatterChart()
        ]);
    } catch (error) {
        console.error('加载分析页面失败:', error);
    }
}

// 加载时间分布雷达图
async function loadTimeRadarChart() {
    try {
        const data = await analyticsAPI.getTimeRadar('hour');
        
        const ctx = document.getElementById('time-radar-chart');
        if (!ctx) return;
        
        if (timeRadarChart) {
            timeRadarChart.destroy();
        }
        
        timeRadarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: data.data.map(d => d.label),
                datasets: [{
                    label: '消费金额',
                    data: data.data.map(d => d.value),
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgb(255, 99, 132)',
                    pointBackgroundColor: 'rgb(255, 99, 132)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('加载时间分布图失败:', error);
    }
}

// 加载金额分布柱状图
async function loadAmountHistChart() {
    try {
        const data = await analyticsAPI.getAmountHistogram(10);
        
        const ctx = document.getElementById('amount-hist-chart');
        if (!ctx) return;
        
        if (amountHistChart) {
            amountHistChart.destroy();
        }
        
        amountHistChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.data.map(d => d.range),
                datasets: [{
                    label: '消费次数',
                    data: data.data.map(d => d.count),
                    backgroundColor: 'rgba(75, 192, 192, 0.8)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
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
        console.error('加载金额分布图失败:', error);
    }
}

// 加载热力图
async function loadHeatmap() {
    try {
        const data = await analyticsAPI.getHeatmap();
        
        const container = document.getElementById('heatmap-chart');
        if (!container) return;
        
        // 使用 ECharts 绘制热力图
        const chart = echarts.init(container);
        
        // 如果没有地理坐标数据，显示提示
        if (!data.data || data.data.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #999;">暂无地理位置数据</p>';
            return;
        }
        
        const option = {
            title: {
                text: '消费地点分布',
                left: 'center'
            },
            tooltip: {
                trigger: 'item'
            },
            visualMap: {
                min: 0,
                max: Math.max(...data.data.map(d => d.intensity)),
                calculable: true,
                inRange: {
                    color: ['#50a3ba', '#eac736', '#d94e5d']
                },
                textStyle: {
                    color: '#000'
                }
            },
            series: [{
                type: 'scatter',
                coordinateSystem: 'geo',
                data: data.data.map(d => ({
                    value: [d.lon, d.lat, d.intensity],
                    name: `金额: ${d.amount}`
                })),
                symbolSize: function (val) {
                    return val[2] * 2;
                },
                itemStyle: {
                    color: '#d94e5d'
                }
            }]
        };
        
        chart.setOption(option);
    } catch (error) {
        console.error('加载热力图失败:', error);
        const container = document.getElementById('heatmap-chart');
        if (container) {
            container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #e74c3c;">加载失败</p>';
        }
    }
}

// 加载散点图
async function loadScatterChart() {
    try {
        const data = await analyticsAPI.getLevelScatter();
        
        const ctx = document.getElementById('scatter-chart');
        if (!ctx) return;
        
        if (scatterChart) {
            scatterChart.destroy();
        }
        
        scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '消费水平',
                    data: data.data.map(d => ({
                        x: d.frequency,
                        y: d.avg_amount,
                        label: d.category
                    })),
                    backgroundColor: 'rgba(153, 102, 255, 0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw.label}: 频次=${context.raw.x}, 平均金额=${context.raw.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '消费频次'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '平均金额'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('加载散点图失败:', error);
    }
}

