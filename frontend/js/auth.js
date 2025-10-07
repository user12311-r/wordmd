// 认证相关功能

// 检查登录状态
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (token && user.id) {
        showApp();
        updateUserInfo(user);
        return true;
    } else {
        showLoginPage();
        return false;
    }
}

// 显示应用
function showApp() {
    document.getElementById('login-page').classList.remove('active');
    document.getElementById('register-page').classList.remove('active');
    document.getElementById('dashboard-page').classList.add('active');
    document.querySelector('.navbar').style.display = 'flex';
}

// 显示登录页
function showLoginPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('login-page').classList.add('active');
    document.querySelector('.navbar').style.display = 'none';
}

// 显示注册页
function showRegisterPage() {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('register-page').classList.add('active');
    document.querySelector('.navbar').style.display = 'none';
}

// 更新用户信息显示
function updateUserInfo(user) {
    const userName = user.email || user.phone || '用户';
    document.getElementById('user-name').textContent = userName;
}

// 登录表单处理
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const identifier = document.getElementById('login-identifier').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const data = await authAPI.login(identifier, password);
        showMessage('登录成功！', 'success');
        showApp();
        updateUserInfo(data.user);
        loadDashboard();
    } catch (error) {
        showMessage('登录失败: ' + error.message, 'error');
    }
});

// 注册表单处理
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('register-email').value;
    const phone = document.getElementById('register-phone').value;
    const password = document.getElementById('register-password').value;
    
    if (!email && !phone) {
        showMessage('请至少填写邮箱或手机号', 'error');
        return;
    }
    
    try {
        await authAPI.register(email, phone, password);
        showMessage('注册成功！请登录', 'success');
        showLoginPage();
    } catch (error) {
        showMessage('注册失败: ' + error.message, 'error');
    }
});

// 切换到注册页
document.getElementById('show-register').addEventListener('click', (e) => {
    e.preventDefault();
    showRegisterPage();
});

// 切换到登录页
document.getElementById('show-login').addEventListener('click', (e) => {
    e.preventDefault();
    showLoginPage();
});

// 退出登录
document.getElementById('logout-btn').addEventListener('click', (e) => {
    e.preventDefault();
    authAPI.logout();
    showLoginPage();
    showMessage('已退出登录', 'success');
});

// 显示消息
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = type === 'error' ? 'error-message' : 'success-message';
    messageDiv.textContent = message;
    
    const container = document.querySelector('.page.active .card') || document.querySelector('.page.active');
    if (container) {
        container.insertBefore(messageDiv, container.firstChild);
        setTimeout(() => messageDiv.remove(), 3000);
    }
}

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});

