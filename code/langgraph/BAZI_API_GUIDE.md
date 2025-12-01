# 八字Bazi API 使用教程

## 快速开始

### 1. 启动服务

```bash
# 进入项目目录
cd /Users/linofficemac/Documents/AI/LIN_AI_resource/code/langgraph

# 启动API服务
python bazi_api_server.py
```

服务会启动在 `http://localhost:8000`

### 2. 访问API文档

启动后，访问以下URL：
- **交互式API文档**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## API 端点说明

### 方式一：直接调用 (Direct API)

**端点**: `POST /api/v1/calculate_bazi`

**用途**: 直接传递结构化数据，快速获得八字分析结果

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/calculate_bazi" \
  -H "Content-Type: application/json" \
  -d '{
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "gender": 1,
    "options": "all"
  }'
```

**参数说明**:
- `year` (int): 出生年份 (1900-2030)
- `month` (int): 出生月份 (1-12)
- `day` (int): 出生日 (1-31)
- `hour` (int, optional): 出生小时 (0-23，默认0)
- `minute` (int, optional): 出生分钟 (0-59，默认0)
- `gender` (int): 性别 (1=男, 0=女)
- `options` (string, optional): 分析选项
  - `"all"` - 返回全部分析结果（默认）
  - `"basic"` - 仅返回基础信息、四柱、日主
  - `"wuxing"` - 仅返回五行分析
  - `"fortune"` - 仅返回运势分析

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "user_info": {
      "阳历": "1990-05-15 14:30",
      "农历": "庚午年 四月 十八",
      "生肖": "马",
      "性别": "男"
    },
    "bazi": {
      "年柱": "庚午",
      "月柱": "己巳",
      "日柱": "癸巳",
      "时柱": "丙午"
    },
    "day_master": "癸",
    ...
  },
  "timestamp": "2024-11-27T10:30:00.000000"
}
```

---

### 方式二：自然语言处理 (NLP API)

**端点**: `POST /api/v1/nlp/bazi`

**用途**: 输入自然语言描述，AI自动解析并计算八字

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/nlp/bazi" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "我出生于1987年3月28日11点，性别男"
  }'
```

支持多种输入格式：
- `"1990年5月15日14点30分，男"`
- `"1990-05-15 14:30, 男性"`
- `"Female, born on 1988-12-25 at 08:20"`
- `"女性，1988年12月25日早上8点20分"`

**响应示例**:
```json
{
  "status": "success",
  "parsed_input": {
    "year": 1987,
    "month": 3,
    "day": 28,
    "hour": 11,
    "minute": 0,
    "gender": 1,
    "options": "all"
  },
  "bazi_analysis": {
    ...八字分析结果...
  },
  "timestamp": "2024-11-27T10:30:00.000000"
}
```

---

## Python 客户端示例

### 安装依赖

```bash
pip install requests
```

### 使用代码

```python
import requests
import json

# API 基础URL
BASE_URL = "http://localhost:8000"

# ===== 方式一：直接调用 =====
def calculate_bazi_direct(year, month, day, hour=0, minute=0, gender=1, options="all"):
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

    response = requests.post(url, json=payload)
    return response.json()

# ===== 方式二：NLP模式 =====
def calculate_bazi_nlp(query):
    """使用NLP自然语言模式调用八字计算API"""
    url = f"{BASE_URL}/api/v1/nlp/bazi"

    payload = {
        "query": query
    }

    response = requests.post(url, json=payload)
    return response.json()

# ===== 获取API信息 =====
def get_api_info():
    """获取API信息和使用指南"""
    url = f"{BASE_URL}/api/v1/"
    response = requests.get(url)
    return response.json()

# ===== 健康检查 =====
def health_check():
    """检查服务是否正常运行"""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    return response.json()

# ===== 使用示例 =====
if __name__ == "__main__":
    # 检查服务状态
    print("健康检查:")
    print(health_check())
    print("\n" + "="*50 + "\n")

    # 直接调用示例
    print("方式一：直接调用")
    result = calculate_bazi_direct(
        year=1990,
        month=5,
        day=15,
        hour=14,
        minute=30,
        gender=1,
        options="basic"
    )
    print(f"状态: {result.get('status')}")
    print(f"日期: {result['data']['user_info']['阳历']}")
    print(f"生肖: {result['data']['user_info']['生肖']}")
    print(f"四柱: {result['data']['bazi']}")
    print("\n" + "="*50 + "\n")

    # NLP模式示例
    print("方式二：NLP自然语言模式")
    result = calculate_bazi_nlp("我是1987年3月28日11点出生的男性")
    print(f"状态: {result.get('status')}")
    print(f"解析结果: {result['parsed_input']}")
    print(f"四柱: {result['bazi_analysis']['bazi']}")
    print("\n" + "="*50 + "\n")

    # 获取完整分析（五行分析）
    print("五行分析")
    result = calculate_bazi_direct(
        year=1990,
        month=5,
        day=15,
        hour=14,
        minute=30,
        gender=1,
        options="wuxing"
    )
    print(f"五行分析: {result['data']['wuxing']['counts']}")
    print("\n" + "="*50 + "\n")

    # 运势分析
    print("运势分析")
    result = calculate_bazi_direct(
        year=1990,
        month=5,
        day=15,
        hour=14,
        minute=30,
        gender=1,
        options="fortune"
    )
    print(f"起运信息: {result['data']['qi_yun']['起运描述']}")
    print(f"大运（前3步）:")
    for dy in result['data']['da_yun'][:3]:
        print(f"  {dy['大运干支']} | {dy['起运年龄']}-{dy['结束年龄']}岁")
