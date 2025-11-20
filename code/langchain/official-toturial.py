"""LangGraph Weather Agent Example - Using Stable API"""

from dataclasses import dataclass
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
# 使用新的导入方式（避免弃用警告）
try:
    from langchain.agents import create_react_agent
except ImportError:
    from langgraph.prebuilt import create_react_agent

# ===== System Prompt =====
SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""

# ===== Context Schema =====
@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

# 全局存储用户上下文（简化版）
USER_CONTEXT = {}

# ===== Tools =====
@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def get_user_location(user_id: str = "1") -> str:
    """Retrieve user location based on user ID.

    Args:
        user_id: The user ID (default is "1")
    """
    # 从全局上下文获取
    ctx = USER_CONTEXT.get("current_user")
    if ctx:
        user_id = ctx.user_id
    return "Florida" if user_id == "1" else "SF"

# ===== Response Format (结构化输出) =====
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    # A punny response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    weather_conditions: str | None = None

# ===== Initialize Model =====
from langchain_openai import ChatOpenAI

# 设置 API 配置（使用自定义代理）
openai_api_key = "sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url = "https://api.poixe.com/v1"  # 自定义 OpenAI 兼容端点

model = ChatOpenAI(
    model="gpt-4",
    temperature=0.5,
    timeout=10,
    max_tokens=1000,
    openai_api_key=openai_api_key,
    base_url=base_url
)

# ===== 自定义 Agent 工作流（模拟 ToolStrategy）=====
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, ToolMessage
import operator

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    structured_response: dict | None

# 创建带结构化输出的模型
structured_llm = model.with_structured_output(ResponseFormat)

def should_continue(state: AgentState):
    """判断是否继续调用工具"""
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "format_response"

def call_model(state: AgentState):
    """调用模型"""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

def call_tools(state: AgentState):
    """执行工具调用"""
    from langgraph.prebuilt import ToolNode
    tool_node = ToolNode([get_user_location, get_weather_for_location])
    result = tool_node.invoke(state)
    return result

def format_response(state: AgentState):
    """格式化为结构化输出（模拟 ToolStrategy）"""
    # 获取最后的 AI 回复
    last_ai_message = None
    for msg in reversed(state['messages']):
        if isinstance(msg, AIMessage) and not hasattr(msg, 'tool_calls'):
            last_ai_message = msg
            break
        elif isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and not msg.tool_calls:
            last_ai_message = msg
            break
        

    if not last_ai_message or not last_ai_message.content:
        # 如果没有最终回复，让模型生成一个
        messages = state['messages']
        response = model.invoke(messages)
        last_ai_message = response

    # 使用结构化模型格式化
    structured = structured_llm.invoke([
        SystemMessage(content="""Extract the weather forecast into structured format:
        - punny_response: The punny weather forecast message
        - weather_conditions: The actual weather condition (e.g., 'sunny', 'rainy') or None"""),
        HumanMessage(content=last_ai_message.content)
    ])

    return {
        "structured_response": structured,
        "messages": []  # 不添加新消息
    }

# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)
workflow.add_node("format_response", format_response)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "format_response": "format_response"
    }
)
workflow.add_edge("tools", "agent")
workflow.add_edge("format_response", END)

# 编译
checkpointer = MemorySaver()
agent = workflow.compile(checkpointer=checkpointer)

# ===== Run Example 1 =====
print("=" * 60)
print("Example 1: What is the weather outside?")
print("=" * 60)

# 设置用户上下文
USER_CONTEXT["current_user"] = Context(user_id="1")

# thread_id 是对话的唯一标识符
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {
        "messages": [HumanMessage(content="what is the weather outside?")],
        "structured_response": None
    },
    config=config
)

# 分析工具调用过程
print("\n📋 工具调用记录:")
print("-" * 60)
for msg in response['messages']:
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        # AI 决定调用工具
        for tool_call in msg.tool_calls:
            print(f"🔧 调用工具: {tool_call['name']}")
            print(f"   参数: {tool_call['args']}")
    elif msg.__class__.__name__ == 'ToolMessage':
        # 工具返回结果
        print(f"✅ 工具返回: {msg.content}")
        print()

# 打印最后的回复
final_message = response['messages'][-1]
print("-" * 60)
print(f"\n💬 Agent 最终回复: {final_message.content}\n")

# 提取结构化输出
print("\n📊 结构化输出 (ResponseFormat):")
print("-" * 60)
structured = extract_structured_response(response)
print(f"  punny_response: \"{structured['punny_response']}\"")
print(f"  weather_conditions: {structured['weather_conditions']}")
print()

# ===== Run Example 2 =====
print("=" * 60)
print("Example 2: Continue conversation")
print("=" * 60)

# 继续同一个对话（使用相同的 thread_id）
response = agent.invoke(
    {
        "messages": [HumanMessage(content="thank you!")]
    },
    config=config
)

# 分析工具调用
print("\n📋 工具调用记录:")
print("-" * 60)
tool_called = False
for msg in response['messages']:
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        for tool_call in msg.tool_calls:
            print(f"🔧 调用工具: {tool_call['name']}")
            print(f"   参数: {tool_call['args']}")
            tool_called = True
    elif msg.__class__.__name__ == 'ToolMessage':
        print(f"✅ 工具返回: {msg.content}")
        print()

if not tool_called:
    print("ℹ️  本次对话未调用任何工具（直接回复）")

final_message = response['messages'][-1]
print("-" * 60)
print(f"\n💬 Agent 最终回复: {final_message.content}\n")

# 提取结构化输出
print("\n📊 结构化输出 (ResponseFormat):")
print("-" * 60)
structured = extract_structured_response(response)
print(f"  punny_response: \"{structured['punny_response']}\"")
print(f"  weather_conditions: {structured['weather_conditions']}")
print()

# ===== Run Example 3 =====
print("=" * 60)
print("Example 3: Different user")
print("=" * 60)

# 改变用户上下文
USER_CONTEXT["current_user"] = Context(user_id="2")

# 新的对话线程
config2 = {"configurable": {"thread_id": "2"}}

response = agent.invoke(
    {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content="what is the weather where I am?")
        ]
    },
    config=config2
)

# 分析工具调用
print("\n📋 工具调用记录:")
print("-" * 60)
for msg in response['messages']:
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        for tool_call in msg.tool_calls:
            print(f"🔧 调用工具: {tool_call['name']}")
            print(f"   参数: {tool_call['args']}")
    elif msg.__class__.__name__ == 'ToolMessage':
        print(f"✅ 工具返回: {msg.content}")
        print()

final_message = response['messages'][-1]
print("-" * 60)
print(f"\n💬 Agent 最终回复: {final_message.content}\n")

# 提取结构化输出
print("\n📊 结构化输出 (ResponseFormat):")
print("-" * 60)
structured = extract_structured_response(response)
print(f"  punny_response: \"{structured['punny_response']}\"")
print(f"  weather_conditions: {structured['weather_conditions']}")
print()

print("=" * 60)
print("All examples completed!")
print("=" * 60)
