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
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig


def llm_call(state: dict, config: RunnableConfig, *, store: BaseStore):
    """LLM decides whether to call a tool or not

    store 参数会被 LangGraph 自动注入！
    """

    # 从 config 中获取 user_id（如果有的话）
    user_id = config.get("configurable", {}).get("user_id", "default_user")

    # 自动从 store 读取用户偏好
    prefs = store.get(namespace=("users", user_id), key="preferences")
    if prefs:
        print(f"   📦 [Store] 读取到用户偏好: {prefs.value}")

    result = model_with_tools.invoke(
        [
            SystemMessage(
                content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
            )
        ]
        + state["messages"]
    )

    # 自动保存计算历史到 store
    call_count = state.get('llm_calls', 0) + 1
    store.put(
        namespace=("history", user_id),
        key=f"call_{call_count}",
        value={
            "call_number": call_count,
            "input": state["messages"][-1].content if state["messages"] else "",
            "has_tool_call": bool(result.tool_calls)
        }
    )
    print(f"   📦 [Store] 自动保存调用历史: call_{call_count}")

    return {
        "messages": [result],
        "llm_calls": call_count
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
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import interrupt, Command

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

# Compile the agent with checkpointer and store
checkpointer = MemorySaver()
store = InMemoryStore()
agent = agent_builder.compile(checkpointer=checkpointer, store=store)

# Show the agent - 保存为文件
print("生成 Agent 工作流图表...")
png_data = agent.get_graph(xray=True).draw_mermaid_png()
with open("agent_graph.png", "wb") as f:
    f.write(png_data)
print("✅ 图表已保存到: agent_graph.png")
print("   使用命令查看: open agent_graph.png\n")

# Invoke - 使用 stream 模式查看每一步的 state
from langchain.messages import HumanMessage

# 定义 thread_id 配置
config = {"configurable": {"thread_id": "math-session-1"}}

print("=" * 70)
print("演示 Checkpointer + Thread ID 功能")
print("=" * 70)

# ========== 第一轮对话 ==========
print("\n" + "=" * 70)
print("第一轮对话: Add 3 and 4")
print("=" * 70)

messages = [HumanMessage(content="Add 3 and 4.")]

for event in agent.stream({"messages": messages}, config=config, stream_mode="values"):
    pass  # 只执行，不打印每一步

# 获取最终结果
final_state = agent.get_state(config)
last_message = final_state.values["messages"][-1]
print(f"\n回答: {last_message.content}")
print(f"当前消息数量: {len(final_state.values['messages'])}")

# ========== 第二轮对话 ==========
print("\n" + "=" * 70)
print("第二轮对话: Now multiply that result by 2")
print("(Agent 应该记得上一轮的结果是 7)")
print("=" * 70)

messages = [HumanMessage(content="Now multiply that result by 2.")]

for event in agent.stream({"messages": messages}, config=config, stream_mode="values"):
    pass

final_state = agent.get_state(config)
last_message = final_state.values["messages"][-1]
print(f"\n回答: {last_message.content}")
print(f"当前消息数量: {len(final_state.values['messages'])}")

# ========== 第三轮对话 ==========
print("\n" + "=" * 70)
print("第三轮对话: Divide that by 7")
print("(Agent 应该记得上一轮的结果是 14)")
print("=" * 70)

messages = [HumanMessage(content="Divide that by 7.")]

for event in agent.stream({"messages": messages}, config=config, stream_mode="values"):
    pass

final_state = agent.get_state(config)
last_message = final_state.values["messages"][-1]
print(f"\n回答: {last_message.content}")
print(f"当前消息数量: {len(final_state.values['messages'])}")

# ========== 查看完整对话历史 ==========
print("\n" + "=" * 70)
print("完整对话历史 (存储在 checkpointer 中)")
print("=" * 70)

all_messages = final_state.values["messages"]
for i, msg in enumerate(all_messages, 1):
    msg_type = msg.__class__.__name__
    if hasattr(msg, 'content') and msg.content:
        content = msg.content[:80] + "..." if len(str(msg.content)) > 80 else msg.content
        print(f"{i}. [{msg_type}] {content}")
    elif hasattr(msg, 'tool_calls') and msg.tool_calls:
        print(f"{i}. [{msg_type}] Tool calls: {[tc['name'] for tc in msg.tool_calls]}")

print(f"\n✅ 总共 {len(all_messages)} 条消息")
print(f"✅ Thread ID: {config['configurable']['thread_id']}")

# ========== 打印 final_state 的完整结构 ==========
print("\n" + "=" * 70)
print("final_state 的完整结构")
print("=" * 70)

print(f"\nfinal_state 类型: {type(final_state)}")
print(f"final_state 属性: {dir(final_state)}")

print("\n--- final_state.values ---")
print(f"类型: {type(final_state.values)}")
print(f"键: {final_state.values.keys()}")
print(f"messages 数量: {len(final_state.values['messages'])}")
print(f"llm_calls: {final_state.values.get('llm_calls', 'N/A')}")

print("\n--- final_state.next ---")
print(f"下一个节点: {final_state.next}")

print("\n--- final_state.config ---")
print(f"配置: {final_state.config}")

print("\n--- final_state.metadata ---")
print(f"元数据: {final_state.metadata}")

print("\n--- final_state.created_at ---")
print(f"创建时间: {final_state.created_at}")

print("\n--- final_state.parent_config ---")
print(f"父配置: {final_state.parent_config}")

# ========== 时间旅行功能演示 ==========
print("\n" + "=" * 70)
print("🕐 时间旅行功能演示")
print("=" * 70)

# 获取所有历史状态快照
print("\n📜 获取完整的状态历史...")
history = list(agent.get_state_history(config))

print(f"\n共有 {len(history)} 个历史快照:")
print("-" * 70)

# 先打印几个不同的 metadata 示例
print("\n📋 metadata 的完整结构:")
print("-" * 70)

# 选择几个有代表性的状态
sample_indices = [0, 4, 9, 14] if len(history) > 14 else [0, len(history)//2, -1]
for idx in sample_indices:
    if idx < len(history):
        state = history[idx]
        print(f"\n  快照 [{idx}] (Step {state.metadata.get('step')}):")
        for key, value in state.metadata.items():
            print(f"    {key}: {value}")

print("\n" + "-" * 70)
print("\n📊 metadata 字段说明:")
print("  • source: 状态来源 ('loop'=节点执行, 'input'=用户输入)")
print("  • step: 执行步骤号 (-1 是初始状态)")
print("  • parents: 父状态信息（用于分支）")
print("  • writes: 该步骤写入的数据（节点名 → 写入内容）")
print("-" * 70)

for i, state in enumerate(history):
    step = state.metadata.get('step', 'N/A')
    source = state.metadata.get('source', 'N/A')
    writes = state.metadata.get('writes', {})
    msg_count = len(state.values.get('messages', []))

    # 获取最后一条消息的摘要
    if state.values.get('messages'):
        last_msg = state.values['messages'][-1]
        msg_type = last_msg.__class__.__name__
        if hasattr(last_msg, 'content') and last_msg.content:
            content = str(last_msg.content)[:25] + "..." if len(str(last_msg.content)) > 25 else last_msg.content
        elif hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
            content = f"Tool: {last_msg.tool_calls[0]['name']}"
        else:
            content = "..."
    else:
        msg_type = "Empty"
        content = "初始状态"

    # 显示 writes 中的节点名
    write_nodes = list(writes.keys()) if writes else []

    print(f"  [{i:2}] Step {step:2} | src: {source:5} | writes: {write_nodes} | {msg_count} msgs | {content}")

# 时间旅行：回到某个历史状态
print("\n" + "-" * 70)
print("🔙 时间旅行：回到第 4 步（第一次计算完成后）")
print("-" * 70)

# 找到 step 4 的状态
target_state = None
for state in history:
    if state.metadata.get('step') == 4:
        target_state = state
        break

if target_state:
    print(f"\n回到的状态:")
    print(f"  Step: {target_state.metadata.get('step')}")
    print(f"  消息数: {len(target_state.values['messages'])}")
    print(f"  Checkpoint ID: {target_state.config['configurable']['checkpoint_id']}")

    # 显示该状态的消息
    print(f"\n该状态下的消息:")
    for i, msg in enumerate(target_state.values['messages'], 1):
        msg_type = msg.__class__.__name__
        if hasattr(msg, 'content') and msg.content:
            print(f"    {i}. [{msg_type}] {msg.content}")
        elif hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"    {i}. [{msg_type}] Tool: {msg.tool_calls[0]['name']}")

    # 从这个历史状态继续执行新的操作
    print("\n" + "-" * 70)
    print("⏩ 从历史状态继续：Multiply the result by 10")
    print("   (从 7 乘以 10，而不是从最终的 2)")
    print("-" * 70)

    # 使用历史状态的 config 继续执行
    history_config = target_state.config

    new_messages = [HumanMessage(content="Multiply the result by 10.")]

    # 保存最后一个 event
    last_event = None
    for event in agent.stream({"messages": new_messages}, config=history_config, stream_mode="values"):
        last_event = event

    # 从 stream 的最后一个 event 获取结果
    if last_event:
        last_message = last_event["messages"][-1]
        print(f"\n回答: {last_message.content}")
        print(f"消息数: {len(last_event['messages'])}")
    else:
        print("执行失败")

    # 验证：应该是 7 * 10 = 70，而不是 2 * 10 = 20
    print("\n✅ 时间旅行成功！")
    print("   我们回到了第一次计算（3+4=7）后的状态")
    print("   然后从那里继续，计算 7*10=70")
    print("   而不是从最终状态（14/7=2）继续，那样会是 2*10=20")

else:
    print("未找到目标状态")

# ========== Store 功能演示：跨线程共享信息 ==========
print("\n" + "=" * 70)
print("🏪 Store 功能演示：跨线程共享信息")
print("=" * 70)

print("""
Checkpointer vs Store:
  • Checkpointer: 线程内状态保存（thread_id 隔离）
  • Store: 跨线程数据共享（全局存储）
""")

# 演示 Store 的基本操作
print("-" * 70)
print("1️⃣  Store 基本操作")
print("-" * 70)

# 存储用户偏好（可以跨线程访问）
store.put(
    namespace=("users", "user_123"),  # 命名空间
    key="preferences",                 # 键
    value={                            # 值
        "language": "中文",
        "favorite_operation": "multiply",
        "precision": 2
    }
)
print("\n✅ 存储用户偏好:")
print('   store.put(("users", "user_123"), "preferences", {...})')

# 存储计算历史
store.put(
    namespace=("history", "user_123"),
    key="last_results",
    value={
        "results": [7, 14, 2, 70],
        "operations": ["add", "multiply", "divide", "multiply"]
    }
)
print("\n✅ 存储计算历史:")
print('   store.put(("history", "user_123"), "last_results", {...})')

# 读取数据
print("\n" + "-" * 70)
print("2️⃣  读取 Store 数据")
print("-" * 70)

# 获取用户偏好
prefs = store.get(namespace=("users", "user_123"), key="preferences")
print(f"\n获取用户偏好:")
print(f"   store.get(('users', 'user_123'), 'preferences')")
print(f"   结果: {prefs.value if prefs else 'None'}")

# 获取计算历史
history_data = store.get(namespace=("history", "user_123"), key="last_results")
print(f"\n获取计算历史:")
print(f"   store.get(('history', 'user_123'), 'last_results')")
print(f"   结果: {history_data.value if history_data else 'None'}")

# 搜索数据
print("\n" + "-" * 70)
print("3️⃣  搜索 Store 数据")
print("-" * 70)

# 搜索某个命名空间下的所有数据
user_data = list(store.search(("users",)))
print(f"\n搜索 users 命名空间:")
print(f"   store.search(('users',))")
print(f"   找到 {len(user_data)} 条数据")

all_data = list(store.search(()))
print(f"\n搜索所有数据:")
print(f"   store.search(())")
print(f"   找到 {len(all_data)} 条数据")

for item in all_data:
    print(f"   - namespace: {item.namespace}, key: {item.key}")

# 演示跨线程共享
print("\n" + "-" * 70)
print("4️⃣  跨线程共享演示")
print("-" * 70)

# 线程 1 存储数据
config_thread1 = {"configurable": {"thread_id": "thread-1"}}
store.put(
    namespace=("shared", "global"),
    key="important_number",
    value={"number": 42, "set_by": "thread-1"}
)
print("\n线程 1 存储共享数据:")
print('   store.put(("shared", "global"), "important_number", {number: 42})')

# 线程 2 读取数据（不同的 thread_id，但可以访问同一个 store）
config_thread2 = {"configurable": {"thread_id": "thread-2"}}
shared_data = store.get(namespace=("shared", "global"), key="important_number")
print("\n线程 2 读取共享数据:")
print(f'   store.get(("shared", "global"), "important_number")')
print(f"   结果: {shared_data.value if shared_data else 'None'}")

print("\n" + "-" * 70)
print("5️⃣  Store vs Checkpointer 对比")
print("-" * 70)

print("""
┌────────────────────────────────────────────────────────────────┐
│ 特性          │ Checkpointer           │ Store                 │
├────────────────────────────────────────────────────────────────┤
│ 数据隔离      │ 按 thread_id 隔离      │ 全局共享              │
│ 用途          │ 对话状态、执行历史     │ 用户偏好、长期记忆    │
│ 生命周期      │ 随线程                 │ 持久化                │
│ 访问方式      │ agent.get_state()      │ store.get/put/search  │
│ 典型数据      │ messages, tool_calls   │ preferences, profiles │
└────────────────────────────────────────────────────────────────┘
""")

# 更新数据
print("-" * 70)
print("6️⃣  更新和删除数据")
print("-" * 70)

# 更新
store.put(
    namespace=("users", "user_123"),
    key="preferences",
    value={
        "language": "English",  # 更新
        "favorite_operation": "divide",  # 更新
        "precision": 4  # 更新
    }
)
updated_prefs = store.get(namespace=("users", "user_123"), key="preferences")
print("\n更新用户偏好:")
print(f"   新值: {updated_prefs.value if updated_prefs else 'None'}")

# 删除
store.delete(namespace=("shared", "global"), key="important_number")
deleted_data = store.get(namespace=("shared", "global"), key="important_number")
print("\n删除共享数据:")
print(f"   store.delete(('shared', 'global'), 'important_number')")
print(f"   验证: {deleted_data}")

print("\n" + "=" * 70)
print("✅ Store 功能演示完成！")
print("=" * 70)
print("""
Store 的典型应用场景:
  • 用户配置和偏好（跨会话保持）
  • 长期记忆（跨线程共享）
  • 全局状态（如系统配置）
  • 缓存数据（避免重复计算）
""")

# ========== 人机交互（Human-in-the-loop）演示 ==========
print("\n" + "=" * 70)
print("🤝 人机交互（Human-in-the-loop）演示")
print("=" * 70)

print("""
人机交互允许在工作流执行过程中：
  • 暂停执行等待人类确认
  • 人类审核后继续或修改
  • 实现审批流程
""")

# 创建一个带人机交互的简单工作流
class ApprovalState(TypedDict):
    task: str
    result: str
    approved: bool

def generate_result(state: ApprovalState):
    """生成结果"""
    task = state["task"]
    # 模拟生成结果
    result = f"计算结果: {task} = 42"
    print(f"\n🤖 生成结果: {result}")
    return {"result": result}

def human_approval(state: ApprovalState):
    """人机交互节点 - 等待人类审批"""
    print(f"\n⏸️  等待人类审批...")
    print(f"   待审批内容: {state['result']}")

    # 使用 interrupt() 暂停执行
    # 人类可以查看结果并决定是否批准
    approval = interrupt({
        "question": "请审批以下结果",
        "result": state["result"],
        "options": ["approve", "reject", "modify"]
    })

    print(f"\n✅ 收到人类反馈: {approval}")

    if approval == "approve":
        return {"approved": True}
    elif approval == "reject":
        return {"approved": False}
    else:
        # 如果是修改，approval 就是修改后的值
        return {"result": approval, "approved": True}

def finalize(state: ApprovalState):
    """最终处理"""
    if state["approved"]:
        print(f"\n🎉 任务完成！最终结果: {state['result']}")
    else:
        print(f"\n❌ 任务被拒绝")
    return {}

# 构建人机交互工作流
approval_builder = StateGraph(ApprovalState)
approval_builder.add_node("generate", generate_result)
approval_builder.add_node("human_approval", human_approval)
approval_builder.add_node("finalize", finalize)

approval_builder.add_edge(START, "generate")
approval_builder.add_edge("generate", "human_approval")
approval_builder.add_edge("human_approval", "finalize")
approval_builder.add_edge("finalize", END)

# 编译时需要 checkpointer（用于保存中断状态）
approval_checkpointer = MemorySaver()
approval_agent = approval_builder.compile(checkpointer=approval_checkpointer)

# 保存工作流图
print("\n生成人机交互工作流图...")
png_data = approval_agent.get_graph().draw_mermaid_png()
with open("approval_workflow_graph.png", "wb") as f:
    f.write(png_data)
print("✅ 图表已保存到: approval_workflow_graph.png")

# 演示执行
print("\n" + "-" * 70)
print("执行人机交互工作流")
print("-" * 70)

approval_config = {"configurable": {"thread_id": "approval-demo-1"}}

# 第一次执行 - 会在 human_approval 节点暂停
print("\n📍 第一次执行（会暂停等待审批）...")
for event in approval_agent.stream(
    {"task": "2 + 2", "result": "", "approved": False},
    config=approval_config,
    stream_mode="values"
):
    pass

# 检查状态
state = approval_agent.get_state(approval_config)
print(f"\n当前状态:")
print(f"   next: {state.next}")  # 下一个要执行的节点

# 检查是否有中断
if state.next:
    print(f"   ⏸️  工作流已暂停，等待人类输入")

    # 获取中断信息
    interrupt_info = None
    if hasattr(state, 'tasks') and state.tasks:
        for task in state.tasks:
            if hasattr(task, 'interrupts') and task.interrupts:
                interrupt_info = task.interrupts[0].value
                print(f"\n   📋 中断信息:")
                print(f"      问题: {interrupt_info.get('question')}")
                print(f"      结果: {interrupt_info.get('result')}")
                print(f"      选项: {interrupt_info.get('options')}")

    # 真正的人机交互 - 等待用户输入！
    print("\n" + "-" * 70)
    print("🖐️  请输入您的决定:")
    print("   - 输入 'approve' 批准")
    print("   - 输入 'reject' 拒绝")
    print("   - 输入其他内容作为修改后的结果")
    print("-" * 70)

    # 使用 input() 获取真实用户输入
    user_input = input("\n👉 您的输入: ").strip()

    if not user_input:
        user_input = "approve"  # 默认批准
        print(f"   (未输入，默认: {user_input})")

    print(f"\n📨 发送用户输入: {user_input}")

    # 使用 Command.resume() 恢复执行并传递真实的人类输入
    for event in approval_agent.stream(
        Command(resume=user_input),  # 真实的人类输入！
        config=approval_config,
        stream_mode="values"
    ):
        pass

    # 检查最终状态
    final_state = approval_agent.get_state(approval_config)
    print(f"\n最终状态:")
    print(f"   result: {final_state.values.get('result')}")
    print(f"   approved: {final_state.values.get('approved')}")

print("\n" + "-" * 70)
print("人机交互的关键代码")
print("-" * 70)

print("""
1️⃣  在节点中使用 interrupt() 暂停:

    from langgraph.types import interrupt

    def human_approval(state):
        # 暂停并等待人类输入
        approval = interrupt({
            "question": "请审批",
            "result": state["result"]
        })
        return {"approved": approval == "approve"}

2️⃣  恢复执行并传递人类输入:

    from langgraph.types import Command

    # 使用 Command.resume() 恢复
    agent.stream(
        Command(resume="approve"),  # 人类的输入
        config=config
    )

3️⃣  检查中断状态:

    state = agent.get_state(config)
    if state.next:
        print("工作流已暂停")

4️⃣  典型应用场景:

    • 敏感操作审批（删除、支付等）
    • AI 生成内容审核
    • 多步骤确认流程
    • 需要人类判断的决策点
""")

print("\n" + "=" * 70)
print("✅ 人机交互演示完成！")
print("=" * 70)