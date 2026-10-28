"""
Suíte de Testes Automatizados — Plano 10
Validação de Fidelidade Estrita de Modelos (Zero Mascaramento & Zero Fallback Oculto).
"""
import unittest
from unittest.mock import MagicMock, patch
from src.conrad_core import ConradEngine, DEFINITIVE_MODELS, DEFAULT_MODEL_NAME


class TestFidelidadeModelos(unittest.TestCase):

    def test_catalogo_oficial_sem_desvios(self):
        """Valida que o catálogo contém apenas modelos vigentes e sem chaves obsoletas."""
        import src.conrad_core as core_mod
        self.assertFalse(hasattr(core_mod, "RUNTIME_MODEL_MAP"), "RUNTIME_MODEL_MAP não deve existir!")
        self.assertFalse(hasattr(core_mod, "FALLBACK_MODEL_NAME"), "FALLBACK_MODEL_NAME não deve existir!")
        self.assertIn("gemini-3.8-flash", DEFINITIVE_MODELS.values())
        self.assertIn("gemini-3.6-flash", DEFINITIVE_MODELS.values())
        self.assertIn("gemini-3.5-flash", DEFINITIVE_MODELS.values())

    @patch("src.conrad_core.genai.Client")
    def test_chats_create_usa_rigorosamente_modelo_configurado(self, mock_client_cls):
        """Valida que ao trocar de modelo, o chat é instanciado estritamente com o model_id correto."""
        mock_client = mock_client_cls.return_value
        engine = ConradEngine(api_key="AIzaSy_FAKE_TEST_KEY", model_name="gemini-3.8-flash")

        # 1. Verifica inicialização padrão com 3.8
        self.assertEqual(engine.model_name, "gemini-3.8-flash")
        self.assertEqual(engine._active_runtime_model, "gemini-3.8-flash")
        mock_client.chats.create.assert_called()
        last_call_kwargs = mock_client.chats.create.call_args[1]
        self.assertEqual(last_call_kwargs["model"], "gemini-3.8-flash")

        # 2. Testa cada modelo do catálogo
        for label, model_id in DEFINITIVE_MODELS.items():
            engine.set_model(model_id)
            self.assertEqual(engine.model_name, model_id)
            self.assertEqual(engine._active_runtime_model, model_id)
            call_kwargs = mock_client.chats.create.call_args[1]
            self.assertEqual(call_kwargs["model"], model_id, f"Falha na vinculação estrita para {label}")

    @patch("src.conrad_core.time.sleep")
    @patch("src.conrad_core.genai.Client")
    def test_send_message_stream_nao_troca_modelo_em_503(self, mock_client_cls, _mock_sleep):
        """Valida que um erro 503 não altera engine.model_name para outro modelo."""
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        # Simula erro de 503
        mock_chat.send_message_stream.side_effect = Exception("503 UNAVAILABLE: High demand")
        mock_client.chats.create.return_value = mock_chat

        engine = ConradEngine(api_key="AIzaSy_FAKE_KEY", model_name="gemini-3.8-flash")
        chunks = list(engine.send_message_stream("Teste de pergunta"))

        # O modelo deve continuar sendo 3.8 flash
        self.assertEqual(engine.model_name, "gemini-3.8-flash")
        self.assertEqual(engine._active_runtime_model, "gemini-3.8-flash")
        # Deve retornar mensagem amigável sem quebrar o app
        self.assertTrue(any("Alta Demanda" in c or "503" in c for c in chunks))


if __name__ == "__main__":
    unittest.main()
