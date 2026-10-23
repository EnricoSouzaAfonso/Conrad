import json
import unittest
from unittest.mock import MagicMock, patch
from src.conrad_core import ConradEngine
from src.conrad_ui import ConradChatUI
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG


class TestConradUI(unittest.TestCase):
    @patch("src.conrad_core.genai.Client")
    def setUp(self, mock_client_cls):
        self.mock_client = mock_client_cls.return_value
        self.mock_chat = MagicMock()
        self.mock_client.chats.create.return_value = self.mock_chat
        self.engine = ConradEngine(api_key="TEST_KEY")
        self.ui = ConradChatUI(engine=self.engine)

    def test_avatar_svg_presente(self):
        self.assertIn("<svg", CONRAD_AVATAR_SVG)
        self.assertIn("Aba da Cartola", CONRAD_AVATAR_SVG)

    def test_mapeamento_dinamico_pygments(self):
        self.assertIn("python", self.ui.lang_info_map)
        self.assertEqual(self.ui.lang_info_map["python"]["ext"], "py")
        self.assertIn("javascript", self.ui.lang_info_map)
        self.assertEqual(self.ui.lang_info_map["javascript"]["ext"], "js")

    def test_processamento_markdown_e_botoes_codigo(self):
        md = "Veja este exemplo:\n```python\nprint('Olá, Conrad!')\n```"
        html_out = self.ui._process_response_markdown(md)
        self.assertIn("conrad-code-0", html_out)
        self.assertIn("Copiar", html_out)
        self.assertIn("Baixar .py", html_out)
        self.assertIn("PYTHON", html_out)

    def test_comando_fim_encerra_sessao(self):
        self.ui._on_user_submit("fim")
        self.assertTrue(self.ui.conversa_encerrada)
        self.assertTrue(self.ui.textarea.disabled)
        self.assertTrue(self.ui.btn_send.disabled)
        self.assertIn("Sessão encerrada com sucesso", self.ui.status_display.value)

    def test_envio_mensagem_e_atualizacao_tokens(self):
        mock_resp = MagicMock()
        mock_resp.text = "O Teorema de Pitágoras afirma:\n$$a^2 + b^2 = c^2$$"
        self.mock_chat.send_message.return_value = mock_resp
        self.engine.count_tokens = MagicMock(return_value=128)

        self.ui._on_user_submit("Explique o Teorema de Pitágoras")
        self.assertIn("128", self.ui.token_display.value)
        self.assertFalse(self.ui.btn_send.disabled)

    def test_reducao_celula_4_notebook(self):
        with open("Conrad.ipynb", "r", encoding="utf-8") as f:
            nb = json.load(f)
        c4_lines = nb["cells"][4]["source"]
        self.assertLess(len(c4_lines), 10)
        c4_text = "".join(c4_lines)
        self.assertIn("ConradChatUI", c4_text)
        self.assertIn("ui.render()", c4_text)


if __name__ == "__main__":
    unittest.main()
