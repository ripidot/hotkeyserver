# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import uvicorn

app = FastAPI()

# --------------------
# DB設定
# --------------------
DATABASE_URL = "sqlite:///./logtime.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --------------------
# APIモデル定義
# --------------------
class LogEntry(BaseModel):
    message: str

class LogResponse(BaseModel):
    id: int
    message: str
    timestamp: datetime

    class Config:
        orm_mode = True

@app.post("/logs", response_model=LogResponse)
async def receive_log(entry: LogEntry):
    db = SessionLocal()
    log = Log(message=entry.message)
    db.add(log)
    db.commit()
    db.refresh(log)
    db.close()
    print(f"📥 受信ログ: {log.message}")
    return log

# ログ一覧を確認するGETエンドポイント
@app.get("/logs")
def get_logs():
    db = SessionLocal()
    logs = db.query(Log).all()
    db.close()
    return logs


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
