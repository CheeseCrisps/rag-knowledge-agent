from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 本地 SQLite 数据库文件地址
SQLITE_DATABASE_URL = "sqlite:///./chat_history.db"

engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 定义聊天记录表结构
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(20), index=True)  # 'user' 或 'assistant'
    content = Column(Text, nullable=False)   # 消息内容
    created_at = Column(DateTime, default=datetime.utcnow) # 记录时间

# 自动创建表
Base.metadata.create_all(bind=engine)

# 数据库 Session 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()