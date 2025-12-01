from langgraph.types import Send
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field
import operator
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# 配置 LLM
openai_api_key = "sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url = "https://api.poixe.com/v1"

llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)

# Schema for report sections
class Section(BaseModel):
    """Schema for a section of the report"""
    name: str = Field(description="Name of the section")
    description: str = Field(description="Description of what should be in the section")

class Sections(BaseModel):
    """Schema for the list of sections"""
    sections: list[Section]

# Planner LLM with structured output
planner = llm.with_structured_output(Sections)

# Graph state
class State(TypedDict):
    topic: str  # Report topic
    sections: list[Section]  # List of report sections
    completed_sections: Annotated[
        list, operator.add
    ]  # All workers write to this key in parallel
    final_report: str  # Final report


# Worker state
class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[list, operator.add]


# Nodes
def orchestrator(state: State):
    """Orchestrator that generates a plan for the report"""

    print("\n📋 Orchestrator 开始制定计划...")

    # Generate queries
    report_sections = planner.invoke(
        [
            SystemMessage(content="Generate a plan for the report."),
            HumanMessage(content=f"Here is the report topic: {state['topic']}"),
        ]
    )

    print(f"✅ 计划完成！生成了 {len(report_sections.sections)} 个章节:")
    for i, section in enumerate(report_sections.sections, 1):
        print(f"   {i}. {section.name}")

    return {"sections": report_sections.sections}


def llm_call(state: WorkerState):
    """Worker writes a section of the report"""

    section_name = state['section'].name
    print(f"   🔨 Worker 开始撰写: {section_name}")

    # Generate section
    section = llm.invoke(
        [
            SystemMessage(
                content="Write a report section following the provided name and description. Include no preamble for each section. Use markdown formatting."
            ),
            HumanMessage(
                content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
            ),
        ]
    )

    print(f"   ✅ Worker 完成: {section_name}")

    # 关键：返回的内容会通过 operator.add 合并到 state["completed_sections"]
    # 每个 worker 返回一个列表，LangGraph 会自动执行:
    # completed_sections = completed_sections + [section.content]
    result = {"completed_sections": [section.content]}
    print(f"      → 写入 completed_sections: [章节内容 {len(section.content)} 字符]")

    # Write the updated section to completed sections
    return result


def synthesizer(state: State):
    """Synthesize full report from sections"""

    print(f"\n📝 Synthesizer 开始合成最终报告...")

    # List of completed sections
    completed_sections = state["completed_sections"]

    print(f"   收到 {len(completed_sections)} 个已完成的章节")
    print(f"\n   ⚠️  重要：章节的顺序 = Workers 完成的顺序（不是原始计划顺序）")
    print(f"   实际收集到的章节顺序:")
    for i, section in enumerate(completed_sections, 1):
        # 提取章节标题（第一行通常是标题）
        title = section.split('\n')[0].strip('#').strip()[:50]
        print(f"      {i}. {title}")

    # Format completed section to str to use as context for final sections
    completed_report_sections = "\n\n---\n\n".join(completed_sections)

    print(f"\n   ✅ 报告合成完成!\n")

    return {"final_report": completed_report_sections}


# Conditional edge function to create llm_call workers that each write a section of the report
def assign_workers(state: State):
    """Assign a worker to each section in the plan"""

    print(f"\n🚀 使用 Send() API 动态创建 Workers...")
    print(f"   共需创建 {len(state['sections'])} 个并行的 llm_call 实例\n")

    # Kick off section writing in parallel via Send() API
    # 关键：每个 Send 对象 = 一个独立的节点执行实例
    send_list = [Send("llm_call", {"section": s}) for s in state["sections"]]

    print(f"   ✅ 已创建 {len(send_list)} 个 Send 对象")
    print(f"   → LangGraph 将并行执行这些 workers\n")

    return send_list


# Build workflow
orchestrator_worker_builder = StateGraph(State)

# Add the nodes
orchestrator_worker_builder.add_node("orchestrator", orchestrator)
orchestrator_worker_builder.add_node("llm_call", llm_call)
orchestrator_worker_builder.add_node("synthesizer", synthesizer)

# Add edges to connect nodes
orchestrator_worker_builder.add_edge(START, "orchestrator")
orchestrator_worker_builder.add_conditional_edges(
    "orchestrator", assign_workers, ["llm_call"]
)
orchestrator_worker_builder.add_edge("llm_call", "synthesizer")
orchestrator_worker_builder.add_edge("synthesizer", END)

# Compile the workflow
orchestrator_worker = orchestrator_worker_builder.compile()

# Show the workflow - 保存为文件
print("生成编排-工作者工作流图表...")
png_data = orchestrator_worker.get_graph().draw_mermaid_png()
with open("orchestrator_worker_graph.png", "wb") as f:
    f.write(png_data)
print("✅ 图表已保存到: orchestrator_worker_graph.png")
print("   使用命令查看: open orchestrator_worker_graph.png\n")

# Invoke
print("\n" + "=" * 70)
print("开始演示 Send() API 的动态并行执行")
print("=" * 70)
state = orchestrator_worker.invoke({"topic": "Create a report on LLM scaling laws"})

print("=" * 70)
print("最终报告:")
print("=" * 70 + "\n")
print(state["final_report"])