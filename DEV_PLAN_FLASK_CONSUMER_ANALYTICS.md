## 消费分析平台（Flask + 原生前端）开发计划（简版）

### 我的一步一步执行清单（命令式，直接照做）
1. 先创建 Git 仓库并提交本文件，建立 main/dev 分支。
2. 用 venv 创建 Python 环境，安装 Flask、SQLAlchemy、JWT 等基础依赖。
3. 定义 SQLite 数据库文件路径，初始化 Alembic（或直接建表）。
4. 搭建 Flask 应用工厂与配置加载，注册日志与错误处理。
5. 创建 ORM 模型（users、expenses、categories、forecasts、reports、settings、imports、login_logs）。
6. 生成并执行首版迁移，让所有表在 SQLite 中落地。
7. 实现密码加密（bcrypt/argon2）与用户注册、登录、找回密码接口。
8. 接入 JWT 认证与角色控制（用户/管理员），给受保护路由加装饰器。
9. 开发数据导入接口（Excel/CSV）：上传、校验、解析入库、导入记录与错误明细。
10. 开发数据导出接口（Excel/CSV）：支持条件筛选导出消费记录与预测结果。
11. 编写消费趋势 API（日/月/年折线图所需的时间序列汇总）。
12. 编写消费类别占比 API（饼图数据）。
13. 编写消费金额分布 API（柱状或直方数据）。
14. 编写消费地点热力 API（聚合经纬度或地名栅格）。
15. 编写消费时间分布 API（雷达图数据：按小时/星期/月份分布）。
16. 编写消费行为关联 API（树状/桑基图需要的层级或关系数据）。
17. 编写消费水平分布 API（散点图数据：金额/频次/类别维度）。
18. 编写消费排行榜 API（条形图 TOP N）。
19. 设计并训练预测模型（TensorFlow；定义特征、切分集、保存模型）。
20. 实现预测接口：加载模型，对指定周期返回预测趋势线，并写入 forecasts 表。
21. 实现异常检测接口（3σ/IsolationForest），输出异常点与阈值供仪表盘使用。
22. 初始化前端 index.html 与 main.js，接入 Chart.js 与 ECharts。
23. 开发登录/注册/找回页面，打通与后端的 JWT 登录态。
24. 开发仪表盘页面，联通趋势、异常、排行榜数据展示。
25. 开发数据导入/导出页面，展示校验结果与下载链接。
26. 开发分析页：折线、饼图、柱状、热力、雷达、树状、散点、预测线图逐个联调。
27. 实现个性化设置：主题色、图表样式、刷新频率（前端本地存储 + 后端 settings）。
28. 实现报告生成：服务端渲染图（Matplotlib），导出 PDF（ReportLab/WeasyPrint）与 Word（python-docx）。
29. 完成登录日志、导入日志审计与列表查询。
30. 做分页与索引优化，排查 N+1，开启输入校验与速率限制。
31. 补充 pytest 单元/集成测试，准备小样本数据用于回归。
32. 配置打包与部署（Gunicorn + Nginx 或 Docker Compose），分离 .env。
33. 完成备份策略（定期备份 SQLite 文件）与基础监控告警。

### 技术栈确认
- 后端：Python + Flask + SQLAlchemy + Marshmallow + JWT（PyJWT/Flask-JWT-Extended）
- 前端：原生 HTML/CSS/JavaScript + Chart.js + ECharts
- 数据库：SQLite（开发/单机），迁移：Alembic（可选）
- 机器学习：TensorFlow（预测），Scikit-learn（随机森林、线回归、K-means）
- 大数据：Spark/Hadoop/Hive（离线批处理，可选接入）
- 可视化/报告：Matplotlib（服务器端渲染图）、ReportLab/WeasyPrint（PDF）、python-docx（Word）

