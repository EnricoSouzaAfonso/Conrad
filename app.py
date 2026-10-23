"""
Interface Web Autônoma do Conrad — Versão 2.1.0
Upgrade Gemini 3.8 Flash, Seletor de Modelos Definitivos, Onboarding BYOK e Recursos Pedagógicos.
"""
import streamlit as st
from src.conrad_core import ConradEngine, DEFINITIVE_MODELS, DEFAULT_MODEL_NAME
from src.conrad_persona import get_missing_key_message
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

st.set_page_config(
    page_title="Conrad — Assistente Cognitivo & Pedagógico",
    page_icon="🎩",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CSS e Identidade Visual Dark Elegante
st.markdown(
    """
<style>
  .stApp { background-color: #1e1e1e; color: #f0f0f0; }
  .chat-header { text-align: center; margin-bottom: 20px; }
  .stChatMessage { border-radius: 8px; margin-bottom: 10px; }
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

# Inicialização de Estado (Lazy — Zero Crash sem API Key)
if "engine" not in st.session_state:
    st.session_state.engine = ConradEngine()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_label" not in st.session_state:
    st.session_state.selected_model_label = list(DEFINITIVE_MODELS.keys())[0]


def _format_study_summary_markdown(messages) -> str:
    """Exporta o histórico de estudos da sessão em formato Markdown estruturado."""
    lines = [
        "# 🎩 Resumo de Estudos — Sessão com o Conrad",
        f"**Modelo utilizado:** `{st.session_state.engine.model_name}`",
        "",
        "---",
        "",
    ]
    if not messages:
        lines.append("*Nenhuma interação registrada nesta sessão ainda.*")
    else:
        for msg in messages:
            author = "🧑 Você" if msg["role"] == "user" else "🎩 Conrad"
            lines.append(f"### {author}\n\n{msg['content']}\n\n---\n")
    return "\n".join(lines)


# ==============================================================================
# --- SIDEBAR: SELETOR DE MODELOS, ONBOARDING BYOK & UTILITÁRIOS ---
# ==============================================================================
with st.sidebar:
    st.markdown(f"<div style='display:flex;align-items:center;gap:8px;'>{CONRAD_AVATAR_SVG} <h3 style='margin:0;'>Configurações</h3></div>", unsafe_allow_html=True)
    st.caption("Personalize o motor cognitivo e sua chave de acesso.")

    # 1. Seletor de Modelos Definitivos
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

    # 2. Gerenciamento da API Key (BYOK)
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

    # 3. Tutorial Visual Expansível
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

    # 4. Métricas de Tokens e Utilitários de Sessão
    st.subheader("📊 Métricas & Utilitários")
    current_tokens = st.session_state.engine.count_tokens()
    st.markdown(
        f"<div class='token-badge'><b>Tokens na Sessão:</b> {current_tokens:,} / 1.048.576</div>",
        unsafe_allow_html=True,
    )

    if st.button("🔄 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
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
# --- ÁREA PRINCIPAL DO CHAT ---
# ==============================================================================
st.title("🎩 Conrad — Assistente Pedagógico")
st.caption(f"Tutor Socrático & Construtivista | Modelo ativo: `{st.session_state.engine.model_name}`")

# Exibição do histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🎩" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Como posso ajudar seus estudos hoje? (digite 'fim' para encerrar)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎩"):
        # Caso 1: Ausência de API Key — Resposta pré-programada graciosa (Zero Crash)
        if not st.session_state.engine.api_key:
            missing_msg = get_missing_key_message()
            st.markdown(missing_msg)
            st.session_state.messages.append({"role": "assistant", "content": missing_msg})
        # Caso 2: Comando estrito de encerramento
        elif prompt.strip() == "fim":
            farewell_msg = "Foi um prazer enorme explorar o conhecimento com você! Lembre-se de revisar os conceitos que discutimos hoje para consolidar seu aprendizado. Até a próxima! 🎩"
            st.markdown(farewell_msg)
            st.session_state.messages.append({"role": "assistant", "content": farewell_msg})
        # Caso 3: Streaming em tempo real via ConradEngine
        else:
            response_placeholder = st.empty()
            full_text = ""
            for chunk in st.session_state.engine.send_message_stream(prompt):
                full_text += chunk
                response_placeholder.markdown(full_text + "▌")
            response_placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
