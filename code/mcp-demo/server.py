#!/usr/bin/env python3
"""
简单的 MCP Demo 服务器
提供计算器、文本处理和时间查询工具
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from datetime import datetime
import json

# 创建 MCP 服务器实例
mcp = FastMCP("simple-demo")

@mcp.tool()
async def calculator(
    operation: str = Field(description="运算类型: add, subtract, multiply, divide"),
    a: float = Field(description="第一个数字"),
    b: float = Field(description="第二个数字")
) -> str:
    """
    简单计算器工具

    支持基本的四则运算。

    示例:
    - operation="add", a=5, b=3 -> 返回 8
    - operation="multiply", a=4, b=6 -> 返回 24
    """
    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return json.dumps({
                    "error": "除数不能为零",
                    "suggestion": "请提供一个非零的除数"
                }, ensure_ascii=False, indent=2)
            result = a / b
        else:
            return json.dumps({
                "error": f"不支持的运算类型: {operation}",
                "valid_operations": ["add", "subtract", "multiply", "divide"]
            }, ensure_ascii=False, indent=2)

        return json.dumps({
            "operation": operation,
            "inputs": {"a": a, "b": b},
            "result": result
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def text_analyzer(
    text: str = Field(description="要分析的文本")
) -> str:
    """
    文本分析工具

    分析文本并返回统计信息：
    - 字符数
    - 单词数
    - 行数
    - 是否包含数字
    """
    try:
        lines = text.split('\n')
        words = text.split()
        has_digits = any(char.isdigit() for char in text)

        return json.dumps({
            "original_text": text[:100] + "..." if len(text) > 100 else text,
            "statistics": {
                "character_count": len(text),
                "word_count": len(words),
                "line_count": len(lines),
                "has_digits": has_digits
            }
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_current_time(
    timezone: str = Field(default="local", description="时区: local, utc")
) -> str:
    """
    获取当前时间

    返回当前的日期和时间信息。

    参数:
    - timezone: "local" 返回本地时间, "utc" 返回 UTC 时间
    """
    try:
        if timezone == "utc":
            now = datetime.utcnow()
            tz_name = "UTC"
        else:
            now = datetime.now()
            tz_name = "本地时间"

        return json.dumps({
            "timezone": tz_name,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),
            "timestamp": now.timestamp()
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def reverse_text(
    text: str = Field(description="要反转的文本"),
    mode: str = Field(default="characters", description="反转模式: characters(字符) 或 words(单词)")
) -> str:
    """
    文本反转工具

    可以反转文本的字符顺序或单词顺序。

    示例:
    - text="Hello World", mode="characters" -> "dlroW olleH"
    - text="Hello World", mode="words" -> "World Hello"
    """
    try:
        if mode == "characters":
            result = text[::-1]
        elif mode == "words":
            result = " ".join(text.split()[::-1])
        else:
            return json.dumps({
                "error": f"不支持的模式: {mode}",
                "valid_modes": ["characters", "words"]
            }, ensure_ascii=False, indent=2)

        return json.dumps({
            "original": text,
            "reversed": result,
            "mode": mode
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 运行服务器
    mcp.run()
