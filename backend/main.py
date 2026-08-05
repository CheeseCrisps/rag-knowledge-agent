import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.orm import Session

from config import settings
from core.llm import llm
from core.rag import process_and_store_pdf, query_relevant_context
from database import get_db, ChatMessage

# RAG 知识库 Agent 系统 API 入口
app = FastAPI(
    title=" RAG 知识库 Agent 系统 API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.9.0/swagger-ui.css",
    )


@app.get("/", summary="系统运行状态检查", tags=["基础运维"])
async def root():
    return {"status": "ok", "message": "FastAPI 服务运行正常！"}


@app.get("/api/v1/history", summary="获取历史聊天记录", tags=["数据库历史记录"])
def get_chat_history(db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).all()
    return {
        "status": "success",
        "data": [
            {"id": msg.id, "sender": msg.sender, "content": msg.content}
            for msg in messages
        ]
    }

# 清空历史记录接口
@app.delete("/api/v1/history", summary="清空历史聊天记录", tags=["数据库历史记录"])
def clear_chat_history(db: Session = Depends(get_db)):
    """删除 SQLite 数据库中的所有聊天记录"""
    try:
        db.query(ChatMessage).delete()
        db.commit()
        return {"status": "success", "message": "历史聊天记录已成功清空！"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"清空失败: {str(e)}"}

@app.post("/api/v1/upload-pdf", summary="上传 PDF 导入向量库", tags=["RAG 知识库服务"])
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持上传 PDF 文件！")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunk_count = await process_and_store_pdf(file_path)
        return {
            "status": "success",
            "filename": file.filename,
            "message": f"PDF 文件【{file.filename}】解析成功！已切分为 {chunk_count} 个片段保存至知识库。"
        }
    except Exception as e:
        return {"status": "error", "message": f"处理失败: {str(e)}"}


@app.get("/api/v1/rag-chat", summary="统一智能对话接口", tags=["智能 Agent 服务"])
async def rag_chat(
        question: str = Query(..., description="用户输入的问题"),
        db: Session = Depends(get_db)
):
    try:
        # 1. 保存用户提问
        user_msg = ChatMessage(sender="user", content=question)
        db.add(user_msg)
        db.commit()

        # 2. 检索向量库
        context_list = query_relevant_context(question, top_k=3)
        context_str = "\n---\n".join(context_list) if context_list else ""

        # 3. 意图判断：是否需要知识库
        router_prompt = f"""请分析【用户问题】是否需要查询个人简历、PDF文档或特定知识库。
如果属于日常打招呼、询问天气、写代码、算术或普通闲聊，回答“NO”。
如果属于查询具体的人名、简历、项目经验等文档内容，回答“YES”。

用户问题：{question}
只回答 YES 或 NO："""

        router_res = llm.invoke(router_prompt).content.strip().upper()

        # 4. 路由分流
        if "YES" in router_res and context_str:
            final_prompt = f"""请严格根据以下【参考资料】回答用户问题。

【参考资料】：
{context_str}

【用户问题】：
{question}
"""
            returned_chunks = context_list
        else:
            # 闲聊模式：完全不传入【参考资料】，物理切断简历内容
            final_prompt = question
            returned_chunks = []

        # 5. 调用大模型生成回答
        response = llm.invoke(final_prompt)
        reply_text = response.content

        # 6. 保存 AI 回复
        ai_msg = ChatMessage(sender="assistant", content=reply_text)
        db.add(ai_msg)
        db.commit()

        return {
            "status": "success",
            "question": question,
            "reply": reply_text,
            "retrieved_chunks": returned_chunks
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"响应失败: {str(e)}"}