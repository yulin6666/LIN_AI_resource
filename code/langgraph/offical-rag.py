# ===== Initialize Model =====
from langchain_openai import ChatOpenAI
# openai_api_key = "sk-5kE9mpbXejDV8ep6eGFSE5TbKmDhNTgROMLSoOJmvRsJFsqN"
# base_url = "https://api.poixe.com/v1"  # 自定义 OpenAI 兼容端点

# model = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     temperature=0.5,
#     timeout=10,
#     max_tokens=1000,
#     openai_api_key=openai_api_key,
#     base_url=base_url
# )
openai_api_key = "sk-c62c4cde8fe747faa4d919780339295f"
base_url = "https://api.deepseek.com/v1"  # 自定义 OpenAI 兼容端点

model = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    timeout=10,
    max_tokens=1000,
    openai_api_key=openai_api_key,
    base_url=base_url
)

# ===== embeding模型 =====
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# ===== vector store =====
from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embeddings)

# ===== Loading documents =====
from langchain_community.document_loaders import TextLoader

loader = TextLoader('../langchain/files/计算机技术与软件专业技术资格（水平）考试简介.txt',encoding='utf-8')
docs=loader.load()

assert len(docs) == 1
# print(f"Total characters: {len(docs[0].page_content)}")
# print(docs[0].page_content[:500])

#====== Splitting documents ======
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,  # chunk size (characters)
    chunk_overlap=20,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)

# print(f"Split blog post into {len(all_splits)} sub-documents.")

#====== Storing documents ======

document_ids = vector_store.add_documents(documents=all_splits)
retriever = vector_store.as_retriever()

# print(document_ids[:3])

#====== retriever_tool ======
from langchain_core.tools import tool

# 3. 手动定义工具
@tool
def retrieve_blog_posts(query: str):
    """Search and return information in files."""
    # 直接调用你上面定义好的 retriever
    docs = retriever.invoke(query)
    # 将检索到的 Document 对象列表转换为纯字符串返回
    return "\n\n".join([doc.page_content for doc in docs])

# 4. 将函数赋值给 retriever_tool，后续代码不用改
retriever_tool = retrieve_blog_posts

#===== graph model =======
from langgraph.graph import MessagesState
def generate_query_or_respond(state: MessagesState):
    """Call the model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
    """
    response = (
        model.bind_tools([retriever_tool]).invoke(state["messages"])  
    )
    return {"messages": [response]}

input = {
    "messages": [
        {
            "role": "user",
            "content": "专业资格考试多少分算通过?",
        }
    ]
}
# generate_query_or_respond(input)["messages"][-1].pretty_print()

#==== 条件边 ================
from pydantic import BaseModel, Field
from typing import Literal

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.\n"
    "You must respond with ONLY 'yes' or 'no', nothing else."
)


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )
def grade_documents(
    state: MessagesState,
) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response = model.invoke([{"role": "user", "content": prompt}])

    # Parse the response to extract 'yes' or 'no'
    score = response.content.strip().lower()

    if "yes" in score:
        return "generate_answer"
    else:
        return "rewrite_question"
    
# ====== rewrite_question node =============
from langchain.messages import HumanMessage

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)
def rewrite_question(state: MessagesState):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [HumanMessage(content=response.content)]}

# ====== generate_answer node =====
from langchain_core.messages import convert_to_messages
GENERATE_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. "
    "Use three sentences maximum and keep the answer concise.\n"
    "Question: {question} \n"
    "Context: {context}"
)


def generate_answer(state: MessagesState):
    """Generate an answer."""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}
# ====== assable=====
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

workflow = StateGraph(MessagesState)

# Define the nodes we will cycle between
workflow.add_node(generate_query_or_respond)
workflow.add_node("retrieve", ToolNode([retriever_tool]))
workflow.add_node(rewrite_question)
workflow.add_node(generate_answer)

workflow.add_edge(START, "generate_query_or_respond")

# Decide whether to retrieve
workflow.add_conditional_edges(
    "generate_query_or_respond",
    # Assess LLM decision (call `retriever_tool` tool or respond to the user)
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
workflow.add_edge("generate_answer", END)
workflow.add_edge("rewrite_question", "generate_query_or_respond")

# Compile
graph = workflow.compile()

#======  测试 =========
for chunk in graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "专业资格考试多少分算通过?",
            }
        ]
    }
):
    for node, update in chunk.items():
        print("Update from node", node)
        update["messages"][-1].pretty_print()
        print("\n\n")