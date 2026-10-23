"""
Módulo de Banco de Dados e Persistência do Projeto Conrad.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./conrad_data.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StudentUser(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("ChatSessionDB", back_populates="student")

class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"
    id = Column(String(50), primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    topic = Column(String(150), default="Geral")
    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("StudentUser", back_populates="sessions")
    messages = relationship("ChatMessageDB", back_populates="session", cascade="all, delete-orphan")

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.id"))
    sender = Column(String(20), nullable=False)  # 'user' ou 'conrad'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSessionDB", back_populates="messages")

def init_db():
    Base.metadata.create_all(bind=engine)
