# ===== Initialize Model =====
from langchain_openai import ChatOpenAI
openai_api_key = "sk-c62c4cde8fe747faa4d919780339295f"
base_url = "https://api.deepseek.com/v1"

model = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    timeout=10,
    max_tokens=1000,
    openai_api_key=openai_api_key,
    base_url=base_url
)

# ===== Bazi Tool Definition =====
from langchain_core.tools import tool
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lunar'))
from bazi import calculate_bazi, print_bazi_result
from datetime import datetime

@tool
def calculate_bazi_tool(year: int, month: int, day: int, hour: int, minute: int, gender: str):
    """Calculate Bazi (Eight Characters) based on birth date and time.

    Args:
        year: Birth year (e.g., 1990)
        month: Birth month (1-12)
        day: Birth day (1-31)
        hour: Birth hour (0-23)
        minute: Birth minute (0-59)
        gender: Gender ("male" or "female")

    Returns:
        Detailed Bazi analysis including four pillars, five elements, ten gods, major fortune cycles, etc.
    """
    # Convert gender string to int (1 for male, 0 for female)
    gender_int = 1 if gender.lower() == "male" else 0

    # Calculate Bazi
    result = calculate_bazi(year, month, day, hour, minute, gender_int)

    # Format the output as a comprehensive string
    output = f"""
Bazi Analysis Result:
====================
【Basic Information】
Gregorian Date: {result['user_info']['阳历']}
Lunar Date: {result['user_info']['农历']}
Chinese Zodiac: {result['user_info']['生肖']}
Gender: {result['user_info']['性别']}

【Four Pillars of Destiny】
Day Master: {result['day_master']}
Year Pillar (年柱): {result['bazi']['年柱']}
Month Pillar (月柱): {result['bazi']['月柱']}
Day Pillar (日柱): {result['bazi']['日柱']}
Hour Pillar (时柱): {result['bazi']['时柱']}

【Five Elements Analysis】
Year Pillar Five Elements: {result['wuxing']['detail']['年柱五行']}
Month Pillar Five Elements: {result['wuxing']['detail']['月柱五行']}
Day Pillar Five Elements: {result['wuxing']['detail']['日柱五行']}
Hour Pillar Five Elements: {result['wuxing']['detail']['时柱五行']}

Five Elements Count: {str(result['wuxing']['counts'])}

【Na Yin (Sound of Elements)】
Year: {result['nayin']['年柱纳音']}
Month: {result['nayin']['月柱纳音']}
Day: {result['nayin']['日柱纳音']}
Hour: {result['nayin']['时柱纳音']}

【Ten Gods (Shi Shen)】
Year Stem Ten God: {result['shi_shen']['年干十神']}
Month Stem Ten God: {result['shi_shen']['月干十神']}
Hour Stem Ten God: {result['shi_shen']['时干十神']}

Beginning of Fortune (起运) Age: {result['qi_yun']['起运描述']}

【Major Fortune Cycles (大运)】
"""
    for dy in result['da_yun'][:5]:  # Show first 5 cycles
        output += f"Cycle {dy['序号']}: {dy['大运干支']} | Age {dy['起运年龄']}-{dy['结束年龄']} | Year {dy['起运年份']}\n"

    output += "\n【 流年运势 】- 第一步大运的流年示例 (前10年) \n"
    if result['liu_nian']:
        for ln in result['liu_nian'][:10]:
            output += f"Year {ln['年份']} | Age {ln['年龄']} | Stem-Branch {ln['干支']}\n"
    else:
        output += "No yearly fortune data available."

    output += "\n===================="

    return output

# ===== Graph State =====
from langgraph.graph import MessagesState

# ===== Node Functions =====
def process_user_input(state: MessagesState):
    """Process user input to extract birth date information."""
    messages = state["messages"]
    user_message = messages[-1].content

    # Use model to extract birth date information
    response = model.bind_tools([calculate_bazi_tool]).invoke(messages)
    return {"messages": [response]}

# ===== Conditional Edges =====
from pydantic import BaseModel, Field
from typing import Literal

