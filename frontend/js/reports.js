// 报告管理功能

// 加载报告页面
async function loadReportsPage() {
    await loadReportsList();
}

// 生成报告表单处理
document.getElementById('generate-report-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('report-title').value;
    const format = document.getElementById('report-format').value;
    
    try {
        showMessage('正在生成报告，请稍候...', 'info');
        
        const data = await reportsAPI.generate(title, format);
        
        showMessage('报告生成成功！', 'success');
        
        // 刷新报告列表
        await loadReportsList();
        
    } catch (error) {
        showMessage('生成报告失败: ' + error.message, 'error');
    }
});

// 加载报告列表
async function loadReportsList() {
    try {
        const data = await reportsAPI.getReports();
        
        const container = document.getElementById('reports-list');
        if (!container) return;
        
        if (data.reports.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999;">暂无报告</p>';
            return;
        }
        
        container.innerHTML = data.reports.map(report => `
            <div class="report-item">
                <div>
                    <strong>${report.title}</strong>
                    <div style="font-size: 0.9rem; color: #666;">
                        ${new Date(report.created_at).toLocaleString()} | ${report.format.toUpperCase()}
                    </div>
                </div>
                <div>
                    <button class="btn btn-secondary" onclick="downloadReport(${report.id})">
                        下载
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载报告列表失败:', error);
    }
}

// 下载报告
async function downloadReport(reportId) {
    try {
        await reportsAPI.download(reportId);
        showMessage('下载成功！', 'success');
    } catch (error) {
        showMessage('下载失败: ' + error.message, 'error');
    }
}

