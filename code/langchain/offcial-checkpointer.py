"""演示 Checkpointer 的作用 - 对话记忆系统"""

from dataclasses import dataclass
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

try:
    from langchain.agents import create_react_agent
except ImportError:
    from langgraph.prebuilt import create_react_agent

# ===== 配置 =====
openai_api_key = "sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url = "https://api.poixe.com/v1"

model = ChatOpenAI(
    model="gpt-4",
    temperature=0.5,
    openai_api_key=openai_api_key,
    base_url=base_url
)

# ===== 简单工具 =====
@tool
def get_city_info(city: str) -> str:
    """Get information about a city."""
    info_db = {
        "Beijing": "北京是中国的首都，人口约2100万",
        "Shanghai": "上海是中国最大的城市，人口约2400万",
        "Paris": "巴黎是法国首都，以埃菲尔铁塔闻名"
    }
    return info_db.get(city, f"{city} 的信息暂不可用")

# ===== 演示 1: 没有 Checkpointer =====
print("=" * 70)
print("演示 1: 没有 Checkpointer（无记忆）")
print("=" * 70)

agent_no_memory = create_react_agent(
    model=model,
    tools=[get_city_info],
    checkpointer=None  # ← 关键：没有 checkpointer
)

print("\n第一轮对话:")
print("用户: 'Tell me about Beijing'")
response1 = agent_no_memory.invoke({
    "messages": [HumanMessage(content="Tell me about Beijing")]
})
print(f"Agent: {response1['messages'][-1].content[:100]}...")

print("\n第二轮对话:")
print("用户: 'What was the city I just asked about?'")
response2 = agent_no_memory.invoke({
    "messages": [HumanMessage(content="What was the city I just asked about?")]
})
print(f"Agent: {response2['messages'][-1].content[:150]}...")

print("\n❌ 结果: Agent 不记得之前聊过 Beijing！")
print("   原因: 没有 checkpointer，每次都是新对话")

# ===== 演示 2: 有 Checkpointer =====
print("\n" + "=" * 70)
print("演示 2: 有 Checkpointer（有记忆）")
print("=" * 70)

checkpointer = MemorySaver()

agent_with_memory = create_react_agent(
    model=model,
    tools=[get_city_info],
    checkpointer=checkpointer  # ← 关键：有 checkpointer
)

# 使用同一个 thread_id
config = {"configurable": {"thread_id": "conversation_1"}}

print("\n第一轮对话:")
print("用户: 'Tell me about Beijing'")
response1 = agent_with_memory.invoke({
    "messages": [HumanMessage(content="Tell me about Beijing")]
}, config=config)
print(f"Agent: {response1['messages'][-1].content[:100]}...")

print("\n第二轮对话（使用相同 thread_id）:")
print("用户: 'What was the city I just asked about?'")
response2 = agent_with_memory.invoke({
    "messages": [HumanMessage(content="What was the city I just asked about?")]
}, config=config)  # ← 相同的 config
print(f"Agent: {response2['messages'][-1].content[:150]}...")

print("\n✅ 结果: Agent 记得之前聊过 Beijing！")
print("   原因: checkpointer 保存了对话历史")

# ===== 演示 3: 查看 Checkpointer 保存的内容 =====
print("\n" + "=" * 70)
print("演示 3: 查看 Checkpointer 保存的内容")
print("=" * 70)

print("\n查看保存的对话历史:")
print("-" * 70)

# 获取当前状态
state = agent_with_memory.get_state(config)

print(f"Thread ID: {config['configurable']['thread_id']}")
print(f"消息总数: {len(state.values.get('messages', []))}")
print(f"\n对话历史:")

for i, msg in enumerate(state.values.get('messages', []), 1):
    msg_type = msg.__class__.__name__
    if msg_type == 'HumanMessage':
        print(f"  {i}. [用户] {msg.content}")
    elif msg_type == 'AIMessage':
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"  {i}. [AI] 调用工具: {[tc['name'] for tc in msg.tool_calls]}")
        else:
            print(f"  {i}. [AI] {msg.content[:80]}...")
    elif msg_type == 'ToolMessage':
        print(f"  {i}. [工具返回] {msg.content[:50]}...")

