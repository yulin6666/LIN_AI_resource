# ===== Initialize Model =====
from langchain_openai import ChatOpenAI
openai_api_key = "sk-5kE9mpbXejDV8ep6eGFSE5TbKmDhNTgROMLSoOJmvRsJFsqN"
base_url = "https://api.poixe.com/v1"  # 自定义 OpenAI 兼容端点

model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5,
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

loader = TextLoader('files/计算机技术与软件专业技术资格（水平）考试简介.txt',encoding='utf-8')
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

print(f"Split blog post into {len(all_splits)} sub-documents.")

#====== Storing documents ======

document_ids = vector_store.add_documents(documents=all_splits)

print(document_ids[:3])

#====== rag ======
from typing import Any
from langchain_core.documents import Document
from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain.agents import create_agent

class State(AgentState):
    context: list[Document]


class RetrieveDocumentsMiddleware(AgentMiddleware[State]):
    state_schema = State

    def before_model(self, state: AgentState) -> dict[str, Any] | None:
        last_message = state["messages"][-1]
        retrieved_docs = vector_store.similarity_search(last_message.text)

        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        augmented_message_content = (
            f"{last_message.text}\n\n"
            "Use the following context to answer the query:\n"
            f"{docs_content}"
        )
        return {
            "messages": [last_message.model_copy(update={"content": augmented_message_content})],
            "context": retrieved_docs,
        }


agent = create_agent(
    model,
    tools=[],
    middleware=[RetrieveDocumentsMiddleware()],
)
#======== test =====
query = (
    "专业资格考试多少分算通过?"
)

for step in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()