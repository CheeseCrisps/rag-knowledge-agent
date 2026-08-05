# 🤖 RAG Knowledge Agent System

> 基于 **FastAPI + LangChain + ChromaDB + DeepSeek API** 搭建的自适应企业级 RAG 知识库助手。

---

## 🌟 核心亮点 (Key Features)

- 🚀 **自适应意图路由 (Adaptive Intent Router)**：自动判别用户提问类型。文档类问题触发向量库检索；闲聊/编程等通用问题自动切断向量上下文，彻底解决传统 RAG 系统的机械拒答痛点。
- 📄 **RAG 向量检索流水线**：支持 PDF 文档动态切片（Chunking）、向量化存储与高维相似度检索 (Similarity Search)。
- 💾 **多轮对话历史持久化**：基于 SQLite + SQLAlchemy 实时保存对话记录，支持历史恢复与一键物理清空。
- ⚡ **高性能 API 与交互**：FastAPI 后端集成 CORS 与 Swagger 文档，前端提供现代化响应式双栏界面。

---

## 🛠️ 技术栈 (Tech Stack)

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Uvicorn
- **AI / RAG**: LangChain, ChromaDB, PyPDF, DeepSeek API
- **Frontend**: HTML5, CSS3, JavaScript (Fetch API)
- **Database**: SQLite, Chroma Vector DB

---

## 📂 项目结构 (Directory Structure)

```text
rag-knowledge-agent/
├── backend/            # 后端 FastAPI 服务与 RAG 核心逻辑
│   ├── core/           # LLM 与 RAG 路由逻辑
│   ├── config.py       # 配置文件
│   ├── database.py     # SQLite 数据库模型
│   └── main.py         # RESTful API 入口
├── frontend/           # 前端交互界面
│   └── index.html
├── .gitignore          # Git 忽略配置
└── README.md           # 项目说明文档
