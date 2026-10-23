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
