# Claude Code MCP 配置指南

## 🚀 自动配置（推荐）

使用提供的自动配置脚本，一键完成所有设置：

```bash
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo

# 给脚本添加执行权限
chmod +x setup_claude_config.sh

# 运行配置脚本
./setup_claude_config.sh
```

脚本会自动：
- ✅ 创建 Claude 配置目录
- ✅ 备份现有配置（如果有）
- ✅ 生成 MCP 服务器配置
- ✅ 验证所有必需文件
- ✅ 显示下一步操作

## 🔧 手动配置

如果你想手动配置，按以下步骤操作：

### 步骤 1: 创建配置目录

```bash
mkdir -p ~/Library/Application\ Support/Claude
```

### 步骤 2: 创建配置文件

```bash
# 使用编辑器打开（如果文件不存在会自动创建）
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 步骤 3: 添加以下内容

```json
{
  "mcpServers": {
    "simple-demo": {
      "command": "/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/venv/bin/python",
      "args": [
        "/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/server.py"
      ],
      "description": "简单的 MCP Demo 服务器"
    }
  }
}
```

### 步骤 4: 保存文件

- nano: 按 `Ctrl + O` 保存，`Ctrl + X` 退出
- vim: 按 `ESC`，输入 `:wq`，按回车

## ✅ 配置后操作

### 1. 重启 Claude Code

**完全退出 Claude Code：**
- 方法 A: 按 `Cmd + Q`
- 方法 B: 右键点击 Dock 中的 Claude Code 图标 → 退出
- 方法 C: 菜单栏 Claude Code → Quit

**重新启动 Claude Code**

### 2. 验证配置

在 Claude Code 中测试以下命令：

```
帮我计算 123 + 456
```

如果返回计算结果，说明配置成功！✅

### 3. 测试所有工具

试试这些命令：

**计算器：**
```
计算 25 乘以 8
帮我算一下 100 除以 4
```

**文本分析：**
```
分析这段文本：Python is awesome! It has 12345 lines of code.
```

**当前时间：**
```
现在几点了？
告诉我 UTC 时间
```

**文本反转：**
```
把 "Hello World" 的字符反转
把 "Hello World" 的单词顺序反转
```

## 🔍 故障排除

### 问题 1: 配置文件不存在

**症状：**
```bash
cat: /Users/linofficemac/Library/Application Support/Claude/claude_desktop_config.json: No such file or directory
```

**解决方案：**
运行自动配置脚本（见上方"自动配置"部分）

### 问题 2: 工具未加载

**可能原因：**
1. ❌ Claude Code 未重启
2. ❌ 配置文件路径错误
3. ❌ Python 虚拟环境不存在
4. ❌ JSON 格式错误

**解决方案：**

**检查虚拟环境：**
```bash
ls -la /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/venv/bin/python
```

如果不存在，重新创建：
```bash
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**验证配置文件：**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**检查 JSON 格式：**
```bash
# 安装 jq（如果没有）
brew install jq

# 验证 JSON
jq . ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 问题 3: 权限错误

**症状：**
```
Permission denied
```

**解决方案：**
```bash
# 给 server.py 添加执行权限
chmod +x /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/server.py

# 给 Python 解释器添加执行权限（通常不需要）
chmod +x /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/venv/bin/python
```

### 问题 4: 找不到配置目录

**解决方案：**

在 Finder 中显示隐藏文件：
- 按 `Cmd + Shift + .`（点）

或直接在终端中访问：
```bash
cd ~/Library/Application\ Support/Claude
ls -la
```

## 📋 配置文件位置速查

| 系统 | 配置文件路径 |
|------|-------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

## 🎯 快速命令参考

```bash
# 查看配置
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 编辑配置
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 备份配置
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup

# 运行测试
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo
source venv/bin/activate
python test_server.py
```

## 💡 提示

1. **配置文件是 JSON 格式**
   - 确保所有引号、逗号、括号都正确匹配
   - 最后一项不要有多余的逗号

2. **使用绝对路径**
   - 不要使用 `~` 或相对路径
   - 使用完整的绝对路径

3. **虚拟环境很重要**
   - 必须使用虚拟环境中的 Python
   - 不要使用系统 Python

4. **重启是必要的**
   - 每次修改配置后都要完全退出并重启 Claude Code
   - 不是刷新，是完全退出（Cmd + Q）

---

**需要帮助？** 查看 README.md 或 QUICK_START.md 获取更多信息。
