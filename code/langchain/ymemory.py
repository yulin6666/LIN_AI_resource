from langchain_classic.memory import ConversationBufferMemory
# 实例化
memory=ConversationBufferMemory(
 return_messages=True   # 以消息类型列表形式返回历史记录
)
# 向Memory对象添加一些消息对象
memory.save_context({'human':"你好"},{"ai":"你好，有什么吩咐"})
print(memory.load_memory_variables({}))  # 加载Memory对象中历史消息


#ConversationBufferMemory
from langchain_classic.chains import ConversationChain
from langchain_openai import ChatOpenAI
openai_api_key="sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url="https://api.poixe.com/v1"

model = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)

conversation=ConversationChain(
    llm=model,
    memory=ConversationBufferMemory()
)

print(conversation.predict(input='我叫白巧克力，我喜欢写代码'))
print(conversation.predict(input='你知道我喜欢什么吗'))

#llmchain使用
from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
template = """
你是一个与人类对话的聊天机器人
{chat_history}
Human:{human_input}
聊天机器人:
"""

prompt = PromptTemplate(
    input_variables=['chat_history', "human_input"],
    template=template
)

memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=model,
    prompt=prompt,
    memory=memory,
)

print("第一轮对话：", llm_chain.invoke({"human_input": "你好，我的名字叫白巧克力，你叫什么名字"}))
print("历史记录：", llm_chain.memory.buffer)
print("第二轮对话：", llm_chain.invoke({"human_input": "你知道我叫什么名字吗"}))