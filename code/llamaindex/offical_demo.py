from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core import SummaryIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

openai_api_key="sk-5kE9mpbXejDV8ep6eGFSE5TbKmDhNTgROMLSoOJmvRsJFsqN"
base_url="https://api.poixe.com/v1"

model = OpenAI(
    model="gpt-4o-mini",
    api_key=openai_api_key,
    api_base=base_url
)

# load documents
documents = SimpleDirectoryReader(input_files=["metagpt.pdf"]).load_data()

splitter = SentenceSplitter(chunk_size=1024)
nodes = splitter.get_nodes_from_documents(documents)

Settings.llm = model

summary_index = SummaryIndex(nodes)

summary_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)

summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description=(
        "Useful for summarization questions related to MetaGPT"
    ),
)

query_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        summary_tool    ],
    verbose=True
)

response = query_engine.query("What is the summary of the document?")
print(str(response))