# ===== 演示 4: 不同 thread_id 的隔离性 =====
print("\n" + "=" * 70)
print("演示 4: 不同 thread_id 的隔离性")
print("=" * 70)

# 创建新的对话线程
config2 = {"configurable": {"thread_id": "conversation_2"}}

print("\n在新的线程中对话:")
print("用户: 'What was the city I asked about?'")
response3 = agent_with_memory.invoke({
    "messages": [HumanMessage(content="What was the city I asked about?")]
}, config=config2)  # ← 不同的 thread_id
print(f"Agent: {response3['messages'][-1].content[:150]}...")

print("\n✅ 结果: 新线程不记得 Beijing")
print("   原因: 不同 thread_id 有独立的对话历史")

# ===== 演示 5: Checkpointer 的实际结构 =====
print("\n" + "=" * 70)
print("演示 5: Checkpointer 内部存储结构")
print("=" * 70)

print("\nMemorySaver 存储的数据结构（简化）:")
print("-" * 70)
print("""
MemorySaver = {
    "conversation_1": {  ← thread_id
        "messages": [
            HumanMessage("Tell me about Beijing"),
            AIMessage(tool_calls=[...]),
            ToolMessage("北京是中国的首都..."),
            AIMessage("Beijing is the capital..."),
            HumanMessage("What was the city I just asked about?"),
            AIMessage("You asked about Beijing")
        ],
        "step": 2,
        ...
    },
    "conversation_2": {  ← 另一个 thread_id
        "messages": [
            HumanMessage("What was the city I asked about?"),
            AIMessage("I don't have that information...")
        ],
        ...
    }
}
""")

# ===== 演示 6: 持久化对比 =====
print("\n" + "=" * 70)
print("演示 6: 不同 Checkpointer 类型对比")
print("=" * 70)

print("""
┌────────────────────┬──────────────────┬──────────────────┐
│ Checkpointer 类型  │ 数据存储位置     │ 用途             │
├────────────────────┼──────────────────┼──────────────────┤
│ MemorySaver        │ 内存（程序运行时）│ 开发、测试       │
│ SqliteSaver        │ SQLite 数据库    │ 本地持久化       │
│ PostgresSaver      │ PostgreSQL       │ 生产环境         │
│ None               │ 不保存           │ 无状态对话       │
└────────────────────┴──────────────────┴──────────────────┘

示例:

# 内存存储（重启后消失）
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# SQLite 持久化（保存到文件）
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# 不使用 checkpointer
checkpointer = None
""")

# ===== 演示 7: 实际应用场景 =====
print("\n" + "=" * 70)
print("演示 7: 实际应用场景")
print("=" * 70)

print("""
🎯 使用场景:

1. **多轮对话客服**
   thread_id = user_session_id
   → 用户可以追问、补充问题

2. **个人助手**
   thread_id = user_id
   → 记住用户偏好、历史操作

3. **调试和审计**
   保存完整对话历史
   → 回溯问题、分析决策

4. **A/B 测试**
   不同 thread_id 测试不同策略
   → 对比效果

5. **协作任务**
   thread_id = task_id
   → 多个 Agent 共享任务上下文
""")

print("\n" + "=" * 70)
print("演示完成！")
print("=" * 70)

print("""
🔑 关键要点:

1. checkpointer = MemorySaver() → 启用对话记忆
2. thread_id → 标识不同的对话线程
3. 相同 thread_id → 共享对话历史
4. 不同 thread_id → 独立对话历史
5. 无 checkpointer → 每次都是新对话

💡 记住公式:
   有记忆 = checkpointer + 相同的 thread_id
   无记忆 = 无 checkpointer 或 不同的 thread_id
""")
