from langchain_core.documents import Document

documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"source": "mammal-pets-doc"},
    ),
]

from langchain_community.document_loaders import PyPDFLoader

file_path = "./files/nke-10k-2023.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

# print(f"{docs[0].page_content[:200]}\n")
# print(docs[0].metadata)

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

# print(len(all_splits))
# print(all_splits[0])

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

print("✅ 使用本地模型: all-mpnet-base-v2")

vector_1 = embeddings.embed_query(all_splits[0].page_content)
vector_2 = embeddings.embed_query(all_splits[1].page_content)

# print(f"\n📊 向量维度信息:")
# print(f"  vector_1 维度: {len(vector_1)}")
# print(f"  vector_2 维度: {len(vector_2)}")

# assert len(vector_1) == len(vector_2)
# print(f"\n✅ 维度一致性检查通过")

# print(f"\n向量示例 (前10个值):")
# print(f"  vector_1[:10] = {vector_1[:10]}")
# print(f"  vector_2[:10] = {vector_2[:10]}")

from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embeddings)

ids = vector_store.add_documents(documents=all_splits)

results = vector_store.similarity_search(
    "How many distribution centers does Nike have in the US?"
)

print(results[0])