import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.api import app, active_engines
from src.database import init_db, SessionLocal, ChatSessionDB, ChatMessageDB, StudentUser


class TestApiAndDatabase(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)
        active_engines.clear()

    def test_openapi_docs_disponivel(self):
        res_docs = self.client.get("/docs")
        self.assertEqual(res_docs.status_code, 200)
        self.assertIn("Swagger UI", res_docs.text)

        res_schema = self.client.get("/openapi.json")
        self.assertEqual(res_schema.status_code, 200)
        self.assertEqual(res_schema.json()["info"]["version"], "2.0.0")

    @patch("src.api.ConradEngine")
    def test_criacao_sessao_e_persistencia_sqlite(self, mock_engine_cls):
        res = self.client.post("/api/sessions?topic=FisicaQuantica")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        session_id = data["session_id"]
        self.assertEqual(data["topic"], "FisicaQuantica")
        self.assertTrue(os.path.exists("conrad_data.db"))

        db = SessionLocal()
        try:
            sess = db.query(ChatSessionDB).filter_by(id=session_id).first()
            self.assertIsNotNone(sess)
            self.assertEqual(sess.topic, "FisicaQuantica")
        finally:
            db.close()

    @patch("src.api.ConradEngine")
    def test_streaming_sse_e_persistencia_mensagens(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.send_message_stream.return_value = iter(["Olá! ", "Como ", "posso ajudar? 🎩"])
        mock_engine_cls.return_value = mock_engine

        res_sess = self.client.post("/api/sessions?topic=Programacao")
        session_id = res_sess.json()["session_id"]

        res_stream = self.client.post(
            "/api/chat/stream",
            json={"session_id": session_id, "message": "Me explique listas em Python"},
        )
        self.assertEqual(res_stream.status_code, 200)
        self.assertIn("posso ajudar?", res_stream.text)

        db = SessionLocal()
        try:
            msgs = db.query(ChatMessageDB).filter_by(session_id=session_id).order_by(ChatMessageDB.id).all()
            self.assertEqual(len(msgs), 2)
            self.assertEqual(msgs[0].sender, "user")
            self.assertEqual(msgs[0].content, "Me explique listas em Python")
            self.assertEqual(msgs[1].sender, "conrad")
            self.assertEqual(msgs[1].content, "Olá! Como posso ajudar? 🎩")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
