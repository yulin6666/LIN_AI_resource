from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

openai_api_key="sk-nRyX1HmENCf4QEk5V0yWZKrQkIKKnEfXloy9lSOe3Jjl9AJH"
base_url="https://api.poixe.com/v1"

llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是个很有能力的助手。用20个字或更少的字回答。"),
        MessagesPlaceholder(variable_name='history'),  # 历史消息占位符
        ("human", "{input}")
    ]
)
runnable = prompt | llm

store = {}  # 存储会话历史记录
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()  
    return store[session_id]

with_message_history = RunnableWithMessageHistory(
    runnable,  # 基础链
    get_session_history,  # 历史记录获取函数
    input_messages_key='input', # 输入消息键
    history_messages_key='history' # 历史消息键
)

response = with_message_history.invoke( {"input": "什么是langchain"}, config={"configurable": {"session_id": "abc123"}} )
print(response)

response = with_message_history.invoke( {"input": "什么？"}, config={"configurable": {"session_id": "abc123"}} )
print(response)

response = with_message_history.invoke( {"input": "什么？"}, config={"configurable": {"session_id": "def234"}} )
print(response)