GRADE_PROMPT = (
    "You are a grader assessing whether the user's message contains birth date information needed for Bazi calculation. "
    "The user should provide: year, month, day, hour, minute, and gender. "
    "Give a binary score 'yes' or 'no' to indicate whether all required information is present.\n"
    "You must respond with ONLY 'yes' or 'no', nothing else.\n"
)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

def grade_user_input(state: MessagesState) -> Literal["extract_info", "respond_help"]:
    """Determine whether user provided all required birth date information."""
    messages = state["messages"]
    user_message = messages[0].content.lower()

    # Check if message contains all required information
    has_date = any(str(year) in user_message for year in range(1900, 2030))
    has_gender = any(word in user_message for word in ["male", "female", "男", "女", "man", "woman"])
    has_time = any(char.isdigit() for char in user_message)

    if has_date and has_gender and has_time:
        return "extract_info"
    else:
        return "respond_help"

# ===== Response Helper Node =====
def respond_help(state: MessagesState):
    """Provide help message asking for required information."""
    help_message = (
        "To calculate your Bazi (Eight Characters), I need the following information:\n\n"
        "1. Birth date (Gregorian calendar): Year, Month, Day\n"
        "2. Birth time: Hour and Minute (24-hour format)\n"
        "3. Gender: Male or Female\n\n"
        "Please provide all information in a single message, for example:\n"
        "\"I was born on 1990-03-15 at 14:30, male\"\n"
        "\"Female, 1987-08-22, 22:15\"\n\n"
        "Note: The input supports both Chinese and English."
    )
    return {"messages": [{"role": "assistant", "content": help_message}]}

# ===== Assemble Graph =====
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

workflow = StateGraph(MessagesState)

# Define nodes
workflow.add_node("process_input", process_user_input)
workflow.add_node("tools", ToolNode([calculate_bazi_tool]))
workflow.add_node("help", respond_help)

# Define edges
workflow.add_edge(START, "process_input")

# Conditional edges based on whether tools were called
workflow.add_conditional_edges(
    "process_input",
    tools_condition,
    {
        "tools": "tools",
        END: "help",
    },
)
workflow.add_edge("tools", END)
workflow.add_edge("help", END)

# Compile
graph = workflow.compile()

# ===== Test =====
if __name__ == "__main__":
    # Test with different inputs
    test_inputs = [
        {
            "messages": [
                {
                    "role": "user",
                    "content": "我出生于1990年5月15日下午3点30分，性别男"
                }
            ]
        },
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Calculate Bazi for female born on 1988-12-25 at 08:20"
                }
            ]
        }
    ]

    for test_input in test_inputs:
        print("\n" + "="*50)
        print("测试新的用户输入")
        print("="*50)

        for chunk in graph.stream(test_input):
            for node, update in chunk.items():
                print(f"Node: {node}")
                if "messages" in update and update["messages"]:
                    last_message = update["messages"][-1]
                    if hasattr(last_message, 'content'):
                        print(f"Content: {last_message.content}")
                    else:
                        print(f"Message: {last_message}")
        print("\n")

    # INTERACTIVE MODE
    print("\n" + "="*50)
    print("交互模式")
    print("输入 'exit' 或 'quit' 退出")
    print("="*50)

    while True:
        user_input = input("\n请输入您的出生信息: ")

        if user_input.lower() in ['exit', 'quit', '退出']:
            print("感谢使用!")
            break

        if not user_input.strip():
            continue

        inputs = {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

        print("\n" + "-"*30)
        print("生成中...")
        print("-"*30 + "\n")

        try:
            for chunk in graph.stream(inputs):
                for node, update in chunk.items():
                    if "messages" in update and update["messages"]:
                        last_message = update["messages"][-1]
                        if hasattr(last_message, 'content'):
                            print(f"Content: {last_message.content}")
                        else:
                            print(f"Message: {last_message}")
            print("\n")
        except Exception as e:
            print(f"发生错误: {e}")
            print("请检查输入格式是否正确")
            print("格式示例: \"1990年5月15日15:30，男\" 或 \"生于1988年3月20日早上8点，女性\"")