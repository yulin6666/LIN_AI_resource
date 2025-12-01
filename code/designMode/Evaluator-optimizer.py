from typing_extensions import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# 配置 LLM
openai_api_key = "sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url = "https://api.poixe.com/v1"

llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)

# Graph state
class State(TypedDict):
    joke: str
    topic: str
    feedback: str
    funny_or_not: str


# Schema for structured output to use in evaluation
class Feedback(BaseModel):
    grade: Literal["funny", "not funny"] = Field(
        description="Decide if the joke is funny or not.",
    )
    feedback: str = Field(
        description="If the joke is not funny, provide feedback on how to improve it.",
    )


# Augment the LLM with schema for structured output
evaluator = llm.with_structured_output(Feedback)


# 计数器
iteration_count = 0

# Nodes
def llm_call_generator(state: State):
    """LLM generates a joke"""
    global iteration_count
    iteration_count += 1

    print(f"\n🎭 Generator - 第 {iteration_count} 次尝试")

    if state.get("feedback"):
        print(f"   📝 收到反馈: {state['feedback']}")
        msg = llm.invoke(
            f"Write a joke about {state['topic']} but take into account the feedback: {state['feedback']}"
        )
    else:
        print(f"   📝 首次生成，主题: {state['topic']}")
        msg = llm.invoke(f"Write a joke about {state['topic']}")

    print(f"   🎤 生成的笑话: {msg.content[:100]}...")
    return {"joke": msg.content}


def llm_call_evaluator(state: State):
    """LLM evaluates the joke"""

    print(f"\n🔍 Evaluator - 评估笑话")

    # 评估器知道一些老套笑话
    grade = evaluator.invoke(
        f"""Grade this joke. Mark as 'funny' if it has some creativity or clever wordplay.

        IMPORTANT: The following jokes are overused and should ALWAYS be marked as 'not funny':
        - "Why was the cat sitting on the computer? Because it wanted to keep an eye on the mouse!"
        - Any variation of cat + computer + mouse joke
        - "Why did the chicken cross the road?"

        If you see these old jokes, provide feedback suggesting a completely different topic or angle.

        Joke: {state['joke']}"""
    )

    print(f"   📊 评分: {grade.grade}")
    if grade.grade == "not funny":
        print(f"   💡 改进建议: {grade.feedback}")

    return {"funny_or_not": grade.grade, "feedback": grade.feedback}


# Conditional edge function to route back to joke generator or end based upon feedback from the evaluator
def route_joke(state: State):
    """Route back to joke generator or end based upon feedback from the evaluator"""

    if state["funny_or_not"] == "funny":
        return "Accepted"
    elif state["funny_or_not"] == "not funny":
        return "Rejected + Feedback"


# Build workflow
optimizer_builder = StateGraph(State)

# Add the nodes
optimizer_builder.add_node("llm_call_generator", llm_call_generator)
optimizer_builder.add_node("llm_call_evaluator", llm_call_evaluator)

# Add edges to connect nodes
optimizer_builder.add_edge(START, "llm_call_generator")
optimizer_builder.add_edge("llm_call_generator", "llm_call_evaluator")
optimizer_builder.add_conditional_edges(
    "llm_call_evaluator",
    route_joke,
    {  # Name returned by route_joke : Name of next node to visit
        "Accepted": END,
        "Rejected + Feedback": "llm_call_generator",
    },
)

# Compile the workflow
optimizer_workflow = optimizer_builder.compile()

# Show the workflow - 保存为文件
print("生成评估器-优化器工作流图表...")
png_data = optimizer_workflow.get_graph().draw_mermaid_png()
with open("evaluator_optimizer_graph.png", "wb") as f:
    f.write(png_data)
print("✅ 图表已保存到: evaluator_optimizer_graph.png")
print("   使用命令查看: open evaluator_optimizer_graph.png\n")

# Invoke
print("=" * 70)
print("开始生成笑话 (使用严格评估模式)")
print("=" * 70)

# 增加递归限制，允许更多次循环
state = optimizer_workflow.invoke(
    {"topic": "Cats"},
    {"recursion_limit": 50}  # 默认是 25
)

print("\n" + "=" * 70)
print(f"✅ 完成！共经过 {iteration_count} 次循环")
print("=" * 70)
print("\n最终笑话:")
print(state["joke"])
print(f"\n评估结果: {state['funny_or_not']}")