#!/bin/bash

# 快速测试脚本
echo "================================"
echo "MCP Demo 快速测试"
echo "================================"

# 检查当前目录
echo ""
echo "📂 当前目录: $(pwd)"

# 检查文件是否存在
echo ""
echo "📋 检查文件..."
if [ -f "server.py" ]; then
    echo "✅ server.py 存在"
else
    echo "❌ server.py 不存在"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 存在"
else
    echo "❌ requirements.txt 不存在"
fi

if [ -d "venv" ]; then
    echo "✅ venv 虚拟环境存在"
else
    echo "❌ venv 虚拟环境不存在"
    echo "   需要运行: python3 -m venv venv"
fi

# 激活虚拟环境并运行测试
echo ""
echo "🧪 运行 Python 测试..."
if [ -d "venv" ]; then
    source venv/bin/activate
    python test_server.py
    deactivate
else
    echo "⚠️  虚拟环境不存在，跳过 Python 测试"
fi

echo ""
echo "================================"
echo "测试完成"
echo "================================"
