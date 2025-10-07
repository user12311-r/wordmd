@echo off
chcp 65001 >nul
echo ================================
echo 消费分析平台启动脚本
echo ================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo ✓ Python 已安装
echo.

REM 检查虚拟环境
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
    echo ✓ 虚拟环境创建成功
)

REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 安装依赖
echo 检查依赖...
pip install -q -r requirements.txt
echo ✓ 依赖安装完成
echo.

REM 检查 .env 文件
if not exist ".env" (
    echo 创建 .env 配置文件...
    copy .env.example .env
    echo ✓ 请编辑 .env 文件配置必要参数
)

REM 初始化数据库
if not exist "consumer_analytics.db" (
    echo 初始化数据库...
    python init_db.py
    echo.
)

REM 启动应用
echo ================================
echo 启动 Flask 应用...
echo ================================
echo.
echo 访问地址: http://localhost:5000
echo 前端页面: frontend/index.html
echo.
echo 测试账号:
echo   邮箱: test@example.com
echo   密码: test123456
echo.
echo 按 Ctrl+C 停止服务器
echo.

python run.py

pause

