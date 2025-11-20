from langchain.tools import tool
from langchain_openai import ChatOpenAI
openai_api_key="sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url="https://api.poixe.com/v1"

model = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)

# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


# Augment the LLM with tools
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

from langchain.messages import SystemMessage


def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

from langchain.messages import ToolMessage

def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

from typing import Literal
from langgraph.graph import StateGraph, START, END

def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()

# Show the agent - 保存为文件
print("生成 Agent 工作流图表...")
png_data = agent.get_graph(xray=True).draw_mermaid_png()
with open("agent_graph.png", "wb") as f:
    f.write(png_data)
print("✅ 图表已保存到: agent_graph.png")
print("   使用命令查看: open agent_graph.png\n")

# Invoke - 使用 stream 模式查看每一步的 state
from langchain.messages import HumanMessage

print("=" * 70)
print("开始执行 - 逐步显示 state")
print("=" * 70)

messages = [HumanMessage(content="Add 3 and 4.")]
step_count = 0

for event in agent.stream({"messages": messages}, stream_mode="values"):
    step_count += 1
    print(f"\n{'='*70}")
    print(f"步骤 {step_count} - State:")
    print(f"{'='*70}")

    # 打印完整的 state
    print(f"State 类型: {type(event)}")
    print(f"State 键: {event.keys()}")
    print(f"\n消息数量: {len(event['messages'])}")
    print("\n消息列表:")

    for i, m in enumerate(event["messages"], 1):
        print(f"\n  消息 {i}:")
        m.pretty_print()

    print(f"\n{'='*70}")

print(f"\n✅ 总共执行了 {step_count} 个步骤")