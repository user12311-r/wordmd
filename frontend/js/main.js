// 主应用逻辑

// 页面导航
const pages = {
    'dashboard': 'dashboard-page',
    'analytics': 'analytics-page',
    'data': 'data-page',
    'reports': 'reports-page',
    'settings': 'settings-page'
};

// 导航链接点击处理
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        
        // 跳过退出按钮
        if (href === '#' || link.id === 'logout-btn') {
            return;
        }
        
        e.preventDefault();
        
        const pageName = href.replace('#', '');
        navigateToPage(pageName);
    });
});

// 导航到指定页面
function navigateToPage(pageName) {
    // 更新导航链接状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${pageName}`) {
            link.classList.add('active');
        }
    });
    
    // 切换页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    const pageId = pages[pageName];
    if (pageId) {
        document.getElementById(pageId).classList.add('active');
        
        // 加载页面数据
        loadPageData(pageName);
    }
}

// 加载页面数据
function loadPageData(pageName) {
    switch (pageName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'data':
            loadDataPage();
            break;
        case 'reports':
            loadReportsPage();
            break;
        case 'settings':
            loadSettingsPage();
            break;
    }
}

// 初始化应用
function initApp() {
    // 检查登录状态
    if (checkAuth()) {
        // 加载仪表盘
        loadDashboard();
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

