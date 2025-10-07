#!/bin/bash

# 消费分析平台启动脚本

echo "================================"
echo "消费分析平台启动脚本"
echo "================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "检查依赖..."
pip install -q -r requirements.txt
echo "✓ 依赖安装完成"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "创建 .env 配置文件..."
    cp .env.example .env
    echo "✓ 请编辑 .env 文件配置必要参数"
fi

# 初始化数据库
if [ ! -f "consumer_analytics.db" ]; then
    echo "初始化数据库..."
    python init_db.py
    echo ""
fi

# 启动应用
echo "================================"
echo "启动 Flask 应用..."
echo "================================"
echo ""
echo "访问地址: http://localhost:5000"
echo "前端页面: frontend/index.html"
echo ""
echo "测试账号:"
echo "  邮箱: test@example.com"
echo "  密码: test123456"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python run.py

