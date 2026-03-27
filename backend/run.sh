#!/bin/bash
# ClawLink Backend 启动脚本

set -e

cd "$(dirname "$0")"

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt -q

# 复制 .env（如果不存在）
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — please update with your keys."
fi

# 启动
echo "Starting ClawLink backend on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
