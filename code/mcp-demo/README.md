# MCP Demo 服务器

一个简单但功能完整的 MCP (Model Context Protocol) 服务器示例。

## 📦 包含的工具

这个 demo 服务器提供了 4 个实用工具：

1. **calculator** - 基本计算器（加减乘除）
2. **text_analyzer** - 文本分析（统计字符、单词、行数等）
3. **get_current_time** - 获取当前时间（本地/UTC）
4. **reverse_text** - 文本反转（字符/单词）

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo
pip install -r requirements.txt
```

### 2️⃣ 测试服务器

运行测试脚本确保一切正常：

```bash
python test_server.py
```

你应该看到所有测试通过的消息 ✅

### 3️⃣ 配置 Claude Code

#### 方法一：使用配置文件（推荐）

将 `mcp_config.json` 的内容添加到你的 Claude Code MCP 设置中：

1. 打开 Claude Code 设置
2. 找到 MCP Servers 配置
3. 添加以下配置：

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

#### 方法二：通过 Claude Code UI 添加

1. 在 Claude Code 中，打开 MCP 服务器设置
2. 点击"添加服务器"
3. 填写：
   - 名称: `simple-demo`
   - 命令: `/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/venv/bin/python`
   - 参数: `/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/server.py`

### 4️⃣ 重启 Claude Code

配置完成后，重启 Claude Code 使配置生效。

### 5️⃣ 测试使用

重启后，你可以在 Claude Code 中测试这些工具：

**测试计算器：**
```
帮我计算 123 + 456
```

**测试文本分析：**
```
分析这段文本：Hello World! This is a test.
```

**测试时间查询：**
```
现在几点了？
```

**测试文本反转：**
```
把 "Hello World" 反转一下
```

## 📁 项目结构

```
mcp-demo/
├── server.py           # MCP 服务器主文件
├── requirements.txt    # Python 依赖
├── mcp_config.json    # Claude Code 配置文件
├── test_server.py     # 测试脚本
└── README.md          # 本文件
```

## 🛠️ 工具详细说明

### 1. calculator

执行基本的数学运算。

**参数：**
- `operation`: 运算类型（add, subtract, multiply, divide）
- `a`: 第一个数字
- `b`: 第二个数字

**示例：**
```python
calculator(operation="add", a=5, b=3)  # 返回 8
calculator(operation="divide", a=10, b=2)  # 返回 5
```

### 2. text_analyzer

分析文本并返回统计信息。

**参数：**
- `text`: 要分析的文本

**返回：**
- 字符数
- 单词数
- 行数
- 是否包含数字

### 3. get_current_time

获取当前日期和时间。

**参数：**
- `timezone`: "local" 或 "utc"（默认：local）

**返回：**
- 完整日期时间
- 日期
- 时间
- 星期
- 时间戳

### 4. reverse_text

反转文本的字符或单词顺序。

**参数：**
- `text`: 要反转的文本
- `mode`: "characters" 或 "words"（默认：characters）

**示例：**
```python
reverse_text(text="Hello World", mode="characters")  # "dlroW olleH"
reverse_text(text="Hello World", mode="words")       # "World Hello"
```

## 🔧 故障排除

### 问题：导入错误

```
ImportError: No module named 'mcp'
```

**解决方案：**
```bash
pip install -r requirements.txt
```

### 问题：服务器未在 Claude Code 中显示

**解决方案：**
1. 检查配置文件路径是否正确
2. 确保 Python 路径正确
3. 重启 Claude Code
4. 查看 Claude Code 的日志输出

### 问题：权限错误

```
Permission denied
```

**解决方案：**
```bash
chmod +x /Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/server.py
```

## 📚 学习资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)

## 🎯 下一步

学会了基础后，你可以：

1. **添加更多工具** - 实现你自己的功能
2. **集成外部 API** - 连接真实的服务（天气、新闻等）
3. **添加数据持久化** - 使用数据库存储信息
4. **创建复杂工作流** - 组合多个工具完成复杂任务

## 💡 提示

- 所有工具都返回 JSON 格式的数据，方便 LLM 解析
- 错误消息包含了如何修复的建议
- 工具描述很重要 - LLM 依赖它们来理解如何使用工具

---

**Happy Coding! 🎉**
