#!/usr/bin/env python3
"""
MCP 服务器测试脚本
用于验证服务器的基本功能
"""

import sys

# 测试是否可以导入必要的模块
def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    try:
        from mcp.server.fastmcp import FastMCP
        from pydantic import Field
        from datetime import datetime
        print("✅ 所有必需模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("\n请运行: pip install -r requirements.txt")
        return False


def test_server_creation():
    """测试服务器创建"""
    print("\n🔍 测试服务器创建...")
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test-server")
        print("✅ MCP 服务器创建成功")
        return True
    except Exception as e:
        print(f"❌ 服务器创建失败: {e}")
        return False


def test_server_file():
    """测试服务器文件语法"""
    print("\n🔍 测试服务器文件语法...")
    try:
        import py_compile
        py_compile.compile('/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo/server.py', doraise=True)
        print("✅ server.py 语法检查通过")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ server.py 语法错误: {e}")
        return False


def test_server_import():
    """测试服务器模块导入"""
    print("\n🔍 测试服务器模块导入...")
    try:
        # 动态导入服务器模块
        sys.path.insert(0, '/Users/linofficemac/Documents/AI/LIN_AI_resource/code/mcp-demo')
        import server

        # 检查服务器对象存在
        if hasattr(server, 'mcp'):
            print("✅ 服务器模块导入成功，MCP 服务器已创建")
            print("   工具包括: calculator, text_analyzer, get_current_time, reverse_text")
            return True
        else:
            print("❌ 服务器模块缺少 mcp 对象")
            return False
    except Exception as e:
        print(f"❌ 服务器模块导入失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("MCP Demo 服务器测试")
    print("=" * 60)

    tests = [
        test_imports(),
        test_server_creation(),
        test_server_file(),
        test_server_import()
    ]

    print("\n" + "=" * 60)
    passed = sum(tests)
    total = len(tests)

    if passed == total:
        print(f"✅ 所有测试通过 ({passed}/{total})")
        print("\n🎉 服务器已准备就绪！")
        print("\n下一步:")
        print("1. 将配置添加到 Claude Code")
        print("2. 重启 Claude Code")
        print("3. 使用工具！")
    else:
        print(f"⚠️  部分测试失败 ({passed}/{total})")
        print("\n请修复上述错误后重试")

    print("=" * 60)


if __name__ == "__main__":
    main()
