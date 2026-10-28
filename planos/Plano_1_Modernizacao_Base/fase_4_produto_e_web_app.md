# 📋 Especificação Técnica de Engenharia — Fase 4
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Etapa:** Fase 4 — Preparação para Produto Comercial, API REST/Streaming e Aplicação Web Autônoma  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Transformar o Conrad de um protótipo dependente do Google Colab em uma **aplicação web autônoma, escalável e comercializável** para escolas, professores e estudantes. Construir uma API backend em FastAPI com suporte a streaming de respostas em tempo real (`send_message_stream`), implementar persistência de sessões e perfis de aprendizagem em banco de dados relacional (SQLAlchemy/SQLite/PostgreSQL) e disponibilizar uma interface web moderna e responsiva pronta para deploy em produção (nuvem / Docker).

---

## 2. Arquivos Afetados
* **Criar:** `src/database.py` (Camada ORM com tabelas de usuários, sessões, mensagens e preferências de estudo).
* **Criar:** `src/api.py` (Serviço backend FastAPI com endpoints REST e streaming via Server-Sent Events).
* **Criar:** `app.py` (Frontend autônomo completo e moderno para demonstração e uso comercial direto fora do Colab).
* **Criar:** `Dockerfile` e `docker-compose.yml` (Empacotamento completo do serviço para infraestrutura em nuvem).
* **Modificar:** `requirements.txt` (Adicionar dependências de produção: `fastapi`, `uvicorn`, `sqlalchemy`, `streamlit`, `sse-starlette`).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 2.0.0 — Transição para Produto Web Autônomo e API Comercial).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Expansão das Dependências de Produção (`requirements.txt`)
Atualizar o arquivo `requirements.txt` com as bibliotecas necessárias para a aplicação web independente:
```text
google-genai>=1.0.0
markdown2>=2.4.10
beautifulsoup4>=4.12.0
lxml>=5.0.0
Pygments>=2.17.0
fastapi>=0.110.0
uvicorn>=0.28.0
sqlalchemy>=2.0.0
streamlit>=1.32.0
sse-starlette>=2.0.0
pydantic>=2.6.0
```

---

### 3.2. Camada de Persistência e Banco de Dados (`src/database.py`)
Modelar a estrutura de persistência para armazenar as jornadas de aprendizado dos alunos:

```python
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
```

---

### 3.3. Streaming Assíncrono no Motor (`src/conrad_core.py`)
Adicionar suporte a streaming no `ConradEngine` para alimentar a aplicação web em tempo real:

```python
    def send_message_stream(self, prompt: str):
        """Envia mensagem e gera chunks de texto em streaming (tempo real)."""
        if not self.chat:
            raise RuntimeError("Sessão de chat não inicializada.")
        
        try:
            response_stream = self.chat.send_message_stream(prompt)
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"(Erro no streaming: {str(e)})"
```

---

### 3.4. Backend Comercial com FastAPI (`src/api.py`)
Construir a API REST para consumo por escolas, plataformas LMS ou frontends modernos:

```python
import uuid
from typing import Generator
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from src.database import init_db, SessionLocal, ChatSessionDB, ChatMessageDB
from src.conrad_core import ConradEngine

app = FastAPI(title="Conrad API", version="2.0.0", description="API Comercial do Assistente Socrático Conrad")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
# Cache em memória para instâncias ativas de chat
active_engines = {}

class PromptRequest(BaseModel):
    session_id: str
    message: str

@app.post("/api/sessions")
def create_session(topic: str = "Geral"):
    session_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        new_session = ChatSessionDB(id=session_id, topic=topic)
        db.add(new_session)
        db.commit()
    finally:
        db.close()
    
    active_engines[session_id] = ConradEngine()
    return {"session_id": session_id, "topic": topic}

@app.post("/api/chat/stream")
def chat_stream(req: PromptRequest):
    session_id = req.session_id
    if session_id not in active_engines:
        active_engines[session_id] = ConradEngine()

    engine_instance = active_engines[session_id]

    def event_generator() -> Generator[str, None, None]:
        # Salva pergunta do usuário
        db = SessionLocal()
        try:
            db.add(ChatMessageDB(session_id=session_id, sender="user", content=req.message))
            db.commit()
        finally:
            db.close()

        full_response = []
        for token in engine_instance.send_message_stream(req.message):
            full_response.append(token)
            yield token

        # Salva resposta completa do Conrad
        db = SessionLocal()
        try:
            db.add(ChatMessageDB(session_id=session_id, sender="conrad", content="".join(full_response)))
            db.commit()
        finally:
            db.close()

    return EventSourceResponse(event_generator())
```

---

### 3.5. Frontend Autônomo com Streamlit (`app.py`)
Criar uma interface web autônoma e polida para demonstrações comerciais:

```python
"""
Interface Web Autônoma do Conrad (Demonstração Comercial & Uso Prático).
"""
import streamlit as st
from src.conrad_core import ConradEngine
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

st.set_page_config(page_title="Conrad — Tutor Educativo", page_icon="🎩", layout="centered")

# CSS e Identidade Visual Dark Elegante
st.markdown("""
<style>
  .stApp { background-color: #1e1e1e; color: #f0f0f0; }
  .chat-header { text-align: center; margin-bottom: 20px; }
  .stChatMessage { border-radius: 8px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# Injeção de MathJax CDN
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
""", unsafe_allow_html=True)

st.title("🎩 Conrad — Assistente Pedagógico")
st.caption("Tutor Socrático & Construtivista de Alta Performance")

if "engine" not in st.session_state:
    st.session_state.engine = ConradEngine()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibição do histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🎩" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Como posso ajudar seus estudos hoje? (digite 'fim' para encerrar)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎩"):
        response_placeholder = st.empty()
        full_text = ""
        for chunk in st.session_state.engine.send_message_stream(prompt):
            full_text += chunk
            response_placeholder.markdown(full_text + "▌")
        response_placeholder.markdown(full_text)

    st.session_state.messages.append({"role": "assistant", "content": full_text})
```

---

### 3.6. Containerização para Nuvem (`Dockerfile` & `docker-compose.yml`)
Criar a infraestrutura necessária para subir o Conrad em qualquer serviço de nuvem (Render, AWS, Railway, DigitalOcean):

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501 8000

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 4. Critério de Validação (Definition of Done)
1. **Validação do Backend API:**
   - O comando `uvicorn src.api:app --port 8000` inicia com sucesso.
   - O acesso a `http://localhost:8000/docs` exibe a documentação OpenAPI/Swagger funcional.
2. **Streaming em Tempo Real:** O endpoint `/api/chat/stream` entrega tokens progressivos sem travamentos.
3. **Execução Web Autônoma:**
   - O comando `streamlit run app.py` abre a interface web no navegador.
   - O envio de mensagens aciona o streaming, renderiza fórmulas em MathJax e preserva a persona socrática.
4. **Persistência de Dados:** O arquivo de banco `conrad_data.db` é criado automaticamente e registra as interações.
5. **Build de Container:** O comando `docker build -t conrad:2.0.0 .` compila a imagem sem erros de dependência.
6. **Git Commit & Push:** Commitar com a mensagem padronizada:  
   `feat(product): criacao da API FastAPI, streaming, persistencia e app web autonomo v2.0.0`
