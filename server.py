# server.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from datetime import datetime
import uvicorn
app = FastAPI()

# --------------------
# DB設定
# --------------------
DATABASE_URL = "sqlite:///./loguser3.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --------------------
# DBモデル
# --------------------
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    logs = relationship("Log", back_populates="user")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("User", back_populates="logs")

Base.metadata.create_all(bind=engine)

# --------------------
# Pydanticモデル
# --------------------
class LogEntry(BaseModel):
    message: str
    user_id: int  # 今回は簡易的にuser_idをリクエストに含める

class LogResponse(BaseModel):
    id: int
    message: str
    timestamp: datetime
    user_id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str  # 今は生のままで（セキュア対応は後で）

class UserResponse(BaseModel):
    user_id: int
    username: str

    class Config:
        orm_mode = True

# --------------------
# DBセッション依存
# --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------
# APIエンドポイント
# --------------------
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = User(username=user.username, password_hash=user.password)  # ⚠️後でハッシュ化が必要
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/logs", response_model=LogResponse)
def create_log(log: LogEntry, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == log.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_log = Log(message=log.message, user_id=log.user_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@app.get("/logs", response_model=List[LogResponse])
def read_logs(db: Session = Depends(get_db)):
    return db.query(Log).all()

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
