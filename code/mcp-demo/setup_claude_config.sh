#!/bin/bash

# Claude Code MCP 自动配置脚本
# 此脚本会自动创建并配置 Claude Code 的 MCP 服务器设置

echo "========================================"
echo "Claude Code MCP 自动配置脚本"
echo "========================================"
echo ""

# 定义配置文件路径
CONFIG_DIR="$HOME/Library/Application Support/Claude"
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📂 项目目录: $SCRIPT_DIR"
echo "📂 配置目录: $CONFIG_DIR"
echo "📄 配置文件: $CONFIG_FILE"
echo ""

# 步骤 1: 创建配置目录
echo "步骤 1: 创建配置目录..."
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    if [ $? -eq 0 ]; then
        echo "✅ 配置目录创建成功"
    else
        echo "❌ 配置目录创建失败"
        exit 1
    fi
else
    echo "✅ 配置目录已存在"
fi
echo ""

# 步骤 2: 备份现有配置（如果存在）
if [ -f "$CONFIG_FILE" ]; then
    echo "步骤 2: 备份现有配置..."
    BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo "✅ 已备份到: $BACKUP_FILE"
    echo ""
fi

# 步骤 3: 创建或更新配置
echo "步骤 3: 创建 MCP 配置..."

# 生成配置内容
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "simple-demo": {
      "command": "$SCRIPT_DIR/venv/bin/python",
      "args": [
        "$SCRIPT_DIR/server.py"
      ],
      "description": "简单的 MCP Demo 服务器 - 提供计算器、文本处理和时间查询工具"
    }
  }
}
EOF

if [ $? -eq 0 ]; then
    echo "✅ 配置文件创建成功"
else
    echo "❌ 配置文件创建失败"
    exit 1
fi
echo ""

# 步骤 4: 验证配置
echo "步骤 4: 验证配置..."
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ 配置文件存在"
    echo ""
    echo "📋 配置内容:"
    echo "----------------------------------------"
    cat "$CONFIG_FILE"
    echo "----------------------------------------"
else
    echo "❌ 配置文件不存在"
    exit 1
fi
echo ""

# 步骤 5: 检查虚拟环境
echo "步骤 5: 检查虚拟环境..."
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "✅ 虚拟环境存在"
else
    echo "⚠️  虚拟环境不存在"
    echo "   请运行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi
echo ""

# 步骤 6: 检查 server.py
echo "步骤 6: 检查服务器文件..."
if [ -f "$SCRIPT_DIR/server.py" ]; then
    echo "✅ server.py 存在"
else
    echo "❌ server.py 不存在"
    exit 1
fi
echo ""

# 完成
echo "========================================"
echo "✅ 配置完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. 完全退出 Claude Code（Cmd + Q）"
echo "2. 重新启动 Claude Code"
echo "3. 测试工具："
echo "   - '帮我计算 25 * 8'"
echo "   - '现在几点了？'"
echo "   - '分析这段文本：Hello World!'"
echo ""
echo "如果遇到问题，查看备份文件："
if [ -f "$BACKUP_FILE" ]; then
    echo "   $BACKUP_FILE"
fi
echo ""
