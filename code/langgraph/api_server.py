import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 配置LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "ytavily")

# 初始化FastAPI
app = FastAPI(
    title="LangGraph Search Agent API",
    description="基于LangGraph的搜索Agent服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Agent
openai_api_key = os.getenv("OPENAI_API_KEY", "")
base_url = os.getenv("OPENAI_BASE_URL", "https://api.poixe.com/v1")
tavily_api_key = os.getenv("TAVILY_API_KEY", "")

model = ChatOpenAI(
    openai_api_key=openai_api_key,
    base_url=base_url
)
search_tool = TavilySearch(
    max_results=5,
    topic="general",
    tavily_api_key=tavily_api_key
)
tools = [search_tool]
search_agent = create_react_agent(model=model, tools=tools)

# 请求模型
class QueryRequest(BaseModel):
    message: str
    session_id: str = "default"

class QueryResponse(BaseModel):
    answer: str
    session_id: str

# API端点
@app.get("/")
async def root():
    return {
        "message": "LangGraph Search Agent API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "query": "/query"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    查询Agent
    """
    try:
        response = search_agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        })

        # 获取最终答案
        final_message = response['messages'][-1]
        answer = final_message.content

        return QueryResponse(
            answer=answer,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream_query(request: QueryRequest):
    """
    流式查询Agent（未来实现）
    """
    return {"message": "Stream endpoint - Coming soon"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
