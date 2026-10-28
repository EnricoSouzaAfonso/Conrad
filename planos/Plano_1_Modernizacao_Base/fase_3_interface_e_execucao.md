# 📋 Especificação Técnica de Engenharia — Fase 3
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Etapa:** Fase 3 — Interface Interativa, Injeções DOM e Resiliência no Google Colab  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Modularizar a camada gráfica e o loop de eventos da Célula 4 do notebook em `src/conrad_ui.py`, garantindo total compatibilidade com o Google Colab moderno e versões recentes do `ipywidgets` (v8+). Implementar a injeção dinâmica do motor MathJax v3 (`tex-svg.js`), renderização avançada de blocos de código com Pygments (botões funcionais de Copiar e Baixar arquivo com tipagem MIME correta), comunicação bidirecional robusta (tecla Enter e auto-resize do campo de texto), monitoramento visual de tokens de contexto (1M tokens com alertas coloridos) e o protocolo de encerramento estrito pelo comando `"fim"`.

---

## 2. Arquivos Afetados
* **Criar:** `src/conrad_ui.py` (Módulo da interface gráfica, injeções DOM, CSS Dark Mode, eventos JS e renderizador de chat).
* **Modificar:** `Conrad.ipynb` (Transformar a Célula 4 em uma chamada limpa de inicialização da interface: `ui = ConradChatUI(engine=engine); ui.render()`).
* **Criar:** `src/assets/conrad_avatar.py` (Constante contendo a renderização vetorial SVG otimizada da Cartola vitoriana 🎩).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 1.6.2-dev — Refatoração da UI, Mapeamento Dinâmico e MathJax).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Avatar Vetorial da Cartola (`src/assets/conrad_avatar.py`)
Isolar o SVG da Cartola Vitoriana do Conrad em uma constante para reutilização no chat e em futuras telas:

```python
"""
Ativos visuais do Projeto Conrad.
"""

CONRAD_AVATAR_SVG = """
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
  <!-- Aba da Cartola -->
  <ellipse cx="12" cy="19" rx="10" ry="2.5" fill="#1a1a1a" stroke="#888" stroke-width="0.8"/>
  <!-- Corpo da Cartola -->
  <path d="M5.5 18 L6.5 6 C6.5 4.5 17.5 4.5 17.5 6 L18.5 18 Z" fill="#242424" stroke="#888" stroke-width="0.8"/>
  <!-- Topo da Cartola -->
  <ellipse cx="12" cy="6" rx="5.5" ry="1.5" fill="#333" stroke="#888" stroke-width="0.8"/>
  <!-- Faixa Branca Tradicional -->
  <path d="M5.8 15.5 C8 16.5 16 16.5 18.2 15.5 L18.4 17.5 C16 18.5 8 18.5 5.6 17.5 Z" fill="#f0f0f0"/>
</svg>
"""
```

---

### 3.2. Implementação da Camada de Interface (`src/conrad_ui.py`)
O Argon deve estruturar a classe `ConradChatUI` encapsulando todo o motor visual:

