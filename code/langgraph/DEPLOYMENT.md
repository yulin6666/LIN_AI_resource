# LangGraph Agent 部署指南

## 方法1: 使用LangGraph CLI本地开发服务器

最简单的方式，用于本地开发和测试。

### 安装CLI
```bash
pip install langgraph-cli
```

### 启动开发服务器
```bash
langgraph dev
```

访问: http://localhost:8123

---

## 方法2: 使用Docker自托管

完全控制的部署方式，适合生产环境。

### 构建并运行
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 测试API
```bash
# 健康检查
curl http://localhost:8000/health

# 查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"message": "请帮我搜索最新的AI新闻", "session_id": "test123"}'
```

---

## 方法3: 使用LangGraph Cloud（官方托管）

最简单的生产部署方式，无需管理服务器。

### 步骤

1. **安装LangGraph CLI**
```bash
pip install langgraph-cli
```

2. **登录LangSmith**
```bash
langsmith login
```

3. **部署到Cloud**
```bash
langgraph deploy
```

4. **获取API端点**
部署完成后会得到一个API端点URL，例如：
```
https://your-app.langgraph.cloud
```

5. **调用API**
```python
import requests

response = requests.post(
    "https://your-app.langgraph.cloud/invoke",
    json={
        "input": {
            "messages": [{"role": "user", "content": "查询北京天气"}]
        }
    },
    headers={"Authorization": f"Bearer {api_key}"}
)
```

---

## 方法4: 部署到其他云平台

### AWS (使用ECS/Fargate)

1. **推送镜像到ECR**
```bash
# 登录ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 构建并推送
docker build -t langgraph-agent .
docker tag langgraph-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/langgraph-agent:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/langgraph-agent:latest
```

2. **创建ECS任务和服务**（通过AWS Console或Terraform）

### Google Cloud Run

```bash
# 构建并推送到GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/langgraph-agent

# 部署到Cloud Run
gcloud run deploy langgraph-agent \
  --image gcr.io/PROJECT-ID/langgraph-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# 登录Azure
az login

# 创建资源组
az group create --name langgraph-rg --location eastus

# 部署容器
az container create \
  --resource-group langgraph-rg \
  --name langgraph-agent \
  --image <your-registry>/langgraph-agent:latest \
  --dns-name-label langgraph-agent \
  --ports 8000
```

---

## 环境变量配置

在部署前确保设置以下环境变量：

- `LANGCHAIN_API_KEY`: LangSmith API密钥
- `LANGCHAIN_PROJECT`: 项目名称
- `OPENAI_API_KEY`: OpenAI API密钥
- `OPENAI_BASE_URL`: OpenAI API地址
- `TAVILY_API_KEY`: Tavily搜索API密钥

---

## 监控和日志

### 使用LangSmith监控
所有部署方式都可以通过LangSmith进行监控：
- 访问: https://smith.langchain.com
- 查看traces、性能指标和调试信息

### Docker日志
```bash
docker-compose logs -f langgraph-api
```

---

## 生产环境最佳实践

1. **使用环境变量管理密钥**，不要硬编码
2. **启用HTTPS**（使用Nginx反向代理或云平台的负载均衡器）
3. **配置速率限制**防止滥用
4. **设置健康检查**确保服务可用性
5. **启用自动扩展**应对流量高峰
6. **定期备份数据**（如果使用持久化存储）
7. **监控和告警**使用LangSmith或云平台的监控工具
