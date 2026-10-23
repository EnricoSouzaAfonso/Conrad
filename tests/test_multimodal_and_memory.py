import unittest
from unittest.mock import MagicMock, patch
from src.database import (
    init_db,
    SessionLocal,
    StudentCognitiveProfile,
    get_or_create_profile,
    update_profile,
)
from src.conrad_core import ConradEngine
from src.conrad_canvas import CanvasParser


class TestMultimodalAndMemory(unittest.TestCase):
    def setUp(self):
        init_db()
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_persistencia_perfil_cognitivo(self):
        profile = get_or_create_profile(self.db)
        self.assertIsNotNone(profile)
        self.assertIsInstance(profile, StudentCognitiveProfile)
        self.assertTrue(len(profile.strengths) > 0)

        updated = update_profile(
            self.db,
            strengths="Equações do 1º grau, Cinemática",
            difficulties="Integrais por partes",
            learning_style="Visual e Socrático",
            pedagogical_notes="Excelente evolução na resolução de sistemas lineares.",
        )
        self.assertEqual(updated.strengths, "Equações do 1º grau, Cinemática")
        self.assertEqual(updated.difficulties, "Integrais por partes")
        self.assertEqual(updated.learning_style, "Visual e Socrático")

    @patch("src.conrad_core.genai.Client")
    def test_build_context_with_memory(self, mock_client_cls):
        engine = ConradEngine(api_key="TEST_KEY")
        ctx = engine.build_context_with_memory("Facilidade em álgebra; praticando derivadas.")
        self.assertEqual(
            ctx,
            "[HISTÓRICO PEDAGÓGICO DO ESTUDANTE]: Facilidade em álgebra; praticando derivadas.\n",
        )

    @patch("src.conrad_core.genai.Client")
    def test_upload_foto_caderno_equacao_multimodal(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        mock_client.chats.create.return_value = mock_chat

        simulated_response = MagicMock()
        simulated_response.text = (
            "Consegui ler perfeitamente a foto do seu caderno! Transcrevi a equação para o nosso Quadro Negro ao lado.\n"
            "Para isolarmos a incógnita $x$, o que você acha que devemos fazer com o número $5$ primeiro?\n\n"
            '<conrad_artifact type="math" title="Equação do Caderno">\n'
            "$$2x + 5 = 15$$\n"
            "Onde:\n"
            "- $x$: Incógnita que desejamos encontrar.\n"
            "</conrad_artifact>"
        )
        mock_chat.send_message.return_value = simulated_response

        engine = ConradEngine(api_key="TEST_KEY")
        fake_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        raw_reply = engine.send_message_multimodal(
            prompt="Me ajude a resolver a equação desta foto",
            media_bytes=fake_png_bytes,
            mime_type="image/png",
        )

        self.assertTrue(mock_chat.send_message.called)
        sent_contents = mock_chat.send_message.call_args[0][0]
        self.assertEqual(len(sent_contents), 2)

        clean_chat, artifact = CanvasParser.parse_message(raw_reply)
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.type, "math")
        self.assertIn("$$2x + 5 = 15$$", artifact.content)
        self.assertIn("o que você acha que devemos fazer com o número $5$ primeiro?", clean_chat)

    @patch("src.conrad_core.genai.Client")
    def test_upload_pdf_exercicio_fisica_multimodal(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        mock_client.chats.create.return_value = mock_chat

        simulated_response = MagicMock()
        simulated_response.text = (
            "Analisei o PDF da sua lista de Física! Extraí os dados do enunciado para o Quadro Negro. "
            "Quais grandezas físicas você identifica nesse movimento uniforme?\n\n"
            '<conrad_artifact type="summary" title="Dados do Problema (PDF)">\n'
            "- Velocidade inicial ($v_0$): $10\\text{ m/s}$\n"
            "- Intervalo de tempo ($\\Delta t$): $5\\text{ s}$\n"
            "</conrad_artifact>"
        )
        mock_chat.send_message.return_value = simulated_response

        engine = ConradEngine(api_key="TEST_KEY")
        fake_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj"
        raw_reply = engine.send_message_multimodal(
            prompt="Analise esta lista em PDF",
            media_bytes=fake_pdf_bytes,
            mime_type="application/pdf",
        )

        clean_chat, artifact = CanvasParser.parse_message(raw_reply)
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.type, "summary")
        self.assertIn("Quais grandezas físicas você identifica", clean_chat)


if __name__ == "__main__":
    unittest.main()