```

---

## JavaScript/Node.js 客户端示例

```javascript
const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:8000';

// 直接调用
async function calculateBaziDirect(year, month, day, hour = 0, minute = 0, gender = 1, options = 'all') {
  const response = await fetch(`${BASE_URL}/api/v1/calculate_bazi`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      year, month, day, hour, minute, gender, options
    })
  });
  return response.json();
}

// NLP模式
async function calculateBaziNLP(query) {
  const response = await fetch(`${BASE_URL}/api/v1/nlp/bazi`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query })
  });
  return response.json();
}

// 使用示例
(async () => {
  // 直接调用
  const result1 = await calculateBaziDirect(1990, 5, 15, 14, 30, 1, 'basic');
  console.log('直接调用结果:', result1.data.user_info);

  // NLP模式
  const result2 = await calculateBaziNLP('1987年3月28日11点出生，男');
  console.log('NLP解析结果:', result2.parsed_input);
})();
```

---

## cURL 快速命令

### 直接调用
```bash
curl -X POST "http://localhost:8000/api/v1/calculate_bazi" \
  -H "Content-Type: application/json" \
  -d '{"year":1990,"month":5,"day":15,"hour":14,"minute":30,"gender":1,"options":"all"}'
```

### NLP模式
```bash
curl -X POST "http://localhost:8000/api/v1/nlp/bazi" \
  -H "Content-Type: application/json" \
  -d '{"query":"我出生于1990年5月15日14点30分，男"}'
```

### 获取API信息
```bash
curl "http://localhost:8000/api/v1/"
```

### 健康检查
```bash
curl "http://localhost:8000/health"
```

---

## 分析选项详解

### "all" - 完整分析
返回所有八字信息，包括：
- 基本信息（阳历、农历、生肖、性别）
- 四柱八字（年月日时柱）
- 日主
- 五行分析（详细和统计）
- 纳音
- 十神
- 起运信息
- 大运
- 流年

### "basic" - 基础信息
返回最常用的信息：
- 基本信息
- 四柱八字
- 日主

### "wuxing" - 五行分析
返回五行相关分析：
- 五行详情（每柱五行）
- 五行统计（缺什么）
- 纳音

### "fortune" - 运势分析
返回运势相关信息：
- 起运年龄
- 大运周期（8步）
- 流年（前10年）

---

## 错误处理

API 会返回错误信息：

```json
{
  "error": "缺少必要参数: year, month, day, gender"
}
```

常见错误：
- `400`: 参数错误或缺少必要参数
- `500`: 服务器错误（通常是计算过程中出错）

---

## 完整响应示例

```json
{
  "status": "success",
  "data": {
    "user_info": {
      "阳历": "1990-05-15 14:30",
      "农历": "庚午年 四月 十八",
      "生肖": "马",
      "性别": "男"
    },
    "bazi": {
      "年柱": "庚午",
      "月柱": "己巳",
      "日柱": "癸巳",
      "时柱": "丙午"
    },
    "day_master": "癸",
    "wuxing": {
      "detail": {
        "年柱五行": "金火",
        "月柱五行": "土火",
        "日柱五行": "水火",
        "时柱五行": "火火"
      },
      "list": ["金火", "土火", "水火", "火火"],
      "counts": {
        "金": 1,
        "木": 0,
        "水": 1,
        "火": 6,
        "土": 1
      }
    },
    "nayin": {
      "年柱纳音": "路旁土",
      "月柱纳音": "大林木",
      "日柱纳音": "长流水",
      "时柱纳音": "天河水"
    },
    "shi_shen": {
      ...十神信息...
    },
    "qi_yun": {
      "起运年数": 10,
      "起运月数": 0,
      "起运天数": 0,
      "起运描述": "出生10年0个月0天后起运"
    },
    "da_yun": [
      {
        "序号": 0,
        "大运干支": "庚申",
        "起运年份": 2000,
        "起运年龄": 10,
        "结束年龄": 20
      },
      ...更多大运...
    ],
    "liu_nian": [
      {
        "序号": 0,
        "年份": 2000,
        "年龄": 10,
        "干支": "庚辰"
      },
      ...更多流年...
    ]
  },
  "timestamp": "2024-11-27T10:30:00.000000"
}
```

