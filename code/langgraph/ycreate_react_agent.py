
import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
class WeatherQuery(BaseModel):
    loc: str = Field(description="城市名称")
class WriteQuery(BaseModel):
    content: str = Field(description="需要写入文档的具体内容")

@tool(args_schema=WeatherQuery)
def get_weather(loc):
    """
        查询即时天气函数
        :param loc: 必要参数，字符串类型，用于表示查询天气的具体城市名称，\
        :return：心知天气 API查询即时天气的结果，具体URL请求地址为："https://api.seniverse.com/v3/weather/now.json"
        返回结果对象类型为解析之后的JSON格式对象，并用字符串形式进行表示，其中包含了全部重要的天气信息
    """
    url = "https://api.seniverse.com/v3/weather/now.json"
    params = {
        "key": "SIEurS4whVCQX83k1",
        "location": loc,
        "language": "zh-Hans",
        "unit": "c",
    }
    response = requests.get(url, params=params)
    temperature = response.json()
    return temperature['results'][0]['now']

@tool(args_schema=WriteQuery)
def write_file(content):
    """
    将指定内容写入本地文件。
    :param content: 必要参数，字符串类型，用于表示需要写入文档的具体内容。
    :return：是否成功写入
    """
    with open('res.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    return "已成功写入本地文件。"

from langchain_openai import ChatOpenAI
openai_api_key="sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url="https://api.poixe.com/v1"

model = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)
tools = [get_weather,write_file]

from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model=model, tools=tools)

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "北京和杭州现在的天气如何?并把查询结果写入文件中?"
            }
        ]
    }, 
    {
        "recursion_limit": 10
    },
)

# Format the output for better readability
def format_response(response):
    print("=" * 60)
    print("对话历史")
    print("=" * 60)

    for i, msg in enumerate(response['messages'], 1):
        msg_type = type(msg).__name__

        if msg_type == 'HumanMessage':
            print(f"\n[用户消息 #{i}]")
            print(f"内容: {msg.content}")

        elif msg_type == 'AIMessage':
            print(f"\n[AI消息 #{i}]")
            if msg.tool_calls:
                print("动作: 调用工具")
                for tool_call in msg.tool_calls:
                    print(f"  - 工具名称: {tool_call['name']}")
                    print(f"  - 参数: {tool_call['args']}")
            else:
                print(f"回复: {msg.content}")

        elif msg_type == 'ToolMessage':
            print(f"\n[工具结果 #{i}]")
            print(f"工具: {msg.name}")
            print(f"结果: {msg.content}")

    print("\n" + "=" * 60)
    print("最终答案")
    print("=" * 60)
    final_message = response['messages'][-1]
    print(final_message.content)
    print("=" * 60)

format_response(response)

# print(f'''
# name: {get_weather.name}
# description: {get_weather.description}
# arguments： {get_weather.args}
# ''')