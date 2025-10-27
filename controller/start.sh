#!/bin/bash
# HomeTom 控制器启动脚本

echo "========================================"
echo "🚀 启动 HomeTom 控制器"
echo "========================================"

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $python_version"

# 检查依赖是否安装
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠ 依赖未安装，正在安装..."
    pip install -r requirements.txt
fi

# 创建必要的目录
mkdir -p data logs

# 启动服务
echo "📡 启动服务..."
python3 main.py

