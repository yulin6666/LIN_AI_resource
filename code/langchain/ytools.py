from langchain_core.tools import tool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")

@tool("multiplication-tool",args_schema=CalculatorInput,return_direct=True)
def multiply(a: int, b: int) -> int:
    """两数相乘"""  # 工具的描述
    return a * b

# print(multiply.name)
# print(multiply.description)
# print(multiply.args)
# print(multiply.return_direct)


import asyncio
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")

def multiply(a: int, b: int) -> int:
    """同步两数相乘"""
    return a * b
async def amultiply(a: int, b: int) -> int:
    """异步两数相乘"""
    return a * b
async def main():
    calculator = StructuredTool.from_function(
        func=multiply,
        coroutine=amultiply,
        description="两数相乘",
        args_schema=CalculatorInput,
        return_direct=True,
    )
    print(calculator.invoke({"a": 2, "b": 3}))      # invoke同步调用
    print(await calculator.ainvoke({"a": 2, "b": 5}))   # ainvoke是异步调用

asyncio.run(main())

from langchain_community.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field, ConfigDict

class CalculatorInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")

class DivisionTool(BaseTool):
    name: str = "除法"
    description: str = "两数相除"
    args_schema: Type[BaseModel] = CalculatorInput
    return_direct: bool = True
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, a: float, b: float) -> float:
        """两数相除"""
        try:
            return a / b
        except Exception as e:
            return e

Division_tool = DivisionTool()
result = Division_tool.run({'a': 1.0, 'b': 2})
print(result)

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

api_wrapper=WikipediaAPIWrapper(
 top_k_results=1,        # 搜索结果数量
    doc_content_chars_max=100   # 获取的页面内容的最大字符长度
)
tool=WikipediaQueryRun(api_wrapper=api_wrapper)
print(tool.invoke({"query":"中国首都在哪里？"}))