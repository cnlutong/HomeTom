#!/bin/bash

# Home Assistant 测试 API 服务器启动脚本

echo "🏠 启动 Home Assistant 测试 API 服务器..."
echo ""
echo "有效的测试 Token:"
echo "  • test_token"
echo "  • demo_token"
echo "  • your_long_lived_access_token"
echo ""
echo "端点列表:"
echo "  • http://localhost:8123/api/     - API 状态"
echo "  • http://localhost:8123/docs     - Swagger 文档"
echo "  • http://localhost:8123/test/reset - 重置测试数据"
echo ""

cd "$(dirname "$0")/.."

python3 -m uvicorn test_API_server.main:app --host 0.0.0.0 --port 8123 --reload
