"""
Interface Web Autônoma do Conrad — Versão 2.6.2 (Chaos & Edge-Case Hardened)
Engenharia de QA, Validação Canônica de API Key (Zero Falso-Positivo),
Streaming Throttled (40ms / 25fps), Encapsulamento Estrito do Quadro Negro (st.container(border=True)),
Layout Sticky Bottom, Blindagem Zero-Crash (429/Timeout) e Reparo de LaTeX/Mermaid.
"""
import os
import re
import time
import html
import streamlit as st
from src.conrad_core import ConradEngine, DEFINITIVE_MODELS, DEFAULT_MODEL_NAME, MSG_EMPTY_PROMPT
from src.conrad_persona import get_missing_key_message, PEDAGOGICAL_MODES
from src.conrad_canvas import CanvasParser
from src.conrad_report import ConradNotebookCompiler
from src.conrad_analytics import CognitiveRetentionTracker
from src.database import init_db, SessionLocal, get_or_create_profile, update_profile
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

# Inicializa o banco de dados local SQLite (Zero-Config)
init_db()

st.set_page_config(
    page_title="Conrad — Tutor Socrático",
    page_icon="🎩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS para Dark Mode, Layout Sticky Bottom, Scroll Independente (css-layout) e Tipografia Resiliente
st.markdown(
    """
<style>
  .stApp { background-color: #121212; color: #e0e0e0; }
  .stChatMessage {
      border-radius: 8px;
      margin-bottom: 10px;
      min-inline-size: 0;
      overflow-wrap: anywhere;
      word-break: break-word;
  }

  /* Tipografia moderna (improve-text-layout-and-legibility) */
  h1, h2, h3, h4, h5, h6 {
      text-wrap: balance;
  }
  .stChatMessage p,
  .stChatMessage li,
  .stChatMessage blockquote {
      text-wrap: pretty;
      overflow-wrap: anywhere;
      word-break: break-word;
  }

  /* Contêiner de mensagens com scroll independente e estabilidade (css-layout) */
  .chat-scroll-area,
  .st-key-chat_scroll_area {
      max-height: calc(100dvh - 220px);
      overflow-y: auto;
      scrollbar-gutter: stable;
      overscroll-behavior: contain;
      min-inline-size: 0;
      padding-right: 8px;
      margin-bottom: 16px;
  }

  /* Barra de perguntas fixa no rodapé com efeito vidro (glassmorphism) */
  .stChatInput,
  div[data-testid="stChatInput"] {
      position: sticky !important;
      bottom: 0 !important;
      z-index: 999 !important;
      background: rgba(18, 18, 18, 0.85) !important;
      backdrop-filter: blur(12px) !important;
      -webkit-backdrop-filter: blur(12px) !important;
      padding-top: 10px !important;
      padding-bottom: 10px !important;
  }

  /* Estilização elegante da moldura do Quadro Negro e proteção contra overflow de matrizes extensas */
  div[data-testid="stVerticalBlockBorderWrapper"] {
      background-color: #161616 !important;
      border: 1px solid #333333 !important;
      border-radius: 10px !important;
      min-inline-size: 0 !important;
      overflow-wrap: anywhere !important;
  }
  .katex-display,
  mjx-container {
      overflow-x: auto;
      overflow-y: hidden;
      max-inline-size: 100%;
  }

  .token-badge {
      background-color: #2b2b2b;
      border: 1px solid #444;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 0.85rem;
      margin-bottom: 10px;
  }

  @media print {
      header, footer, [data-testid="stSidebar"], .stChatInput { display: none !important; }
      .stApp { background: white !important; color: black !important; }
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
    mermaid.initialize({ startOnLoad: true, theme: 'dark', securityLevel: 'strict' });
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
if "cached_tokens" not in st.session_state:
    st.session_state.cached_tokens = 0


def _load_cognitive_profile():
    """Carrega o perfil cognitivo persistente do aluno a partir do banco SQLite."""
    db = SessionLocal()
    try:
        profile = get_or_create_profile(db)
        return {
            "strengths": profile.strengths,
            "difficulties": profile.difficulties,
            "learning_style": profile.learning_style,
            "pedagogical_notes": profile.pedagogical_notes,
        }
    finally:
        db.close()


def _save_cognitive_profile(strengths: str, difficulties: str, learning_style: str, pedagogical_notes: str):
    """Persiste atualizações do perfil cognitivo no banco SQLite."""
    db = SessionLocal()
    try:
        update_profile(
            db,
            strengths=strengths,
            difficulties=difficulties,
            learning_style=learning_style,
            pedagogical_notes=pedagogical_notes,
        )
    finally:
        db.close()


cognitive_profile = _load_cognitive_profile()


def _collect_session_artifacts():
    """Reúne todos os artifacts gerados na sessão atual para compilação no Caderno Digital."""
    collected = [m["artifact"] for m in st.session_state.messages if m.get("artifact") is not None]
    if st.session_state.active_artifact and st.session_state.active_artifact not in collected:
        collected.append(st.session_state.active_artifact)
    return collected


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
    stripped = (content or "").strip()
    pattern = rf"^```(?:{expected_lang}|\w+)?\s*\n(.*?)(?:\n```)?$"
    match = re.match(pattern, stripped, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return stripped


def _format_math_for_canvas(content: str) -> str:
    """Garante que blocos $$...$$ possuam quebras de linha duplas para renderização em destaque no Quadro Negro."""
    formatted = re.sub(
        r"\$\$\s*(.*?)\s*\$\$",
        lambda m: f"\n\n$$\n{m.group(1).strip()}\n$$\n\n",
        (content or "").strip(),
        flags=re.DOTALL,
    )
    return re.sub(r"\n{3,}", "\n\n", formatted).strip()


# ==============================================================================
# --- SIDEBAR: MODOS, PERFIL COGNITIVO, BYOK & TERMÔMETRO DE RETENÇÃO ---
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

    # 3. Memória Pedagógica Persistente (Perfil Cognitivo)
    with st.expander("🧠 Seu Perfil de Aprendizado (O que o Conrad já aprendeu sobre você)", expanded=False):
        st.markdown(
            f"**✅ Pontos Fortes:** {cognitive_profile['strengths']}\n\n"
            f"**🎯 Em Evolução:** {cognitive_profile['difficulties']}\n\n"
            f"**🎨 Estilo Preferido:** {cognitive_profile['learning_style']}\n\n"
            f"**📝 Notas do Tutor:** *{cognitive_profile['pedagogical_notes']}*"
        )
        new_strengths = st.text_input("Atualizar Pontos Fortes:", value=cognitive_profile["strengths"])
        new_difficulties = st.text_input("Atualizar Temas em Evolução:", value=cognitive_profile["difficulties"])
        new_style = st.text_input("Estilo de Aprendizado:", value=cognitive_profile["learning_style"])
        if st.button("💾 Atualizar Perfil Cognitivo", use_container_width=True):
            _save_cognitive_profile(
                strengths=new_strengths,
                difficulties=new_difficulties,
                learning_style=new_style,
                pedagogical_notes=cognitive_profile["pedagogical_notes"],
            )
            st.success("Perfil cognitivo salvo no banco de dados!")
            st.rerun()

    st.divider()

    # 4. Gerenciamento da API Key (BYOK)
    st.subheader("🔑 Chave da API Gemini (BYOK)")
    api_key_input = st.text_input(
        "Insira sua chave do Google AI Studio:",
        value=st.session_state.engine.api_key or "",
        type="password",
        placeholder="AIzaSy...",
    )

    if st.button("Salvar e Validar Chave", use_container_width=True, type="primary"):
        clean_key = (api_key_input or "").strip()
        st.session_state.engine.set_api_key(clean_key)
        with st.spinner("Validando chave junto à API do Google Gemini..."):
            if st.session_state.engine.validate_api_key():
                try:
                    with open(".env", "w", encoding="utf-8") as env_file:
                        env_file.write(f"GEMINI_API_KEY={clean_key}\nGOOGLE_API_KEY={clean_key}\n")
                except Exception:
                    pass
                st.success("✅ Chave válida e ativa!")
            else:
                st.error("❌ Chave inválida ou não autorizada.")

    if st.session_state.engine.api_key:
        st.caption("🟢 Status: Chave configurada na sessão.")
    else:
        st.caption("🟠 Status: Aguardando configuração de chave.")

    # 5. Tutorial Visual Expansível
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

    # 6. Termômetro de Retenção Cognitiva
    stats_placeholder = st.empty()
    tokens_placeholder = st.empty()

    if st.button("🔄 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_artifact = None
        st.session_state.cached_tokens = 0
        if st.session_state.engine.api_key:
            st.session_state.engine._init_chat()
        st.rerun()


# ==============================================================================
# --- ÁREA PRINCIPAL: LAYOUT SPLIT-VIEW (CHAT À ESQUERDA | CANVAS À DIREITA) ---
# ==============================================================================
col_chat, col_canvas = st.columns([1.1, 0.9], gap="medium")

with col_chat:
    st.subheader("🎩 Diálogo com Conrad")
    st.caption(
        f"Modo: **{PEDAGOGICAL_MODES[st.session_state.current_mode]['nome']}** | Modelo: `{st.session_state.engine.model_name}`"
    )

    # Contêiner de mensagens com rolagem independente (.st-key-chat_scroll_area / .chat-scroll-area)
    chat_scroll_container = st.container(key="chat_scroll_area")
    with chat_scroll_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🎩" if msg["role"] == "assistant" else None):
                if msg["role"] == "assistant" and msg.get("show_cot", False):
                    _render_cot_details(msg.get("thought") or "")
                if msg.get("media_bytes") and msg.get("mime_type", "").startswith("image/"):
                    st.image(msg["media_bytes"], width=220)
                elif msg.get("media_name"):
                    st.caption(f"📄 Arquivo anexado: `{msg['media_name']}`")
                st.markdown(msg["content"])

    # Widget Multimodal de Upload de Fotos de Caderno e PDFs de Listas
    uploaded_file = st.file_uploader(
        "📎 Anexar foto do caderno, lista ou PDF de estudos:",
        type=["png", "jpg", "jpeg", "pdf"],
        key="study_media_uploader",
    )

    # Input do aluno (fixado no rodapé via CSS position: sticky)
    if prompt := st.chat_input("Como posso ajudar seus estudos hoje? (digite 'fim' para encerrar)"):
        media_bytes = None
        mime_type = None
        media_name = None
        if uploaded_file is not None:
            media_bytes = uploaded_file.getvalue()
            mime_type = uploaded_file.type or (
                "application/pdf" if uploaded_file.name.lower().endswith(".pdf") else "image/png"
            )
            media_name = uploaded_file.name

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
                "media_bytes": media_bytes,
                "mime_type": mime_type,
                "media_name": media_name,
            }
        )
        with chat_scroll_container:
            with st.chat_message("user"):
                if media_bytes and mime_type and mime_type.startswith("image/"):
                    st.image(uploaded_file, width=220)
                elif media_name:
                    st.caption(f"📄 Arquivo anexado: `{media_name}`")
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🎩"):
                # Caso 0: Prompt em branco sem anexo
                if not prompt.strip() and not media_bytes:
                    st.markdown(MSG_EMPTY_PROMPT)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": MSG_EMPTY_PROMPT, "show_cot": False}
                    )
                # Caso 1: Ausência de API Key — Resposta pré-programada graciosa (Zero Crash)
                elif not st.session_state.engine.api_key:
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
                # Caso 3: Envio Multimodal ou Streaming Throttled (40ms) + Blindagem Zero Crash
                else:
                    cot_slot = st.empty()
                    with cot_slot.container():
                        _render_cot_details()

                    memory_summary = (
                        f"Pontos fortes: {cognitive_profile['strengths']} | "
                        f"Dificuldades em evolução: {cognitive_profile['difficulties']} | "
                        f"Estilo de aprendizado: {cognitive_profile['learning_style']} | "
                        f"Notas: {cognitive_profile['pedagogical_notes']}"
                    )
                    memory_prefix = st.session_state.engine.build_context_with_memory(memory_summary)

                    response_placeholder = st.empty()
                    full_text = ""

                    try:
                        if media_bytes and mime_type:
                            multimodal_prompt = (
                                f"{memory_prefix}"
                                "Transcreva o enunciado ou equação deste material para o Quadro Negro usando "
                                '<conrad_artifact type="math" title="Enunciado Transcrito"> (ou o tipo mais adequado) '
                                "e comece guiando o estudante com uma pergunta indutiva sobre o primeiro passo.\n\n"
                                f"Mensagem do estudante: {prompt}"
                            )
                            with st.spinner("Analisando foto/documento anexado e preparando o Quadro Negro..."):
                                full_text = st.session_state.engine.send_message_multimodal(
                                    prompt=multimodal_prompt,
                                    media_bytes=media_bytes,
                                    mime_type=mime_type,
                                )
                        else:
                            contextual_prompt = f"{memory_prefix}{prompt}"
                            last_render_time = time.time()
                            RENDER_THROTTLE_SECONDS = 0.04  # Atualiza a tela a cada 40ms (~25 fps), suave e ultra-rápido

                            for chunk in st.session_state.engine.send_message_stream(contextual_prompt):
                                full_text += chunk
                                now = time.time()
                                if now - last_render_time > RENDER_THROTTLE_SECONDS:
                                    # Apenas durante a geração: preview simples sem regex pesado a cada caractere
                                    response_placeholder.markdown(full_text + "▌")
                                    last_render_time = now
                    except Exception as exc:
                        full_text = ConradEngine._format_resilient_error(exc)

                    # Ao terminar o streaming: executa o parse final completo de uma única vez
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
                    st.session_state.cached_tokens = st.session_state.engine.count_tokens()

# Atualiza o Termômetro de Retenção e Contador de Tokens na Sidebar sem bloquear o carregamento inicial
with stats_placeholder.container():
    stats = CognitiveRetentionTracker.evaluate_session(st.session_state.messages)
    st.markdown("### 🌡️ Termômetro de Retenção")
    st.progress(stats["score"] / 100)
    st.caption(f"**Nível:** {stats['status']}\n\n*{stats['feedback']}*")

with tokens_placeholder.container():
    st.divider()
    st.subheader("📊 Métricas & Utilitários")
    st.markdown(
        f"<div class='token-badge'><b>Tokens na Sessão:</b> {st.session_state.cached_tokens:,} / 1.048.576</div>",
        unsafe_allow_html=True,
    )

session_artifacts = _collect_session_artifacts()

with col_canvas:
    st.subheader("📐 Quadro Negro do Conrad")

    # Contêiner nativo com borda integrada — conteúdo 100% encapsulado
    canvas_card = st.container(border=True)
    with canvas_card:
        if st.session_state.active_artifact:
            art = st.session_state.active_artifact
            safe_art_title = html.escape(str(art.title))
            safe_art_badge = html.escape(str(art.type).upper())
            # Cabeçalho da Lousa com Badge (blindado contra injeção HTML/XSS)
            st.markdown(
                f"""
                <div style="border-bottom: 2px solid #C59B27; padding-bottom: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                    <span style="font-size: 15px; font-weight: bold; color: #f5f5f5; min-inline-size: 0; overflow-wrap: anywhere;">📌 {safe_art_title}</span>
                    <span style="background: #2A2A2A; border: 1px solid #444; font-size: 11px; padding: 2px 8px; border-radius: 4px; color: #C59B27; flex-shrink: 0;">{safe_art_badge}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Renderização interna estritamente DENTRO do container
            if art.type == "math":
                st.markdown(_format_math_for_canvas(art.content))
            elif art.type == "code":
                st.code(_clean_code_or_mermaid_fence(art.content))
            elif art.type == "mermaid":
                repaired_mermaid, is_valid_mermaid, mermaid_warn = CanvasParser.validate_and_repair_mermaid(art.content)
                st.markdown(f"```mermaid\n{repaired_mermaid}\n```")
                if not is_valid_mermaid and mermaid_warn:
                    st.caption(f"🛠️ *Estrutura do diagrama ajustada automaticamente: {mermaid_warn}*")
            else:
                st.markdown(art.content)
        else:
            st.info(
                "🎩 **O Quadro Negro está limpo.** Conforme você conversar com o Conrad sobre matemática, física ou programação, as fórmulas, diagramas e códigos aparecerão aqui dentro automaticamente!"
            )

    # Botões de Exportação do Caderno Digital no Rodapé do Canvas
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        md_data = ConradNotebookCompiler.to_markdown(
            "Matemática & Física",
            st.session_state.messages,
            session_artifacts,
        )
        st.download_button(
            "📥 Baixar Resumo (.md)",
            data=md_data,
            file_name="caderno_conrad.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_d2:
        pdf_data = ConradNotebookCompiler.to_pdf_bytes(
            "Matemática & Física",
            st.session_state.messages,
            session_artifacts,
        )
        st.download_button(
            "📄 Baixar Caderno (.pdf)",
            data=pdf_data,
            file_name="caderno_conrad.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
