from langchain_openai import ChatOpenAI
from config import settings

# 初始化 DeepSeek 大模型实例
llm = ChatOpenAI(
    model="deepseek-chat",               # 使用 DeepSeek-V3 模型
    api_key=settings.DEEPSEEK_API_KEY,   # 从 config 自动读取 .env 里的 Key
    base_url="https://api.deepseek.com",  # DeepSeek 官方 API 接口地址
    temperature=0.7
)