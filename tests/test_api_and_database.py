import os
import time
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.api import app, active_engines
from src.conrad_core import ConradEngine
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

    @patch("src.conrad_core.genai.Client")
    def test_validacao_chave_canonica_models_list_valida(self, mock_client_cls):
        """Garante que validate_api_key() usa client.models.list() sem gastar tokens e aprova chaves válidas."""
        mock_client = mock_client_cls.return_value
        mock_model = MagicMock()
        mock_model.name = "models/gemini-2.5-flash"
        mock_client.models.list.return_value = iter([mock_model])

        engine = ConradEngine(api_key="AIzaSyValidKeyExample123456")
        t0 = time.perf_counter()
        is_valid = engine.validate_api_key()
        elapsed = time.perf_counter() - t0

        self.assertTrue(is_valid)
        self.assertLess(elapsed, 0.5)
        mock_client.models.list.assert_called()
        mock_client.models.generate_content.assert_not_called()

    @patch("src.conrad_core.genai.Client")
    def test_rejeicao_chave_corrompida_api_key_invalid(self, mock_client_cls):
        """Garante que chaves falsas/corrompidas (API_KEY_INVALID) ou vazias são rejeitadas."""
        mock_client = mock_client_cls.return_value
        mock_client.models.list.side_effect = Exception(
            "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid.', 'reason': 'API_KEY_INVALID'}}"
        )

        engine = ConradEngine(api_key="AIzaSyFakeKey123456789")
        self.assertFalse(engine.validate_api_key())

        with patch.object(ConradEngine, "_resolve_api_key", return_value=None):
            empty_engine = ConradEngine(api_key="   ")
            self.assertFalse(empty_engine.validate_api_key())

    @patch("src.conrad_core.genai.Client")
    def test_streaming_baixa_latencia_ttft(self, mock_client_cls):
        """Verifica que send_message_stream entrega os chunks diretamente com baixa latência."""
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        chunk1 = MagicMock(text="Vamos ")
        chunk2 = MagicMock(text="pensar juntos! 🎩")
        mock_chat.send_message_stream.return_value = iter([chunk1, chunk2])
        mock_client.chats.create.return_value = mock_chat

        engine = ConradEngine(api_key="AIzaSyValidKeyExample123456")
        t0 = time.perf_counter()
        chunks = list(engine.send_message_stream("Explique o Teorema de Pitágoras"))
        elapsed = time.perf_counter() - t0

        self.assertEqual("".join(chunks), "Vamos pensar juntos! 🎩")
        self.assertLess(elapsed, 0.5)


if __name__ == "__main__":
    unittest.main()
