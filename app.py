"""
Interface Web Autônoma do Conrad — Versão 2.3.0
Modos Pedagógicos Especializados, Pensamento Socrático Visível (CoT),
Split-View com Quadro Negro Interativo (Conrad Canvas), Mermaid Nativo, Gemini 3.8 Flash e Onboarding BYOK.
"""
import re
import html
import streamlit as st
from src.conrad_core import ConradEngine, DEFINITIVE_MODELS, DEFAULT_MODEL_NAME
from src.conrad_persona import get_missing_key_message, PEDAGOGICAL_MODES
from src.conrad_canvas import CanvasParser
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

st.set_page_config(
    page_title="Conrad — Tutor Socrático",
    page_icon="🎩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS para Dark Mode e Estilização do Quadro Negro (Split-View)
st.markdown(
    """
<style>
  .stApp { background-color: #121212; color: #e0e0e0; }
  .stChatMessage { border-radius: 8px; margin-bottom: 10px; }
  .canvas-container {
      background-color: #1a1a1a;
      border: 1px solid #333333;
      border-radius: 12px;
      padding: 18px;
      min-height: 520px;
  }
  .canvas-header {
      border-bottom: 2px solid #C59B27;
      padding-bottom: 8px;
      margin-bottom: 14px;
      font-weight: 600;
      color: #f5f5f5;
  }
  .token-badge {
      background-color: #2b2b2b;
      border: 1px solid #444;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 0.85rem;
      margin-bottom: 10px;
  }
</style>
""",
    unsafe_allow_html=True,
)

# Injeção de MathJax v3 e Mermaid.js CDN
st.markdown(
    """
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  if (window.mermaid) {
    mermaid.initialize({ startOnLoad: true, theme: 'dark' });
  }
</script>
""",
    unsafe_allow_html=True,
)

# Inicialização de Estados (Lazy — Zero Crash sem API Key)
if "engine" not in st.session_state:
    st.session_state.engine = ConradEngine()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_label" not in st.session_state:
    st.session_state.selected_model_label = list(DEFINITIVE_MODELS.keys())[0]
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "socratico"
if "active_artifact" not in st.session_state:
    st.session_state.active_artifact = None


def _render_cot_details(thought_text: str = ""):
    """Renderiza o bloco expansível de CoT com elementos nativos <details> e <summary>."""
    default_cot = (
        "Estratégia ativada: Diagnóstico socrático prévio. "
        "As pistas foram calibradas para provocar reflexão autônoma sem entregar a conclusão pronta."
    )
    safe_thought = html.escape(thought_text.strip()) if thought_text else default_cot
    st.markdown(
        f"""
<details style="background: #252525; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #C59B27;">
  <summary style="cursor: pointer; font-size: 12px; font-weight: 600; color: #ddd;">
    🧠 Raciocínio Pedagógico do Conrad
  </summary>
  <div style="font-size: 11px; color: #bbb; margin-top: 6px; line-height: 1.4;">
    {safe_thought}
  </div>
</details>
""",
        unsafe_allow_html=True,
    )


def _clean_code_or_mermaid_fence(content: str, expected_lang: str = "") -> str:
    """Remove cercas markdown redundantes caso o modelo as inclua dentro do artifact."""
    stripped = content.strip()
    pattern = rf"^```(?:{expected_lang}|\w+)?\s*\n(.*?)\n```$"
    match = re.match(pattern, stripped, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return stripped


def _format_study_summary_markdown(messages) -> str:
    """Exporta o histórico de estudos da sessão em formato Markdown estruturado."""
    lines = [
        "# 🎩 Resumo de Estudos — Sessão com o Conrad",
        f"**Modelo utilizado:** `{st.session_state.engine.model_name}`",
        f"**Modo Pedagógico:** `{PEDAGOGICAL_MODES[st.session_state.current_mode]['nome']}`",
        "",
        "---",
        "",
    ]
    if not messages:
        lines.append("*Nenhuma interação registrada nesta sessão ainda.*")
    else:
        for msg in messages:
            author = "🧑 Você" if msg["role"] == "user" else "🎩 Conrad"
            lines.append(f"### {author}\n\n{msg['content']}\n")
            art = msg.get("artifact")
            if art:
                lines.append(f"\n#### 📐 Quadro Negro: {art.title} ({art.type.upper()})\n\n{art.content}\n")
            lines.append("\n---\n")
    return "\n".join(lines)


# ==============================================================================
# --- SIDEBAR: MODOS PEDAGÓGICOS, MODELOS, ONBOARDING BYOK & UTILITÁRIOS ---
# ==============================================================================
with st.sidebar:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;'>{CONRAD_AVATAR_SVG} <h3 style='margin:0;'>Configurações</h3></div>",
        unsafe_allow_html=True,
    )
    st.caption("Personalize o modo didático, motor cognitivo e sua chave de acesso.")

    # 1. Seletor de Modo Pedagógico Especializado
    modo_selecionado = st.selectbox(
        "🎯 Modo Pedagógico",
        options=list(PEDAGOGICAL_MODES.keys()),
        index=list(PEDAGOGICAL_MODES.keys()).index(st.session_state.current_mode),
        format_func=lambda k: PEDAGOGICAL_MODES[k]["nome"],
        help="Altere o estilo de tutoria do Conrad conforme seu objetivo de estudo.",
    )
    if st.session_state.get("current_mode") != modo_selecionado:
        st.session_state.current_mode = modo_selecionado
        st.session_state.engine.set_pedagogical_mode(modo_selecionado)
        st.toast(f"Modo alterado para {PEDAGOGICAL_MODES[modo_selecionado]['nome']}!", icon="🎩")
    st.caption(f"ℹ️ {PEDAGOGICAL_MODES[modo_selecionado]['descricao']}")

    # 2. Seletor de Modelos Definitivos
    selected_label = st.selectbox(
        "🤖 Modelo de IA (Estáveis)",
        options=list(DEFINITIVE_MODELS.keys()),
        index=list(DEFINITIVE_MODELS.keys()).index(st.session_state.selected_model_label),
    )
    selected_model_id = DEFINITIVE_MODELS[selected_label]
    if selected_model_id != st.session_state.engine.model_name:
        st.session_state.selected_model_label = selected_label
        st.session_state.engine.set_model(selected_model_id)
        st.toast(f"Modelo alterado para {selected_model_id}!", icon="🎩")

    st.divider()

    # 3. Gerenciamento da API Key (BYOK)
    st.subheader("🔑 Chave da API Gemini (BYOK)")
    api_key_input = st.text_input(
        "Insira sua chave do Google AI Studio:",
        value=st.session_state.engine.api_key or "",
        type="password",
        placeholder="AIzaSy...",
    )

    if st.button("Salvar e Validar Chave", use_container_width=True, type="primary"):
        st.session_state.engine.set_api_key(api_key_input)
        with st.spinner("Validando chave junto à API do Google Gemini..."):
            if st.session_state.engine.validate_api_key():
                st.success("✅ Chave válida e ativa!")
            else:
                st.error("❌ Chave inválida. Verifique os caracteres.")

    if st.session_state.engine.api_key:
        st.caption("🟢 Status: Chave configurada na sessão.")
    else:
        st.caption("🟠 Status: Aguardando configuração de chave.")

    # 4. Tutorial Visual Expansível
    with st.expander("📘 Como Obter sua Chave Gratuita", expanded=not bool(st.session_state.engine.api_key)):
        st.markdown(
            """
            1. **Acesse o portal oficial:** Clique em [Google AI Studio](https://aistudio.google.com/app/apikey) e faça login com sua conta Google.
            2. **Gere a chave:** Clique no botão azul **"Create API Key"**.
            3. **Ative no Conrad:** Copie o código gerado (`AIza...`), cole no campo acima e clique em **"Salvar e Validar Chave"**.

            💡 *Dica: O Google oferece uma cota **100% gratuita** e generosa para estudantes, professores e uso pessoal!*
            """
        )

    st.divider()

    # 5. Métricas de Tokens e Utilitários de Sessão
    st.subheader("📊 Métricas & Utilitários")
    current_tokens = st.session_state.engine.count_tokens()
    st.markdown(
        f"<div class='token-badge'><b>Tokens na Sessão:</b> {current_tokens:,} / 1.048.576</div>",
        unsafe_allow_html=True,
    )

    if st.button("🔄 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_artifact = None
        if st.session_state.engine.api_key:
            st.session_state.engine._init_chat()
        st.rerun()

    st.download_button(
        label="📥 Baixar Resumo de Estudos",
        data=_format_study_summary_markdown(st.session_state.messages),
        file_name="resumo_estudos_conrad.md",
        mime="text/markdown",
        use_container_width=True,
    )


# ==============================================================================
# --- ÁREA PRINCIPAL: LAYOUT SPLIT-VIEW (CHAT À ESQUERDA | CANVAS À DIREITA) ---
# ==============================================================================
col_chat, col_canvas = st.columns([1.1, 0.9], gap="medium")

with col_chat:
    st.subheader("🎩 Diálogo com Conrad")
    st.caption(
        f"Modo: **{PEDAGOGICAL_MODES[st.session_state.current_mode]['nome']}** | Modelo: `{st.session_state.engine.model_name}`"
    )

    # Renderização das mensagens de chat (apenas diálogo limpo + CoT expansível em <details>)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🎩" if msg["role"] == "assistant" else None):
            if msg["role"] == "assistant" and msg.get("show_cot", False):
                _render_cot_details(msg.get("thought") or "")
            st.markdown(msg["content"])

    # Input do aluno
    if prompt := st.chat_input("Como posso ajudar seus estudos hoje? (digite 'fim' para encerrar)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🎩"):
            # Caso 1: Ausência de API Key — Resposta pré-programada graciosa (Zero Crash)
            if not st.session_state.engine.api_key:
                missing_msg = get_missing_key_message()
                st.markdown(missing_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": missing_msg, "show_cot": False}
                )
            # Caso 2: Comando estrito de encerramento
            elif prompt.strip() == "fim":
                farewell_msg = (
                    "Foi um prazer enorme explorar o conhecimento com você! "
                    "Lembre-se de revisar os conceitos que discutimos hoje para consolidar seu aprendizado. Até a próxima! 🎩"
                )
                st.markdown(farewell_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": farewell_msg, "show_cot": False}
                )
            # Caso 3: Streaming em tempo real + CoT Visível + Extração de Artifacts para o Quadro Negro
            else:
                cot_slot = st.empty()
                with cot_slot.container():
                    _render_cot_details()

                response_placeholder = st.empty()
                full_text = ""
                for chunk in st.session_state.engine.send_message_stream(prompt):
                    full_text += chunk
                    preview_text, _ = CanvasParser.parse_message(full_text)
                    response_placeholder.markdown(preview_text + "▌")

                text_without_thought, extracted_thought = CanvasParser.parse_thought(full_text)
                if extracted_thought:
                    with cot_slot.container():
                        _render_cot_details(extracted_thought)

                clean_chat_text, artifact = CanvasParser.parse_message(text_without_thought)
                response_placeholder.markdown(clean_chat_text)

                if artifact:
                    st.session_state.active_artifact = artifact

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": clean_chat_text,
                        "show_cot": True,
                        "thought": extracted_thought,
                        "artifact": artifact,
                    }
                )

with col_canvas:
    st.subheader("📐 Quadro Negro do Conrad")
    with st.container():
        st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
        if st.session_state.active_artifact:
            art = st.session_state.active_artifact
            st.markdown(
                f'<div class="canvas-header">📌 {art.title} ({art.type.upper()})</div>',
                unsafe_allow_html=True,
            )

            if art.type == "math":
                st.markdown(art.content)
            elif art.type == "code":
                st.code(_clean_code_or_mermaid_fence(art.content))
            elif art.type == "mermaid":
                # Renderiza diagrama Mermaid nativo
                clean_mermaid = _clean_code_or_mermaid_fence(art.content, "mermaid")
                st.markdown(f"```mermaid\n{clean_mermaid}\n```")
            else:
                st.markdown(art.content)
        else:
            st.info(
                "O Quadro Negro está limpo. Conforme o Conrad apresentar fórmulas, diagramas ou códigos, eles aparecerão aqui automaticamente!"
            )
        st.markdown("</div>", unsafe_allow_html=True)
