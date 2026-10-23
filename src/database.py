"""
Módulo de Banco de Dados e Persistência do Projeto Conrad.
Inclui sessões de chat e Memória Pedagógica Persistente (StudentCognitiveProfile).
"""
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./conrad_data.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
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
    messages = relationship(
        "ChatMessageDB", back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.id"))
    sender = Column(String(20), nullable=False)  # 'user' ou 'conrad'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSessionDB", back_populates="messages")


class StudentCognitiveProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=True)
    strengths = Column(Text, default="")         # Ex: "Geometria plana, Lógica Booleana"
    difficulties = Column(Text, default="")      # Ex: "Regra da Cadeia em Derivadas, Recursão"
    learning_style = Column(String(50), default="Visual e Prático")  # Visual, Intuitivo, Formal
    pedagogical_notes = Column(Text, default="") # Observações cumulativas do tutor
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_or_create_profile(db, student_id: Optional[int] = None) -> StudentCognitiveProfile:
    """Busca ou inicializa o perfil cognitivo do estudante."""
    query = db.query(StudentCognitiveProfile)
    if student_id is not None:
        profile = query.filter(StudentCognitiveProfile.student_id == student_id).first()
    else:
        profile = query.first()

    if not profile:
        profile = StudentCognitiveProfile(
            student_id=student_id,
            strengths="Introdução à álgebra",
            difficulties="Identificação de variáveis em equações",
            learning_style="Analogias do cotidiano",
            pedagogical_notes="Aluno motivado; responde bem quando estimulado com exemplos do dia a dia.",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_profile(
    db,
    strengths: Optional[str] = None,
    difficulties: Optional[str] = None,
    learning_style: Optional[str] = None,
    pedagogical_notes: Optional[str] = None,
    student_id: Optional[int] = None,
) -> StudentCognitiveProfile:
    """Atualiza e persiste os atributos do perfil cognitivo do estudante."""
    profile = get_or_create_profile(db, student_id=student_id)
    if strengths is not None:
        profile.strengths = strengths
    if difficulties is not None:
        profile.difficulties = difficulties
    if learning_style is not None:
        profile.learning_style = learning_style
    if pedagogical_notes is not None:
        profile.pedagogical_notes = pedagogical_notes
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile


def init_db():
    Base.metadata.create_all(bind=engine)
