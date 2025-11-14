import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# 加载.env文件
load_dotenv()

# Configure LangSmith - 从环境变量读取
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "default")

# 从环境变量读取API密钥
openai_api_key = os.getenv("OPENAI_API_KEY", "")
base_url = os.getenv("OPENAI_BASE_URL", "https://api.poixe.com/v1")
tavily_api_key = os.getenv("TAVILY_API_KEY", "")

model = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)
search_tool = TavilySearch(
    max_results=5,
    topic="general",
    tavily_api_key=tavily_api_key
)
tools = [search_tool]
search_agent = create_react_agent(model=model, tools=tools)
response = search_agent.invoke({"messages": [{"role": "user", "content": "请帮我搜索最近OpenAI CEO在访谈中的核心观点。"}]})
# print(response["messages"][-1].content)
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