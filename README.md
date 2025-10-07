# 消费分析平台

基于 Flask + 原生前端的消费数据分析平台，提供数据导入/导出、多维度分析、智能预测、异常检测和报告生成等功能。

## 功能特性

### 核心功能
- ✅ 用户认证（注册、登录、JWT）
- ✅ 数据导入（Excel/CSV）
- ✅ 数据导出（Excel/CSV）
- ✅ 多维度数据分析
- ✅ 智能预测
- ✅ 异常检测
- ✅ 报告生成（PDF/Word）
- ✅ 个性化设置

### 数据分析功能
- 消费趋势分析（日/月/年）
- 类别占比分析（饼图）
- 金额分布分析（柱状图）
- 地点热力图
- 时间分布（雷达图）
- 消费行为关联（树状图/桑基图）
- 消费水平分布（散点图）
- 消费排行榜

## 技术栈

### 后端
- Python 3.8+
- Flask 3.0
- SQLAlchemy（ORM）
- Flask-JWT-Extended（认证）
- Pandas（数据处理）
- Scikit-learn（机器学习）
- TensorFlow（深度学习）
- Matplotlib（图表生成）
- ReportLab/WeasyPrint（PDF生成）

### 前端
- 原生 HTML/CSS/JavaScript
- Chart.js（图表库）
- ECharts（高级图表）

### 数据库
- SQLite（开发/单机）

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd wordmd
```

### 2. 创建虚拟环境
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

### 5. 初始化数据库
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 6. 运行应用
```bash
python run.py
```

应用将在 http://localhost:5000 启动

### 7. 访问前端
在浏览器中打开 `frontend/index.html` 或配置静态文件服务。

## API 文档

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新 token
- `GET /api/auth/me` - 获取当前用户信息

### 数据管理接口
- `POST /api/data/import` - 导入数据
- `GET /api/data/export` - 导出数据
- `GET /api/data/imports` - 获取导入记录

### 分析接口
- `GET /api/analytics/trend` - 消费趋势
- `GET /api/analytics/category-share` - 类别占比
- `GET /api/analytics/amount-hist` - 金额分布
- `GET /api/analytics/heatmap` - 地点热力图
- `GET /api/analytics/time-radar` - 时间分布
- `GET /api/analytics/behavior-tree` - 行为关联
- `GET /api/analytics/level-scatter` - 水平分布
- `GET /api/analytics/rank` - 排行榜

### 预测接口
- `GET /api/forecast/predict` - 预测消费
- `GET /api/forecast/anomaly` - 异常检测
- `GET /api/forecast/history` - 预测历史

### 报告接口
- `POST /api/reports/generate` - 生成报告
- `GET /api/reports/` - 获取报告列表
- `GET /api/reports/<id>/download` - 下载报告

### 设置接口
- `GET /api/settings/` - 获取设置
- `PUT /api/settings/` - 更新设置

## 数据导入格式

### CSV/Excel 格式要求
必需列：
- `time` - 消费时间（格式：YYYY-MM-DD HH:MM:SS）
- `amount` - 消费金额（数字）

可选列：
- `category` - 消费类别
- `location` - 消费地点
- `note` - 备注

示例：
```csv
time,amount,category,location,note
2024-01-01 10:30:00,50.5,餐饮,北京市朝阳区,午餐
2024-01-02 15:20:00,200,购物,上海市浦东新区,衣服
```

## 项目结构
```
.
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用工厂
│   ├── models/            # 数据模型
│   └── routes/            # 路由蓝图
├── frontend/              # 前端文件
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript 文件
│   └── index.html        # 主页面
├── config.py             # 配置文件
├── run.py                # 启动文件
├── requirements.txt      # Python 依赖
└── README.md            # 项目文档
```

## 开发计划

详见 [DEV_PLAN_FLASK_CONSUMER_ANALYTICS.md](DEV_PLAN_FLASK_CONSUMER_ANALYTICS.md)

## 测试

```bash
# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 部署

### 使用 Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 使用 Docker
```bash
# 构建镜像
docker build -t consumer-analytics .

# 运行容器
docker run -p 5000:5000 consumer-analytics
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