```python
import html
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import markdown2
from pygments.lexers import get_all_lexers
from IPython.display import display, HTML as IPyHTML, Javascript
import ipywidgets as widgets

from src.conrad_core import ConradEngine
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

class ConradChatUI:
    def __init__(self, engine: ConradEngine, max_input_length: int = 20000):
        self.engine = engine
        self.max_input_length = max_input_length
        self.lang_info_map = self._build_dynamic_language_map()
        self.conversa_encerrada = False
        self.total_token_limit = 1048576  # 1M tokens (Gemini 2.5)

        # Componentes visuais
        self.output_chat = widgets.Output(layout=widgets.Layout(height="450px", overflow_y="auto", border="1px solid #444", padding="10px"))
        self.textarea = widgets.Textarea(placeholder="Digite sua dúvida ou cole seu código aqui...", layout=widgets.Layout(width="80%", height="42px"))
        self.btn_send = widgets.Button(description="Enviar", button_style="primary", layout=widgets.Layout(width="18%"))
        self.token_display = widgets.HTML(value="<b>Tokens:</b> 0 / 1.048.576")
        self.status_display = widgets.HTML(value="")

        self._setup_events()

    def _build_dynamic_language_map(self) -> Dict[str, Dict[str, str]]:
        """Mapeia dinamicamente extensões e MIME types a partir dos lexers do Pygments."""
        lang_map = {}
        for lexer in get_all_lexers():
            if not lexer[2]:
                continue
            ext = lexer[2][0].lstrip("*.")
            mime = lexer[3][0] if lexer[3] else "text/plain"
            info = {"ext": ext, "mime": mime}
            for alias in lexer[1]:
                lang_map[alias.lower()] = info
        return lang_map

    def _get_css(self) -> str:
        return """
        <style>
          .conrad-chat-box { font-family: 'Segoe UI', sans-serif; background: #1e1e1e; color: #ddd; padding: 8px; border-radius: 8px; }
          .conrad-msg-user { background: #2b2b2b; border-left: 4px solid #4a90e2; padding: 8px; margin: 6px 0; border-radius: 4px; }
          .conrad-msg-conrad { background: #222222; border-left: 4px solid #e0e0e0; padding: 8px; margin: 6px 0; border-radius: 4px; }
          .codehilite { position: relative; background: #272822 !important; padding: 12px; padding-bottom: 40px; border-radius: 6px; margin: 8px 0; overflow-x: auto; }
          .codehilite pre { margin: 0; font-family: 'Consolas', monospace; color: #f8f8f2; }
          .conrad-code-actions { position: absolute; bottom: 6px; left: 8px; display: flex; gap: 6px; }
          .conrad-btn-action { background: #444; color: #fff; border: 1px solid #666; border-radius: 4px; padding: 2px 8px; font-size: 11px; cursor: pointer; }
          .conrad-btn-action:hover { background: #666; }
          .conrad-badge-lang { position: absolute; bottom: 6px; right: 8px; background: #333; color: #aaa; font-size: 10px; padding: 2px 6px; border-radius: 3px; }
        </style>
        """

    def _inject_mathjax_script(self):
        """Injeta a biblioteca MathJax v3 e dispara a renderização dinâmica."""
        display(IPyHTML("""
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" id="MathJax-script"></script>
        <script>
          if (window.MathJax) {
            MathJax.typesetPromise();
          }
        </script>
        """))

    def _trigger_mathjax_render(self):
        display(Javascript("if (window.MathJax) { MathJax.typesetPromise(); }"))

    def _process_response_markdown(self, markdown_text: str) -> str:
        """Converte Markdown para HTML, trata MathJax e injeta botões de código via BeautifulSoup."""
        # Processamento Markdown com extras
        raw_html = markdown2.markdown(
            markdown_text,
            extras=["fenced-code-blocks", "code-friendly", "tables", "smarty-pants"]
        )
        soup = BeautifulSoup(raw_html, "html.parser")

        # Injeção interativa nos blocos de código
        for idx, block in enumerate(soup.find_all("div", class_="codehilite")):
            block_id = f"conrad-code-{idx}"
            block["id"] = block_id
            
            # Detecta linguagem ou usa padrão
            classes = block.get("class", [])
            lang = "texto"
            for c in classes:
                if c != "codehilite":
                    lang = c.replace("language-", "")
                    break
            
            info = self.lang_info_map.get(lang.lower(), {"ext": "txt", "mime": "text/plain"})
            ext = info["ext"]

            # Contêiner de botões
            action_div = soup.new_tag("div", attrs={"class": "conrad-code-actions"})
            
            # Botão Copiar
            btn_copy = soup.new_tag(
                "button",
                attrs={
                    "class": "conrad-btn-action",
                    "onclick": f"navigator.clipboard.writeText(document.querySelector('#{block_id} pre').innerText); this.innerText='Copiado!';"
                }
            )
            btn_copy.string = "Copiar"
            action_div.append(btn_copy)

            # Botão Baixar
            btn_download = soup.new_tag(
                "button",
                attrs={
                    "class": "conrad-btn-action",
                    "onclick": f"""
                    const code = document.querySelector('#{block_id} pre').innerText;
                    const blob = new Blob([code], {{ type: '{info['mime']}' }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'conrad_codigo_{idx}.{ext}';
                    a.click();
                    URL.revokeObjectURL(url);
                    """
                }
            )
            btn_download.string = f"Baixar .{ext}"
            action_div.append(btn_download)

            # Badge da Linguagem
            badge_span = soup.new_tag("span", attrs={"class": "conrad-badge-lang"})
            badge_span.string = lang.upper()

            block.append(action_div)
            block.append(badge_span)

        return str(soup)

    def _setup_events(self):
        self.btn_send.on_click(self._on_send_clicked)
        # Tenta registrar callback para Enter no Google Colab
        try:
            from google.colab import output as colab_output
            colab_output.register_callback("conrad_submit_enter", self._on_user_submit)
        except Exception:
            pass

    def _on_send_clicked(self, _):
        text = self.textarea.value.strip()
        if text:
            self.textarea.value = ""
            self._on_user_submit(text)

    def _on_user_submit(self, prompt: str):
        if not prompt or self.conversa_encerrada:
            return

        # 1. Checagem do comando estrito de encerramento
        if prompt.strip().lower() == "fim":
            self.conversa_encerrada = True
            with self.output_chat:
                display(IPyHTML(f"<div class='conrad-msg-user'><b>Você:</b> {html.escape(prompt)}</div>"))
                display(IPyHTML(f"<div class='conrad-msg-conrad'>{CONRAD_AVATAR_SVG} <b>Conrad:</b> Foi um prazer enorme explorar o conhecimento com você! Até a próxima! 🎩</div>"))
            self.textarea.disabled = True
            self.btn_send.disabled = True
            self.status_display.value = "<b style='color: lightgreen;'>Sessão encerrada com sucesso.</b>"
            return

        # 2. Exibição da mensagem do usuário
        with self.output_chat:
            display(IPyHTML(f"<div class='conrad-msg-user'><b>Você:</b> {html.escape(prompt)}</div>"))

        # 3. Requisição ao motor do Conrad
        self.btn_send.disabled = True
        self.status_display.value = "<span style='color: #ffa500;'>Conrad está pensando... 💭</span>"

        try:
            resposta_texto = self.engine.send_message(prompt)
            html_processado = self._process_response_markdown(resposta_texto)
            with self.output_chat:
                display(IPyHTML(f"<div class='conrad-msg-conrad'>{CONRAD_AVATAR_SVG} <b>Conrad:</b><br>{html_processado}</div>"))
            self._trigger_mathjax_render()
            self._update_tokens()
        except Exception as e:
            with self.output_chat:
                display(IPyHTML(f"<div style='color: red;'>Erro: {html.escape(str(e))}</div>"))
        finally:
            self.btn_send.disabled = False
            self.status_display.value = ""

    def _update_tokens(self):
        total = self.engine.count_tokens()
        pct = (total / self.total_token_limit) * 100
        cor = "#aaa" if pct < 75 else "#ffa500" if pct < 90 else "#ff4444"
        self.token_display.value = f"<b>Tokens:</b> <span style='color:{cor};'>{total:,}</span> / {self.total_token_limit:,}"

    def render(self):
        """Renderiza a interface completa no notebook."""
        display(IPyHTML(self._get_css()))
        self._inject_mathjax_script()
        input_row = widgets.HBox([self.textarea, self.btn_send], layout=widgets.Layout(width="100%", align_items="center"))
        top_row = widgets.HBox([self.token_display, self.status_display], layout=widgets.Layout(justify_content="space-between", margin="0 0 6px 0"))
        container = widgets.VBox([top_row, self.output_chat, input_row], layout=widgets.Layout(max_width="900px", margin="auto"))
        display(container)
        self._inject_enter_listener()

    def _inject_enter_listener(self):
        """Injeta JavaScript para suporte a Enter (envio) e Shift+Enter (quebra de linha)."""
        display(Javascript("""
        const textarea = document.querySelector('.widget-textarea textarea');
        if (textarea) {
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (window.google && google.colab) {
                        google.colab.kernel.invokeFunction('conrad_submit_enter', [textarea.value], {});
                        textarea.value = '';
                    }
                }
            });
        }
        """))
```

