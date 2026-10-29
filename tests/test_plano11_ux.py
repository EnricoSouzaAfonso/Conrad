"""
Suíte de Testes Automatizados - Plano 11
Validação de UX: Unificação de Botões da Lousa, Selectbox Read-Only e Desativação Instantânea de Downloads.
"""
import unittest
import os
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(ROOT_DIR, "app.py")


class TestPlano11UX(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(APP_PATH, "r", encoding="utf-8") as f:
            cls.app_src = f.read()

    def test_unicidade_botao_lousa_sem_duplicidade(self):
        """Valida que não existem botões duplicados de lousa no chat ou na coluna do canvas."""
        # Botões inline redundantes NÃO devem existir
        self.assertNotIn("canvas_toggle_inline_btn", self.app_src, "canvas_toggle_inline_btn não deve mais existir!")
        self.assertNotIn("canvas_close_col_btn", self.app_src, "canvas_close_col_btn não deve mais existir!")

        # O botão flutuante persistente DEVE existir e ser o único controle
        self.assertIn("canvas_toggle_fixed_btn", self.app_src, "canvas_toggle_fixed_btn deve existir como único botão flutuante!")

    def test_regras_css_selectbox_readonly(self):
        """Valida que o CSS remove o cursor de digitação do selectbox."""
        self.assertIn('div[data-testid="stSelectbox"] input', self.app_src)
        self.assertIn("caret-color: transparent", self.app_src)

    def test_desativacao_instantanea_download_css_e_js(self):
        """Valida a blindagem instantânea dos botões de download."""
        # Verifica seletores CSS com transição imediata (none)
        self.assertIn('div[data-testid="stDownloadButton"] button', self.app_src)
        self.assertIn("transition: none !important;", self.app_src)

        # Verifica injeção do script de travamento imediato no envio
        self.assertIn("lockDownloadButtonsImmediately", self.app_src)
        self.assertIn("enforceReadonlySelectboxes", self.app_src)

    def test_integridade_dos_modelos_vigentes(self):
        """Re-confirma que a fidelidade estrita de modelos continua 100% íntegra."""
        from src.conrad_core import DEFINITIVE_MODELS, DEFAULT_MODEL_NAME
        self.assertEqual(DEFAULT_MODEL_NAME, "gemini-3.8-flash")
        self.assertIn("gemini-3.8-flash", DEFINITIVE_MODELS.values())
        self.assertIn("gemini-3.6-flash", DEFINITIVE_MODELS.values())

    def test_selectbox_somente_selecao_sem_edicao_de_texto(self):
        """Todo st.selectbox deve ser somente-seleção: sem digitar, selecionar texto ou apagar."""
        total_selectboxes = len(re.findall(r"st\.selectbox\(", self.app_src))
        self.assertGreaterEqual(total_selectboxes, 2)
        # Desativação nativa do filtro por digitação em TODOS os selectboxes
        self.assertEqual(
            self.app_src.count("filter_mode=None"), total_selectboxes,
            "Todo st.selectbox deve declarar filter_mode=None (dropdown puro)!",
        )
        # Trava de edição no navegador: readOnly real + bloqueio de beforeinput/colar/recortar/arrastar
        self.assertIn("inp.readOnly = true", self.app_src)
        for evt in ("'beforeinput'", "'paste'", "'cut'", "'drop'"):
            self.assertIn(evt, self.app_src)
        self.assertIn("setSelectionRange(n, n)", self.app_src)

    def test_javascript_executa_via_st_html_e_nao_via_markdown_sanitizado(self):
        """st.markdown remove <script>/onload; o JS de UX precisa rodar via st.html(unsafe_allow_javascript=True)."""
        self.assertIn("unsafe_allow_javascript=True", self.app_src)
        self.assertNotIn("onload=", self.app_src, "Handlers inline onload são sanitizados pelo st.markdown e nunca executam!")
        html_block = self.app_src.split("\nst.html(\n", 1)[1].split("unsafe_allow_javascript=True", 1)[0]
        self.assertIn("enforceReadonlySelectboxes", html_block)
        self.assertIn("lockDownloadButtonsImmediately", html_block)
        self.assertIn("unlockDownloadButtons", html_block)


if __name__ == "__main__":
    unittest.main()
