# 🧪 Especificação Técnica de Engenharia — Plano 11: Fase 3
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 11 — Polimento de UX: Unificação da Lousa, Selectbox Read-Only e Desativação Instantânea dos Downloads  
**Etapa:** Fase 3 — Suíte Automatizada de Testes de UX e Homologação Final  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Objetivo dos Testes
Garantir que as correções de usabilidade sejam verificadas por testes automatizados, assegurando:
1. A ausência de botões redundantes da lousa no chat e na coluna do canvas.
2. A presença exclusiva do botão flutuante persistente `canvas_toggle_fixed_btn`.
3. A presença das regras CSS e scripts JavaScript de proteção para o Selectbox (read-only) e Download instantâneo.
4. Passagem com sucesso de 100% dos testes do projeto (66+ testes unitários e QA visual).

---

## 2. Instruções Técnicas Passo a Passo para o Argon

Argon, crie o arquivo [`tests/test_plano11_ux.py`](file:///c:/Users/enric/Downloads/ProjetoConrad/tests/test_plano11_ux.py):

```python
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


if __name__ == "__main__":
    unittest.main()
```

---

## 3. Roteiro de Homologação para o Argon

1. **Executar a nova suíte de testes:**
   ```powershell
   python -m unittest tests/test_plano11_ux.py -v
   ```

2. **Executar toda a bateria de testes do sistema:**
   ```powershell
   python -m unittest discover -s tests -v
   ```

3. **Executar o QA visual automatizado:**
   ```powershell
   python tests/qa_visual_inspection.py
   ```

4. **Validação Manual no Navegador:**
   * Abrir o site no Streamlit.
   * Verificar que o topo do chat tem apenas "🎩 Diálogo com Conrad", sem botões extras.
   * Verificar que a lousa aberta tem apenas "📐 Quadro Negro do Conrad", sem botão "✕ Ocultar".
   * Clicar no botão flutuante no canto superior direito e verificar que abre e oculta a lousa perfeitamente.
   * Clicar no seletor de "Modelo de IA" na barra lateral e confirmar que não é possível digitar e que nenhum cursor pisca.
   * Enviar uma mensagem no chat e confirmar que os botões "📥 Baixar Resumo" e "📄 Baixar Caderno" ficam imediatamente escurecidos e desabilitados no mesmo instante em que se pressiona Enter.
