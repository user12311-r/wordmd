// 设置功能

// 加载设置页面
async function loadSettingsPage() {
    try {
        const data = await settingsAPI.getSettings();
        
        // 填充表单
        document.getElementById('theme-select').value = data.settings.theme || 'light';
        document.getElementById('refresh-interval').value = data.settings.refresh_interval_sec || 300;
        
        // 应用主题
        applyTheme(data.settings.theme);
        
    } catch (error) {
        console.error('加载设置失败:', error);
    }
}

// 设置表单处理
document.getElementById('settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const theme = document.getElementById('theme-select').value;
    const refreshInterval = parseInt(document.getElementById('refresh-interval').value);
    
    try {
        await settingsAPI.updateSettings({
            theme: theme,
            refresh_interval_sec: refreshInterval
        });
        
        showMessage('设置保存成功！', 'success');
        
        // 应用主题
        applyTheme(theme);
        
    } catch (error) {
        showMessage('保存设置失败: ' + error.message, 'error');
    }
});

// 应用主题
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.style.backgroundColor = '#1a1a1a';
        document.body.style.color = '#f5f5f5';
    } else {
        document.body.style.backgroundColor = '#f5f5f5';
        document.body.style.color = '#333';
    }
}

