// 数据管理功能

// 加载数据管理页面
async function loadDataPage() {
    await loadImportRecords();
}

// 导入表单处理
document.getElementById('import-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('import-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('请选择文件', 'error');
        return;
    }
    
    const resultDiv = document.getElementById('import-result');
    resultDiv.innerHTML = '<p class="loading">正在上传...</p>';
    
    try {
        const data = await dataAPI.importData(file);
        
        let html = `
            <div class="success-message">
                <p>导入完成！</p>
                <p>总行数: ${data.import_record.rows_total}</p>
                <p>成功: ${data.import_record.rows_success}</p>
                <p>失败: ${data.import_record.rows_failed}</p>
            </div>
        `;
        
        if (data.errors && data.errors.length > 0) {
            html += '<div class="error-message"><h4>错误详情（前10条）:</h4><ul>';
            data.errors.forEach(err => {
                html += `<li>第 ${err.row} 行: ${err.error}</li>`;
            });
            html += '</ul></div>';
        }
        
        resultDiv.innerHTML = html;
        
        // 刷新导入记录
        await loadImportRecords();
        
        // 清空文件选择
        fileInput.value = '';
        
    } catch (error) {
        resultDiv.innerHTML = `<div class="error-message">导入失败: ${error.message}</div>`;
    }
});

// 导出 CSV
document.getElementById('export-csv-btn').addEventListener('click', async () => {
    try {
        await dataAPI.exportData('csv');
        showMessage('导出成功！', 'success');
    } catch (error) {
        showMessage('导出失败: ' + error.message, 'error');
    }
});

// 导出 Excel
document.getElementById('export-xlsx-btn').addEventListener('click', async () => {
    try {
        await dataAPI.exportData('xlsx');
        showMessage('导出成功！', 'success');
    } catch (error) {
        showMessage('导出失败: ' + error.message, 'error');
    }
});

// 加载导入记录
async function loadImportRecords() {
    try {
        const data = await dataAPI.getImportRecords();
        
        const container = document.getElementById('import-records');
        if (!container) return;
        
        if (data.records.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999;">暂无导入记录</p>';
            return;
        }
        
        container.innerHTML = data.records.map(record => `
            <div class="record-item">
                <div>
                    <strong>${record.filename}</strong>
                    <div style="font-size: 0.9rem; color: #666;">
                        ${new Date(record.created_at).toLocaleString()}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div>总数: ${record.rows_total}</div>
                    <div style="color: #27ae60;">成功: ${record.rows_success}</div>
                    <div style="color: #e74c3c;">失败: ${record.rows_failed}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载导入记录失败:', error);
    }
}

