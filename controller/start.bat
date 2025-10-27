@echo off
REM HomeTom 控制器启动脚本 (Windows)

echo ========================================
echo 🚀 启动 HomeTom 控制器
echo ========================================

REM 检查 Python
python --version
if errorlevel 1 (
    echo ❌ Python 未安装
    exit /b 1
)

REM 检查依赖
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ⚠ 依赖未安装，正在安装...
    pip install -r requirements.txt
)

REM 创建必要的目录
if not exist data mkdir data
if not exist logs mkdir logs

REM 启动服务
echo 📡 启动服务...
python main.py

