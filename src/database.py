"""
Módulo de Banco de Dados e Persistência do Projeto Conrad.
Inclui sessões de chat, Memória Pedagógica Multidisciplinar (StudentCognitiveProfile)
e Gems Pedagógicas Customizáveis (PedagogicalGemDB).
"""
import os
import re
import unicodedata
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./conrad_data.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Valores padrão neutros e multidisciplinares para o perfil cognitivo escolar
DEFAULT_STRENGTHS = "Curioso e aberto a novos conhecimentos"
DEFAULT_DIFFICULTIES = "Diagnóstico conceitual em andamento"
DEFAULT_LEARNING_STYLE = "Adaptativo (Analogias e exemplos práticos)"
DEFAULT_PEDAGOGICAL_NOTES = (
    "Estudante iniciando jornada multidisciplinar. "
    "Adapte a linguagem ao ritmo e aos interesses do aluno."
)


def _utcnow():
    return datetime.now(timezone.utc)


class StudentUser(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True)
    created_at = Column(DateTime, default=_utcnow)
    sessions = relationship("ChatSessionDB", back_populates="student")


class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"
    id = Column(String(50), primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    topic = Column(String(150), default="Geral")
    created_at = Column(DateTime, default=_utcnow)
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
    timestamp = Column(DateTime, default=_utcnow)
    session = relationship("ChatSessionDB", back_populates="messages")


class StudentCognitiveProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=True)
    strengths = Column(Text, default=DEFAULT_STRENGTHS)
    difficulties = Column(Text, default=DEFAULT_DIFFICULTIES)
    learning_style = Column(String(100), default=DEFAULT_LEARNING_STYLE)
    pedagogical_notes = Column(Text, default=DEFAULT_PEDAGOGICAL_NOTES)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class PedagogicalGemDB(Base):
    __tablename__ = "pedagogical_gems"
    id = Column(Integer, primary_key=True, index=True)
    gem_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    system_directive = Column(Text, nullable=False)
    is_builtin = Column(Integer, default=0)  # 1 para as 4 oficiais (protegidas), 0 para customizadas
    created_at = Column(DateTime, default=_utcnow)


def get_or_create_profile(db, student_id: Optional[int] = None) -> StudentCognitiveProfile:
    """Busca ou inicializa o perfil cognitivo neutro e multidisciplinar do estudante."""
    query = db.query(StudentCognitiveProfile)
    if student_id is not None:
        profile = query.filter(StudentCognitiveProfile.student_id == student_id).first()
    else:
        profile = query.first()

    if not profile:
        profile = StudentCognitiveProfile(
            student_id=student_id,
            strengths=DEFAULT_STRENGTHS,
            difficulties=DEFAULT_DIFFICULTIES,
            learning_style=DEFAULT_LEARNING_STYLE,
            pedagogical_notes=DEFAULT_PEDAGOGICAL_NOTES,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    else:
        # Migração transparente: se o banco local ainda possuir o mock antigo de álgebra, atualiza suavemente
        if "Introdução à álgebra" in (profile.strengths or ""):
            profile.strengths = DEFAULT_STRENGTHS
            if "Identificação de variáveis" in (profile.difficulties or ""):
                profile.difficulties = DEFAULT_DIFFICULTIES
            if "Analogias do cotidiano" in (profile.learning_style or ""):
                profile.learning_style = DEFAULT_LEARNING_STYLE
            if "Aluno motivado" in (profile.pedagogical_notes or ""):
                profile.pedagogical_notes = DEFAULT_PEDAGOGICAL_NOTES
            db.commit()
            db.refresh(profile)
    return profile


def reset_profile_to_default(db, student_id: Optional[int] = None) -> StudentCognitiveProfile:
    """Restaura o perfil cognitivo para os padrões neutros e multidisciplinares."""
    profile = get_or_create_profile(db, student_id=student_id)
    profile.strengths = DEFAULT_STRENGTHS
    profile.difficulties = DEFAULT_DIFFICULTIES
    profile.learning_style = DEFAULT_LEARNING_STYLE
    profile.pedagogical_notes = DEFAULT_PEDAGOGICAL_NOTES
    profile.updated_at = _utcnow()
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
    profile.updated_at = _utcnow()
    db.commit()
    db.refresh(profile)
    return profile


def seed_default_gems(db):
    """Garante a existência das 4 Gems nativas do Conrad."""
    from src.conrad_pedagogy import PEDAGOGICAL_MODES

    for key, data in PEDAGOGICAL_MODES.items():
        existing = db.query(PedagogicalGemDB).filter(PedagogicalGemDB.gem_id == key).first()
        if not existing:
            gem = PedagogicalGemDB(
                gem_id=key,
                name=data["nome"],
                description=data["descricao"],
                system_directive=data["diretriz"],
                is_builtin=1,
            )
            db.add(gem)
    db.commit()


def get_all_gems(db) -> List[PedagogicalGemDB]:
    """Retorna todas as Gems ordenando oficiais primeiro, depois por nome."""
    gems = (
        db.query(PedagogicalGemDB)
        .order_by(PedagogicalGemDB.is_builtin.desc(), PedagogicalGemDB.id.asc())
        .all()
    )
    if not gems:
        seed_default_gems(db)
        gems = (
            db.query(PedagogicalGemDB)
            .order_by(PedagogicalGemDB.is_builtin.desc(), PedagogicalGemDB.id.asc())
            .all()
        )
    return gems


def get_gem_by_id(db, gem_id: str) -> Optional[PedagogicalGemDB]:
    return db.query(PedagogicalGemDB).filter(PedagogicalGemDB.gem_id == gem_id).first()


def create_custom_gem(db, name: str, description: str, system_directive: str) -> PedagogicalGemDB:
    """Cria uma nova Gem pedagógica customizada no banco SQLite."""
    normalized = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", normalized.lower()).strip("_")[:40] or "gem"
    gem_id = f"custom_{slug}_{int(_utcnow().timestamp() * 1000)}"
    gem = PedagogicalGemDB(
        gem_id=gem_id,
        name=(name or "Nova Gem").strip(),
        description=(description or "Gem personalizada").strip(),
        system_directive=(system_directive or "").strip(),
        is_builtin=0,
    )
    db.add(gem)
    db.commit()
    db.refresh(gem)
    return gem


def update_custom_gem(
    db, gem_id: str, name: str, description: str, system_directive: str
) -> Optional[PedagogicalGemDB]:
    """Atualiza uma Gem customizada existente (protege built-ins contra alteração)."""
    gem = get_gem_by_id(db, gem_id)
    if not gem or gem.is_builtin == 1:
        return None
    gem.name = name.strip()
    gem.description = description.strip()
    gem.system_directive = system_directive.strip()
    db.commit()
    db.refresh(gem)
    return gem


def delete_custom_gem(db, gem_id: str) -> bool:
    """Exclui uma Gem customizada (protege built-ins contra exclusão)."""
    gem = get_gem_by_id(db, gem_id)
    if not gem or gem.is_builtin == 1:
        return False
    db.delete(gem)
    db.commit()
    return True


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_gems(db)
    finally:
        db.close()
