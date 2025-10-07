// API 配置和请求封装
const API_BASE_URL = 'http://localhost:5000/api';

// 存储 token
let accessToken = localStorage.getItem('access_token');

// API 请求封装
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // 添加认证 token
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.message || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API 请求错误:', error);
        throw error;
    }
}

// 认证 API
const authAPI = {
    async login(identifier, password) {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email: identifier, password })
        });
        
        if (data.access_token) {
            accessToken = data.access_token;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('user', JSON.stringify(data.user));
        }
        
        return data;
    },
    
    async register(email, phone, password) {
        return await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, phone, password })
        });
    },
    
    async getCurrentUser() {
        return await apiRequest('/auth/me');
    },
    
    logout() {
        accessToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    }
};

// 数据 API
const dataAPI = {
    async importData(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/data/import`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
            body: formData
        });
        
        return await response.json();
    },
    
    async exportData(format = 'csv') {
        const response = await fetch(`${API_BASE_URL}/data/export?format=${format}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `expenses_${Date.now()}.${format}`;
        a.click();
    },
    
    async getImportRecords(page = 1) {
        return await apiRequest(`/data/imports?page=${page}`);
    }
};

// 分析 API
const analyticsAPI = {
    async getTrend(period = 'month', startDate = null, endDate = null) {
        let url = `/analytics/trend?period=${period}`;
        if (startDate) url += `&start_date=${startDate}`;
        if (endDate) url += `&end_date=${endDate}`;
        return await apiRequest(url);
    },
    
    async getCategoryShare(startDate = null, endDate = null) {
        let url = '/analytics/category-share';
        const params = [];
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        if (params.length) url += '?' + params.join('&');
        return await apiRequest(url);
    },
    
    async getAmountHistogram(bins = 10) {
        return await apiRequest(`/analytics/amount-hist?bins=${bins}`);
    },
    
    async getHeatmap() {
        return await apiRequest('/analytics/heatmap');
    },
    
    async getTimeRadar(dimension = 'hour') {
        return await apiRequest(`/analytics/time-radar?dimension=${dimension}`);
    },
    
    async getBehaviorTree() {
        return await apiRequest('/analytics/behavior-tree');
    },
    
    async getLevelScatter() {
        return await apiRequest('/analytics/level-scatter');
    },
    
    async getRank(rankBy = 'category', topN = 10) {
        return await apiRequest(`/analytics/rank?rank_by=${rankBy}&top_n=${topN}`);
    }
};

// 预测 API
const forecastAPI = {
    async predict(period = 'month', days = 30) {
        return await apiRequest(`/forecast/predict?period=${period}&days=${days}`);
    },
    
    async detectAnomaly(method = 'isolation_forest') {
        return await apiRequest(`/forecast/anomaly?method=${method}`);
    },
    
    async getHistory(page = 1) {
        return await apiRequest(`/forecast/history?page=${page}`);
    }
};

// 报告 API
const reportsAPI = {
    async generate(title, format = 'pdf', startDate = null, endDate = null) {
        return await apiRequest('/reports/generate', {
            method: 'POST',
            body: JSON.stringify({ title, format, start_date: startDate, end_date: endDate })
        });
    },
    
    async getReports(page = 1) {
        return await apiRequest(`/reports/?page=${page}`);
    },
    
    async download(reportId) {
        const response = await fetch(`${API_BASE_URL}/reports/${reportId}/download`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${reportId}.pdf`;
        a.click();
    }
};

// 设置 API
const settingsAPI = {
    async getSettings() {
        return await apiRequest('/settings/');
    },
    
    async updateSettings(settings) {
        return await apiRequest('/settings/', {
            method: 'PUT',
            body: JSON.stringify(settings)
        });
    }
};

