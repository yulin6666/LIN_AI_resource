#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
八字Bazi API 客户端测试脚本
测试 FastAPI + LangServe 八字计算API的不同用例和模式
"""

import requests
import json
import time
from typing import Dict, Any

# API 基础URL
BASE_URL = "http://localhost:8000"

# ===== API 客户端函数定义 =====

def health_check() -> Dict[str, Any]:
    """健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"健康检查失败: {e}")
exit(1)

def get_api_info() -> Dict[str, Any]:
    """获取API信息"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/")
        response.raise_for_status()
    return response.json()
    except requests.exceptions.RequestException as e:
      raise Exception(f"API 调用失败: {e}")

def calculate_bazi_direct(year: int, month: int, day: int, hour: int = 0, minute: int = 0,
 gender: int = 1, options: str = "all") -> Dict[str, Any]:
    """直接调用八字计算API"""
    url = f"{BASE_URL}/api/v1/calculate_bazi"

    payload = {
        "year": year,
   "month": month,
 "day": day,
        "hour": hour,
        "minute": minute,
        "gender": gender,
   "options": options
    }

    try:
        response = requests.post(url, json=payload)
    response.raise_for_status()
       return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"直接计算调用失败: {e}")

def calculate_bazi_nlp(query: str) -> Dict[str, Any]:
    """使用NLP自然语言模式调用八字计算API"""
    url = f"{BASE_URL}/api/v1/nlp/bazi"

    payload = {
        "query": query
    }

    try:
   response = requests.post(url, json=payload)
     response.raise_for_status()
 return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"NLP调用失败: {e}")

# ===== 格式化输出函数 =====

def print_bazi_basic(result: Dict[str, Any]):
    """格式化打印基础信息"""
    data = result.get("data", {})
    print(f"【基本信息】")
    print(f"  出生日期: {data['user_info']['阳历']}")
    print(f"  农历日期: {data['user_info']['农历']}")
    print(f"  生肖: {data['user_info']['生肖']}")
  print(f"  性别: {data['user_info']['性别']}")
    print(f"\n【四柱八字】")
    print(f"  年柱: {data['bazi']['年柱']}")
    print(f"  月柱: {data['bazi']['月柱']}")
    print(f"  日柱: {data['bazi']['日柱']}")
    print(f"  时柱: {data['bazi']['时柱']}")
    print(f"  日主: {data['day_master']}")

def print_bazi_wuxing(result: Dict[str, Any]):
 """格式化打印五行分析"""
    data = result.get("data", {})
    print(f"【五行分析】")
    wuxing = data['wuxing']
    print(f"  五行详情:")
    for key, value in wuxing['detail'].items():
        print(f"    {key}: {value}")
 print(f"  五行统计: {wuxing['counts']}")

    print(f"\n【纳音】")
    nayin = data['nayin']
    print(f"  年柱: {nayin['年柱纳音']}")
    print(f"  月柱: {nayin['月柱纳音']}")
    print(f"  日柱: {nayin['日柱纳音']}")
    print(f"  时柱: {nayin['时柱纳音']}")

def print_bazi_fortune(result: Dict[str, Any]):
    """格式化打印运势分析"""
    data = result.get("data", {})
    print(f"【起运信息】")
    print(f"  {data['qi_yun']['起运描述']}")

    print(f"\n【大运 (前8步)】")
    for dy in data['da_yun'][:8]:
        print(f"  第{dy['序号']}步: {dy['大运干支']} | {dy['起运年龄']}-{dy['结束年龄']}岁 | {dy['起运年份']}年")

    print(f"\n【流年 (前10年)】")
    for ln in data['liu_nian'][:10]:
        print(f"  {ln['年份']}年 | {ln['年龄']}岁 | {ln['干支']}")

def print_separator():
    print("\n" + "="*80 + "\n")

# ===== 测试用例 =====

def test_case_1_basic_calculation():
    """测试基础八字计算"""
    print("测试用例 1: 基础八字计算")
    print("请求参数: 1990年5月15日14:30, 性别男")

    try:
    result = calculate_bazi_direct(1990, 5, 15, 14, 30, 1, "basic")
    if result.get("status") == "success":
            print_bazi_basic(result)
        else:
            print(f"计算失败: {result.get('error')}")
    except Exception as e:
   print(f"执行失败: {e}")

    print_separator()

def test_case_2_wuxing_analysis():
    """测试五行分析"""
    print("测试用例 2: 五行分析")
    print("请求参数: 1987年3月28日11:00, 性别男")

    try:
   result = calculate_bazi_direct(1987, 3, 28, 11, 0, 1, "wuxing")
     if result.get("status") == "success":
      print_bazi_wuxing(result)
        else:
       print(f"计算失败: {result.get('error')}")
    except Exception as e:
        print(f"执行失败: {e}")

    print_separator()

def test_case_3_fortune_analysis():
    """测试运势分析"""
    print("测试用例 3: 运势分析")
    print("请求参数: 1988年12月25日08:20, 性别女")

 try:
        result = calculate_bazi_direct(1988, 12, 25, 8, 20, 0, "fortune")
    if result.get("status") == "success":
        print_bazi_fortune(result)
        else:
            print(f"计算失败: {result.get('error')}")
    except Exception as e:
     print(f"执行失败: {e}")

    print_separator()

def test_case_4_nlp_chinese():
    """测试中文NLP解析"""
    print("测试用例 4: 中文NLP解析")
    print("请求内容: '我出生于1987年3月28日11点，性别男'")

    try:
        result = calculate_bazi_nlp("我出生于1987年3月28日11点，性别男")
        if result.get("status") == "success":
       print(f"解析结果: {result['parsed_input']}")
      print_bazi_basic(result)  # 简基本信息
        else:
         print(f"计算失败: {result.get('error')}")
    except Exception as e:
  print(f"执行失败: {e}")

    print_separator()

def test_case_5_nlp_english():
    """测试英文NLP解析"""
    print("测试用例 5: 英文NLP解析")
    print("请求内容: 'Female, born on 1991-07-15 at 22:30'")

    try:
    result = calculate_bazi_nlp("Female, born on 1991-07-15 at 22:30")
        if result.get("status") == "success":
          print(f"解析结果: {result['parsed_input']}")
print_bazi_basic(result)  # 简基本信息
        else:
            print(f"计算失败: {result.get('error')}")
    except Exception as e:
        print(f"执行失败: {e}")

    print_separator()

def test_case_6_error_handling():
    """测试错误处理"""
   print("测试用例 6: 错误处理")

    # 测试1: 缺少参
test_cases = [
        ("缺少年份", {"month": 5, "day": 15, "gender": 1}),
   	("缺少月份", {"year": 1990, "day": 15, "gender": 1}),
      ("缺少日期", {"year": 1990, "month": 5, "gender": 1}),
     ("缺少性别", {"year": 1990, "month": 5, "day": 15}),
 ("无效年份", {"year": 1899, "month": 5, "day": 15, "gender": 1}),
    ]

    for desc, params in test_cases:
        print(f"\n测试: {desc}")
        try:
   request_body = json.dumps(params)
response = requests.post(
     f"{BASE_URL}/api/v1/calculate_bazi",
                headers={"Content-Type": "application/json"},
                data=request_body
   )
            result = response.json()
if "error" in result:
       print(f"捕获到预期错误: {result['error']}")
  else:
      print(f"意外成功: {result}")
    except Exception as e:
    print(f"通信错误: {e}")

def test_case_7_performance_test():
    """性能测试"""
    print("测试用例 7: 性能测试")
    print("连续调用10次NLP接口测试响应时间")

    queries = [
    "1990年5月15日14:30出生，男",
        "我是1987年3月28日11点出生的",
   "出生于1988年12月25日早上8:20，女性",
     "1991年7月15日22点30分，男",
    "1990年5月15日14:30出生，男",
    "我是1987年3月28日11点出生的",
    "出生于1988年12月25日早上8:20，女性",
        "1991年7月15日22点30分，男",
    "1990年5月15日14:30出生，男",
   "我是1987年3月28日11点出生的",
    ]

response_times = []
    for i, query in enumerate(queries):
start_time = time.time()
        try:
   result = calculate_bazi_nlp(query)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
      response_times.append(response_time)

   if result.get("status") == "success":
    print(f"查询{i+1}: {response_time:.2f}ms - 成功")
           else:
                print(f"查询{i+1}: {response_time:.2f}ms - 失败: {result.get('error')}")
    except Exception as e:
     print(f"查询{i+1}: 失败 - {e}")
            response_times.append(None)

    # 汇总统计
valid_times = [t for t in response_times if t is not None]
    if valid_times:
        print(f"\n响应时间统计:")
        print(f"  平均响应时间: {sum(valid_times)/len(valid_times):.2f}ms")
 print(f"  最快响应: {min(valid_times):.2f}ms")
    print(f"  最慢响应: {max(valid_times):.2f}ms")

    print_separator()

# ===== 主测试函数 =====

def main():
    """主测试函数"""
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                         ║")
    print("║        八字Bazi API 客户端测试脚本                                       ║")
    print("║                                                                         ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print(f"API地址: {BASE_URL}")

    # 1. 健康检查
    print("\n1. 执行健康检查...")
    health_result = health_check()
    print(f"服务状态: {health_result}")

    if health_result.get('status') != 'healthy':
      print("服务未，请查API服务是否启动")
      return

   # 2. 获取API信息
    print("\n2. 获取API信息...")
    api_info = get_api_info()
    print(f"API信息: {api_info['name']} v{api_info['version']}")
    print_separator()

    # 3. 执行各种试
print("开始执行测试用例...")

    # 基础测试
    test_case_1_basic_calculation()
    test_case_2_wuxing_analysis()
    test_case_3_fortune_analysis()

    # NLP测试
    test_case_4_nlp_chinese()
    test_case_5_nlp_english()

    # 错误处理测试
    test_case_6_error_handling()

    # 性能测试
    test_case_7_performance_test()

    # 全部测试完成
    print("所有测试执行完成！")
    print("\n使用建议:")
    print("1. 生产环境请设置合适的CORS策略")
    print("2. 根据需要选择合适的分析选项('basic', 'wuxing', 'fortune', 'all')")
    print("3. 对于中文用户，推荐使用NLP接口更方便")
  print("4. 合理控制请求频率，避免对API服务造成压力")

if __name__ == "__main__":
    main()

"""
# 常用命令：

# 1. 启动服务
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/langgraph
python bazi_api_server.py

# 2. 运行测试
python test_bazi_api.py

# 3. cURL 快速测试
# 健康问题检查
curl -s "http://localhost:8000/health"

# 直接调用八字计算
curl -s -X POST "http://localhost:8000/api/v1/calculate_bazi" \
  -H "Content-Type: application/json" \
  -d '{"year":1990,"month":5,"day":15,"hour":14,"minute":30,"gender":1,"options":"basic"}'

# NLP模式调用
curl -s -X POST "http://localhost:8000/api/v1/nlp/bazi" \
  -H "Content-Type: application/json" \
  -d '{"query":"我是1990年5月15日14点30分出生的，男"}'

# 4. Python交互式使用
python -i test_bazi_api.py
# In [1]: result = calculate_bazi_direct(1990, 5, 15, 14, 30, 1, "all")
# In [2]: print(json.dumps(result, indent=2, ensure_ascii=False))
"""