---

### 3.3. Refatoração da Célula 4 de `Conrad.ipynb`
A Célula 4 passa a ter apenas 8 linhas:
```python
# -- Célula 4: Lançamento da Interface Interativa do Conrad --
from src.conrad_core import ConradEngine
from src.conrad_ui import ConradChatUI

engine = ConradEngine(api_key=GOOGLE_API_KEY, model_name=model_name_conrad)
ui = ConradChatUI(engine=engine)
ui.render()
```

---

## 4. Critério de Validação (Definition of Done)
1. **Redução Drástica da Célula 4:** A célula passa de 1.125 linhas para menos de 10 linhas no notebook, importando a classe limpa `ConradChatUI`.
2. **Execução Interativa no Colab:**
   - O chat carrega o contêiner visual com Dark Mode, avatar SVG da Cartola e contador de tokens.
   - O envio via botão "Enviar" e tecla `Enter` funciona sem erros no console.
3. **Renderização de Fórmulas:** Ao solicitar uma fórmula (ex: Teorema de Pitágoras ou Função de Onda de Schrödinger), as equações aparecem formatadas e nítidas em MathJax.
4. **Interatividade de Código:** Ao gerar um bloco em Python ou JavaScript, os botões flutuantes "Copiar" (copia para o clipboard) e "Baixar .py/.js" funcionam no navegador.
5. **Comando Fim:** Ao digitar `"fim"`, a caixa de texto desabilita e a despedida do Conrad é renderizada.
6. **Git Commit & Push:** Commitar com a mensagem padronizada:  
   `feat(ui): modularizacao do conrad_ui, suporte modernizado a ipywidgets e MathJax`