### 开发顺序（从零到一）
1. 创建 Git 仓库与分支策略（main/dev/feature/*），提交本计划。
2. 定义需求边界与KPI（用户、数据规模、报表刷新频率、预测周期）。
3. 细化数据库表结构与字段约束（见"数据库设计"），规划必要索引。
4. 初始化后端工程骨架（Flask 应用工厂、蓝图、配置管理、日志）。
5. 接入 SQLAlchemy 与 SQLite，定义 ORM 模型与会话管理。
6. 初始化 Alembic（可选），生成并应用首版迁移脚本建表。
7. 实现用户注册/登录/找回密码（手机号/邮箱），加密存储密码（bcrypt/argon2）。
8. 实现 JWT 认证与权限拦截（角色：用户/管理员），编写基础中间件。
9. 实现数据导入 API（Excel/CSV 上传）：
   - 文件校验（扩展名、大小、表头、数据类型）；
   - 后台解析入库（pandas/openpyxl/csv），写入导入记录表；
   - 幂等与错误行反馈（返回行号与错误原因）。
10. 实现数据导出 API（Excel/CSV 下载）：按筛选条件导出消费记录/预测/报表。
11. 构建消费数据分析 API：
   - 日/月/年消费趋势（折线图）；
   - 类别占比（饼图）；金额分布（柱状图）；
   - 地点热力图（坐标聚合/网格热力数据）；
   - 时间分布（雷达图）；
   - 行为关联（树状/桑基需要的层级数据）；
   - 水平分布（散点图数据结构）；
   - 排行榜（条形图 TOP N）。
12. 训练与推理：智能预测功能（TensorFlow + 特征工程）：
   - 构建时序/回归模型，定义训练数据切分与特征；
   - 保存模型（SavedModel）与版本；
   - 推理 API：输入时间范围/维度，返回预测趋势线数据；
   - 将结果写入预测结果表，支持缓存与失效策略。
13. 异常检测与仪表盘：
   - 基于统计或模型（如 IsolationForest/3σ 规则）；
   - 返回告警级别、异常点列表与阈值。
14. 前端基础框架与页面：
   - 登录/注册/找回密码页面；
   - 首页仪表盘（趋势、异常、排行榜概览卡片）；
   - 数据导入/导出页面（上传、校验结果、下载链接）；
   - 分析页（折线/饼图/柱状/热力/雷达/树状/散点/预测线图）。
15. 前端图表接入：
   - Chart.js：折线、柱状、饼图、雷达、散点、条形；
   - ECharts：热力图、桑基/树状、复杂交互。
16. 个性化设置：主题色切换、图表样式偏好、数据刷新频率（本地存储 + 服务器侧设置表）。
17. 报告生成：
   - 服务端渲染 Matplotlib 图（PNG/SVG）；
   - 生成 PDF（ReportLab/WeasyPrint）与 Word（python-docx）；
   - 打包所有图表与摘要指标，提供下载。
18. 大数据接入（可并行在分支推进）：
   - 设计 Hive 表结构与ETL（Sqoop/自研导入）；
   - Spark 作业（批计算：汇总指标、离线训练特征）；
   - 与 Flask 通过离线结果表/对象存储对接展示。
19. 性能与安全：
   - 增加分页、必要索引、N+1 查询排查；
   - 速率限制（Flask-Limiter）、CORS、输入验证（Marshmallow）；
   - 审计登录日志、导入日志；保护导出链接有效期。
20. 测试与质量：
   - pytest 单元/集成测试；
   - 前端 E2E（可选 Playwright）验证关键流程；
   - 数据一致性校验与回归测试集。
21. 部署与运维：
   - 配置分离（.env）、日志切割、静态资源缓存；
   - 单机部署（Gunicorn + Nginx）或容器化（Docker Compose）；
   - 备份策略（SQLite 文件定期备份）与监控告警（可选）。

### 数据库设计（字段简述）
- 用户信息表 users：id，phone，email，password_hash，role，status，created_at
- 消费记录表 expenses：id，user_id，time，amount，category_id，location(lat,lon/文本)，note，created_at
- 消费类别表 categories：id，name，parent_id，code
- 预测结果表 forecasts：id，user_id，period（日/月/年），date，predicted_amount，model_version，created_at
- 分析报告表 reports：id，user_id，title，file_path，format(pdf/docx)，created_at
- 系统设置表 settings：id，user_id，theme，chart_prefs(json)，refresh_interval_sec，updated_at
- 数据导入记录表 imports：id，user_id，filename，rows_total，rows_success，rows_failed，status，error_report_path，created_at
- 登录日志表 login_logs：id，user_id，login_time，ip，ua

### API 粒度（示例，后端先做这些）
- 认证：POST /auth/register，POST /auth/login，POST /auth/forgot，POST /auth/reset
- 导入/导出：POST /data/import，GET /data/export
- 分析：GET /analytics/trend，GET /analytics/category-share，GET /analytics/amount-hist
- 地点热力：GET /analytics/heatmap
- 时间分布：GET /analytics/time-radar
- 行为关联：GET /analytics/behavior-tree
- 水平分布：GET /analytics/level-scatter
- 排行榜：GET /analytics/rank
- 预测：POST /forecast/train（可选），GET /forecast/predict
- 报告：POST /reports/generate，GET /reports/{id}/download
- 设置：GET/PUT /settings

### 开发里程碑（建议）
- M1（后端基础）：认证、SQLite、导入/导出、趋势/类别/排行 API
- M2（分析与前端）：剩余可视化 API 与页面联调、主题与设置
- M3（智能与报告）：预测/异常检测、报告生成下载
- M4（大数据与优化）：Spark/Hive 接入、性能与安全加固、上线

### 本地最小命令（Windows PowerShell 示例）
```powershell
# 后端环境
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install flask sqlalchemy flask-jwt-extended marshmallow pandas openpyxl scikit-learn tensorflow matplotlib reportlab python-docx

# 数据库迁移（可选）
pip install alembic
alembic init alembic

# 前端（原生）初始化占位
mkdir frontend
cd frontend
echo "<!doctype html><html><head><meta charset=\"utf-8\"><title>消费分析</title></head><body><div id=\"app\"></div><script src=\"/main.js\"></script></body></html>" > index.html
echo "// init charts code" > main.js
```

