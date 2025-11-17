# MCP Demo - 快速开始

## 1. 已完成的准备工作

- ✅ 虚拟环境已创建
- ✅ 依赖已安装
- ✅ 服务器代码已准备

## 2. 如何在 Claude Code 中使用

### 方法 A: 自动配置（推荐）

在 Claude Code 的 MCP 设置中添加以下配置：

```json
{
  "mcpServers": {
    "simple-demo": {
      "command": "/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/venv/bin/python",
      "args": [
        "/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/server.py"
      ]
    }
  }
}
```

**注意**: 使用虚拟环境中的 Python 解释器路径 (`venv/bin/python`)

### 方法 B: 手动测试

你也可以在命令行手动测试服务器（仅用于调试）：

```bash
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo
source venv/bin/activate
python server.py
```

## 3. 配置 Claude Code

### 找到 MCP 配置文件

Claude Code 的 MCP 配置通常位于:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- 或在 Claude Code 设置中直接编辑

### 编辑配置文件

打开配置文件，添加 `simple-demo` 服务器配置：

```json
{
  "mcpServers": {
    "simple-demo": {
      "command": "/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/venv/bin/python",
      "args": [
        "/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/server.py"
      ]
    }
  }
}
```

### 重启 Claude Code

配置完成后，完全退出并重启 Claude Code。

## 4. 测试工具

重启后，你可以测试这些功能：

### 计算器
```
帮我计算 25 * 8
```

### 文本分析
```
分析这段文本：Python is awesome! It has 12345 characters.
```

### 当前时间
```
现在几点了？
```

### 文本反转
```
把 "Hello World" 的单词顺序反转
```

## 5. 可用工具列表

| 工具名 | 功能 | 示例 |
|-------|------|------|
| `calculator` | 四则运算 | add, subtract, multiply, divide |
| `text_analyzer` | 文本统计 | 字符数、单词数、行数统计 |
| `get_current_time` | 获取时间 | 本地时间或 UTC 时间 |
| `reverse_text` | 文本反转 | 字符反转或单词反转 |

## 6. 故障排除

### 问题：服务器未显示在 Claude Code 中

**检查清单:**
1. 配置文件路径是否正确？
2. Python 路径是否使用虚拟环境的路径？
3. 是否重启了 Claude Code？
4. 检查 Claude Code 日志是否有错误

### 问题：工具调用失败

**解决方案:**
```bash
# 测试服务器是否正常
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo
source venv/bin/activate
python -c "import server; print('OK')"
```

### 问题：虚拟环境丢失

**重新创建:**
```bash
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 7. 下一步学习

完成基础 demo 后，你可以：

1. **修改现有工具** - 在 `server.py` 中编辑工具逻辑
2. **添加新工具** - 参考现有工具添加新的 `@mcp.tool()` 函数
3. **集成 API** - 调用外部服务（天气、新闻等）
4. **添加数据持久化** - 使用 SQLite 或文件存储数据

## 8. 有用的命令

```bash
# 激活虚拟环境
source /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/venv/bin/activate

# 安装新的依赖
pip install 包名

# 更新 requirements.txt
pip freeze > requirements.txt

# 查看已安装的包
pip list

# 退出虚拟环境
deactivate
```

---

**需要帮助？** 查看完整的 README.md 文件获取更多详细信息。
