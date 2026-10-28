"""
Interface Web Autônoma do Conrad — Versão 3.4.3
Polimento de UX: Unificação do Botão Flutuante da Lousa, Selectbox Read-Only,
Desativação Instantânea (Zero Delay) dos Botões de Download, Fidelidade Estrita 1:1 de Modelos,
Gems Pedagógicas Customizáveis (CRUD SQLite) e Perfil Cognitivo Multidisciplinar.
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
from src.database import (
    init_db,
    SessionLocal,
    get_or_create_profile,
    update_profile,
    reset_profile_to_default,
    get_all_gems,
    get_gem_by_id,
    create_custom_gem,
    update_custom_gem,
    delete_custom_gem,
)
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

# Inicializa o banco de dados local SQLite e semeia as 4 Gems oficiais (Zero-Config)
init_db()

st.set_page_config(
    page_title="Conrad — Tutor Socrático",
    page_icon="🎩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS: Viewport 100dvh, Scrollbar Unificada, Cabeçalho Sticky, Botão '+' no Floating Dock e Blindagem de Downloads
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

  /* ==============================================================================
     RESET DE VIEWPORT E UNIFICAÇÃO DE SCROLLBAR (PADRÃO GEMINI / CLAUDE)
     ============================================================================== */

  /* 1. Trava a raiz para evitar scroll duplo no body da página */
  html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
      height: 100dvh !important;
      max-height: 100dvh !important;
      overflow: hidden !important;
  }

  /* 2. O contêiner principal ocupa exatamente a altura da tela */
  [data-testid="stMainBlockContainer"] {
      height: 100dvh !important;
      max-height: 100dvh !important;
      padding-top: 1.5rem !important;
      padding-bottom: 0 !important;
      overflow: hidden !important;
  }

  /* 3. Coluna de Chat: Única área de rolagem vertical da esquerda */
  div[data-testid="stColumn"]:first-child {
      --scrollbar-thumb: #333333;
      --scrollbar-track: transparent;
      height: calc(100dvh - 90px) !important;
      overflow-y: auto !important;
      scrollbar-gutter: stable !important;
      scrollbar-width: thin;
      scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
      overscroll-behavior: contain !important;
      min-inline-size: 0 !important;
      padding-right: 12px !important;
      padding-bottom: 140px !important; /* Espaço reservado para o Floating Dock */
  }

  /* ==============================================================================
     REMOÇÃO DA SCROLLBAR DUPLA NA COLUNA DO QUADRO NEGRO
     ============================================================================== */

  /* 1. Coluna direita não força scrollbar permanente */
  div[data-testid="stColumn"]:last-child {
      height: auto !important;
      max-height: calc(100dvh - 90px) !important;
      overflow: visible !important;
      min-inline-size: 0 !important;
      padding-right: 4px !important;
  }

  /* Reset para colunas na Sidebar e colunas aninhadas (cabeçalho do chat e botões de download do Canvas) */
  [data-testid="stSidebar"] div[data-testid="stColumn"],
  [data-testid="stSidebar"] div[data-testid="stColumn"]:first-child,
  [data-testid="stSidebar"] div[data-testid="stColumn"]:last-child,
  div[data-testid="stColumn"] div[data-testid="stColumn"],
  div[data-testid="stColumn"] div[data-testid="stColumn"]:first-child,
  div[data-testid="stColumn"] div[data-testid="stColumn"]:last-child {
      height: auto !important;
      max-height: none !important;
      overflow: visible !important;
      padding-bottom: 0 !important;
      padding-right: 0 !important;
  }

  /* 2. O Card do Quadro Negro só rola se a dedução for muito longa, com barra discreta */
  div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlockBorderWrapper"] {
      max-height: calc(100dvh - 160px) !important;
      overflow-y: auto !important;
      scrollbar-gutter: stable !important;
      scrollbar-width: thin !important;
      scrollbar-color: transparent transparent !important; /* Invisível por padrão */
  }

  /* 3. A barra da lousa só ganha cor sutil quando o usuário passar o mouse por cima dela */
  div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlockBorderWrapper"]:hover {
      scrollbar-color: #444444 transparent !important;
  }

  /* 4. Adaptação de alto contraste para acessibilidade */
  @media (prefers-contrast: more) {
      div[data-testid="stColumn"]:first-child {
          --scrollbar-thumb: #ffffff;
          --scrollbar-track: #000000;
      }
      div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlockBorderWrapper"]:hover {
          scrollbar-color: #ffffff #000000 !important;
      }
  }

  /* 5. Customização da Scrollbar (Fallback WebKit legado isolado por @supports) */
  @supports not (scrollbar-color: auto) {
      ::-webkit-scrollbar {
          width: 6px !important;
          height: 6px !important;
      }
      ::-webkit-scrollbar-track {
          background: var(--scrollbar-track, transparent) !important;
      }
      ::-webkit-scrollbar-thumb {
          background: var(--scrollbar-thumb, #333333) !important;
          border-radius: 4px !important;
      }
      ::-webkit-scrollbar-thumb:hover {
          background: #555555 !important;
      }
  }

  /* ==============================================================================
     BOTÃO FLUTUANTE PERSISTENTE PARA ABRIR / OCULTAR O QUADRO NEGRO
     ============================================================================== */
  header[data-testid="stHeader"] {
      background: transparent !important;
      pointer-events: none !important;
  }
  header[data-testid="stHeader"] button,
  header[data-testid="stHeader"] a {
      pointer-events: auto !important;
  }
  [data-testid="stAppDeployButton"],
  [data-testid="stToolbarActions"] {
      display: none !important;
  }
  [data-testid="stStatusWidget"] {
      margin-right: 190px !important;
  }
  [data-testid="stMainMenu"] {
      margin-right: 175px !important;
  }
  .st-key-canvas_toggle_fixed_btn,
  div[data-testid="stElementContainer"]:has(.st-key-canvas_toggle_fixed_btn) {
      position: fixed !important;
      top: 14px !important;
      right: 28px !important;
      z-index: 999995 !important;
      width: auto !important;
  }
  @supports not selector(:has(*)) {
      div[data-testid="stElementContainer"].has-canvas-toggle-fixed {
          position: fixed !important;
          top: 14px !important;
          right: 28px !important;
          z-index: 999995 !important;
          width: auto !important;
      }
  }
  .st-key-canvas_toggle_fixed_btn button {
      background: rgba(28, 28, 28, 0.92) !important;
      backdrop-filter: blur(12px) !important;
      -webkit-backdrop-filter: blur(12px) !important;
      border: 1px solid rgba(255, 255, 255, 0.22) !important;
      color: #f0f0f0 !important;
      border-radius: 20px !important;
      padding: 6px 16px !important;
      font-size: 13px !important;
      font-weight: 600 !important;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.45) !important;
      transition: all 0.2s ease !important;
  }
  .st-key-canvas_toggle_fixed_btn button:hover:not(:disabled) {
      border-color: #C59B27 !important;
      color: #C59B27 !important;
      transform: scale(1.05) !important;
  }

  /* ==============================================================================
     FLOATING INPUT DOCK + BOTÃO '+' DE UPLOAD INTEGRADO (ESTILO GEMINI / CLAUDE)
     ============================================================================== */

  /* 1. Ancoragem do botão '+' de upload diretamente à esquerda da barra de chat */
  div[data-testid="stPopover"] {
      position: fixed !important;
      bottom: 28px !important;
      left: calc(21rem + 2rem) !important;
      z-index: 1005 !important;
      width: 46px !important;
  }
  div[data-testid="stPopover"] button {
      border-radius: 50% !important;
      width: 46px !important;
      height: 46px !important;
      min-height: 46px !important;
      padding: 0 !important;
      background-color: #262626 !important;
      border: 1px solid rgba(255, 255, 255, 0.18) !important;
      color: #C59B27 !important;
      font-size: 18px !important;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
      transition: transform 0.2s ease, border-color 0.2s ease !important;
  }
  div[data-testid="stPopover"] button:hover {
      border-color: #C59B27 !important;
      transform: scale(1.05) !important;
  }
  /* Oculta a setinha nativa do dropdown no botão circular '+' */
  div[data-testid="stPopover"] button svg {
      display: none !important;
  }

  /* 2. Fixa a barra de input permanentemente no rodapé da tela ao lado do botão '+' */
  div[data-testid="stChatInput"],
  .stChatInput {
      position: fixed !important;
      bottom: 24px !important;
      z-index: 1000 !important;
      left: calc(21rem + 2rem + 56px) !important;
      width: calc(44% - 56px) !important;
      max-width: calc(54% - 56px) !important;
      background: rgba(22, 22, 22, 0.85) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      border-radius: 28px !important;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
      padding: 4px 10px !important;
      transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
  }

  /* 3. Destaque ao focar no campo de digitação */
  div[data-testid="stChatInput"]:focus-within,
  .stChatInput:focus-within {
      border-color: #C59B27 !important;
      box-shadow: 0 10px 35px rgba(197, 155, 39, 0.25) !important;
  }

  /* 4. Ajuste responsivo caso a sidebar esteja colapsada ou em telas menores */
  @media (max-width: 1024px) {
      div[data-testid="stPopover"] {
          left: 5% !important;
      }
      div[data-testid="stChatInput"],
      .stChatInput {
          width: calc(90% - 56px) !important;
          max-width: calc(90% - 56px) !important;
          left: calc(5% + 56px) !important;
      }
  }

  /* 5. Espaçamento de segurança no final do chat (Garante que a última mensagem não seja coberta) */
  .chat-bottom-spacer {
      height: 120px !important;
      width: 100% !important;
      clear: both !important;
  }

  /* ==============================================================================
     MICRO-COMPONENTE DE RETENÇÃO COM HOVER TOOLTIP / POPOVER HINT (WCAG 1.4.13)
     ============================================================================== */
  .retention-micro-wrapper {
      position: relative;
      margin-bottom: 10px;
  }
  .retention-trigger-btn {
      all: unset;
      box-sizing: border-box;
      display: block;
      width: 100%;
      cursor: help;
      padding: 6px 8px;
      border-radius: 6px;
      background: #1b1b1b;
      border: 1px solid #303030;
      --interest-delay-start: 0.15s;
      interest-delay-start: var(--interest-delay-start);
      --interest-delay-end: 0.1s;
      interest-delay-end: var(--interest-delay-end);
  }
  .retention-trigger-btn:hover,
  .retention-trigger-btn:focus-visible,
  .retention-trigger-btn:is(:interest-source, .interest-source) {
      border-color: #C59B27;
  }
  .retention-tooltip-card {
      visibility: hidden;
      opacity: 0;
      position: absolute;
      bottom: calc(100% + 6px);
      left: 0;
      right: 0;
      background: #1f1f1f;
      border: 1px solid #C59B27;
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 11px;
      color: #e8e8e8;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.65);
      z-index: 1200;
      transition: opacity 0.18s ease, visibility 0.18s ease;
      pointer-events: auto;
  }
  .retention-micro-wrapper:hover .retention-tooltip-card,
  .retention-micro-wrapper:focus-within .retention-tooltip-card,
  .retention-tooltip-card:is(:interest-target, .interest-target) {
      visibility: visible;
      opacity: 1;
  }

  /* Bloqueio do cursor de digitação no selectbox para experiência de dropdown puro */
  div[data-testid="stSelectbox"] input {
      caret-color: transparent !important;
      cursor: pointer !important;
      user-select: none !important;
  }

  /* ==============================================================================
     BLINDAGEM E DESATIVAÇÃO INSTANTÂNEA DOS BOTÕES DE DOWNLOAD (ZERO DELAY)
     ============================================================================== */
  .generating-active button[kind="primary"],
  .generating-active div[data-testid="stDownloadButton"] button,
  [data-testid="stDownloadButton"] button:disabled,
  div[data-testid="stDownloadButton"] button:disabled,
  body:has(div[data-testid="stChatInput"] textarea:disabled) div[data-testid="stDownloadButton"] button,
  .stApp:has([data-testid="stStatusWidget"]) div[data-testid="stDownloadButton"] button {
      pointer-events: none !important;
      opacity: 0.35 !important;
      cursor: not-allowed !important;
      filter: grayscale(80%) !important;
      transition: none !important; /* Elimina qualquer atraso de transição na desativação */
  }
  @supports not selector(:has(*)) {
      .stApp.is-generating-fallback div[data-testid="stDownloadButton"] button {
          pointer-events: none !important;
          opacity: 0.35 !important;
          cursor: not-allowed !important;
          filter: grayscale(80%) !important;
          transition: none !important;
      }
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
      background-color: #1f1f1f;
      border: 1px solid #333;
      border-radius: 6px;
      padding: 6px 10px;
      font-size: 0.78rem;
      color: #bbb;
      margin-bottom: 10px;
  }

  @media print {
      header, footer, [data-testid="stSidebar"], .stChatInput, #jump-to-bottom-btn, div[data-testid="stPopover"] { display: none !important; }
      .stApp { background: white !important; color: black !important; }
  }
</style>
""",
    unsafe_allow_html=True,
)

# Injeção de MathJax v3, Mermaid.js CDN, Selectbox Read-Only e Trava Instantânea de Downloads
st.markdown(
    """
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  if (window.mermaid) {
    mermaid.initialize({ startOnLoad: true, theme: 'dark', securityLevel: 'strict' });
  }
  if (typeof HTMLButtonElement !== 'undefined' && !HTMLButtonElement.prototype.hasOwnProperty('interestForElement')) {
    document.documentElement.dataset.interestPolyfillFallback = 'css-hover';
  }
  if (typeof CSS !== 'undefined' && !CSS.supports('selector(:has(*))')) {
    const containers = document.querySelectorAll('div[data-testid="stElementContainer"]');
    containers.forEach(c => {
      if (c.querySelector('.st-key-canvas_toggle_fixed_btn')) {
        c.classList.add('has-canvas-toggle-fixed');
      }
    });
  }

  // 1. Bloqueia digitação em todos os inputs de selectbox (Dropdown Puro / Read-Only)
  function enforceReadonlySelectboxes() {
    const inputs = document.querySelectorAll('div[data-testid="stSelectbox"] input');
    inputs.forEach(inp => {
      if (!inp.readOnly) {
        inp.readOnly = true;
        inp.setAttribute('readonly', 'readonly');
        inp.style.cursor = 'pointer';
        inp.style.caretColor = 'transparent';
      }
    });
  }

  // 2. Trava instantânea dos botões de download no milissegundo do envio
  function lockDownloadButtonsImmediately() {
    window._conradSubmittingTs = Date.now();
    const appRoot = document.querySelector('.stApp');
    if (appRoot) {
      appRoot.classList.add('generating-active');
      if (typeof CSS !== 'undefined' && !CSS.supports('selector(:has(*))')) {
        appRoot.classList.add('is-generating-fallback');
      }
    }
    const dlButtons = document.querySelectorAll('div[data-testid="stDownloadButton"] button');
    dlButtons.forEach(btn => {
      btn.disabled = true;
      btn.setAttribute('disabled', 'disabled');
      btn.setAttribute('aria-disabled', 'true');
      btn.style.pointerEvents = 'none';
      btn.style.opacity = '0.35';
      btn.style.cursor = 'not-allowed';
      btn.style.filter = 'grayscale(80%)';
    });
  }

  function unlockDownloadButtons() {
    const appRoot = document.querySelector('.stApp');
    if (appRoot) {
      appRoot.classList.remove('generating-active', 'is-generating-fallback');
    }
    const dlButtons = document.querySelectorAll('div[data-testid="stDownloadButton"] button');
    dlButtons.forEach(btn => {
      btn.disabled = false;
      btn.removeAttribute('disabled');
      btn.removeAttribute('aria-disabled');
      btn.style.pointerEvents = '';
      btn.style.opacity = '';
      btn.style.cursor = '';
      btn.style.filter = '';
    });
  }

  // Escuta eventos de submissão do chat (tecla Enter e clique no botão de envio)
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey && e.target.closest('div[data-testid="stChatInput"]')) {
      lockDownloadButtonsImmediately();
    }
  }, true);

  document.addEventListener('click', function(e) {
    if (e.target.closest('button[data-testid="stChatInputSubmitButton"]')) {
      lockDownloadButtonsImmediately();
    }
  }, true);

  // Observador contínuo para manter os selects read-only após re-renderizações do Streamlit
  enforceReadonlySelectboxes();
  if (window._conradObserver) {
    window._conradObserver.disconnect();
  }
  window._conradObserver = new MutationObserver(() => {
    enforceReadonlySelectboxes();
    const isRunning = Boolean(document.querySelector('[data-testid="stStatusWidget"]'));
    if (isRunning) {
      window._conradSawRunning = true;
      lockDownloadButtonsImmediately();
    } else if (window._conradSawRunning || (window._conradSubmittingTs && Date.now() - window._conradSubmittingTs > 1500)) {
      window._conradSawRunning = false;
      window._conradSubmittingTs = 0;
      unlockDownloadButtons();
    }
  });
  window._conradObserver.observe(document.body, { childList: true, subtree: true });
</script>
<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" style="display:none;" alt="" onload="
  window.enforceReadonlySelectboxes = function() {
    const inputs = document.querySelectorAll('div[data-testid=\\'stSelectbox\\'] input');
    inputs.forEach(inp => {
      inp.setAttribute('inputmode', 'none');
      inp.style.cursor = 'pointer';
      inp.style.caretColor = 'transparent';
      inp.style.userSelect = 'none';
    });
  };
  window.lockDownloadButtonsImmediately = function() {
    window._conradSubmittingTs = Date.now();
    const appRoot = document.querySelector('.stApp');
    if (appRoot) {
      appRoot.classList.add('generating-active');
      if (typeof CSS !== 'undefined' && !CSS.supports('selector(:has(*))')) {
        appRoot.classList.add('is-generating-fallback');
      }
    }
    const dlButtons = document.querySelectorAll('div[data-testid=\\'stDownloadButton\\'] button');
    dlButtons.forEach(btn => {
      btn.disabled = true;
      btn.setAttribute('disabled', 'disabled');
      btn.setAttribute('aria-disabled', 'true');
      btn.style.pointerEvents = 'none';
      btn.style.opacity = '0.35';
      btn.style.cursor = 'not-allowed';
      btn.style.filter = 'grayscale(80%)';
    });
  };
  window.unlockDownloadButtons = function() {
    const appRoot = document.querySelector('.stApp');
    if (appRoot) {
      appRoot.classList.remove('generating-active', 'is-generating-fallback');
    }
    const dlButtons = document.querySelectorAll('div[data-testid=\\'stDownloadButton\\'] button');
    dlButtons.forEach(btn => {
      btn.disabled = false;
      btn.removeAttribute('disabled');
      btn.removeAttribute('aria-disabled');
      btn.style.pointerEvents = '';
      btn.style.opacity = '';
      btn.style.cursor = '';
      btn.style.filter = '';
    });
  };
  if (!window._conradListenersBound) {
    window._conradListenersBound = true;
    document.addEventListener('keydown', function(e) {
      if (e.target.closest && e.target.closest('div[data-testid=\\'stSelectbox\\']')) {
        if (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Delete') {
          e.preventDefault();
          e.stopPropagation();
          return false;
        }
      }
      if (e.key === 'Enter' && !e.shiftKey && e.target.closest && e.target.closest('div[data-testid=\\'stChatInput\\']')) {
        window.lockDownloadButtonsImmediately();
      }
    }, true);
    document.addEventListener('click', function(e) {
      if (e.target.closest && e.target.closest('button[data-testid=\\'stChatInputSubmitButton\\']')) {
        window.lockDownloadButtonsImmediately();
      }
    }, true);
  }
  window.enforceReadonlySelectboxes();
  if (window._conradObserver) {
    window._conradObserver.disconnect();
  }
  window._conradObserver = new MutationObserver(() => {
    window.enforceReadonlySelectboxes();
    const isRunning = Boolean(document.querySelector('[data-testid=\\'stStatusWidget\\']'));
    if (isRunning) {
      window._conradSawRunning = true;
      window.lockDownloadButtonsImmediately();
    } else if (window._conradSawRunning || (window._conradSubmittingTs && Date.now() - window._conradSubmittingTs > 1500)) {
      window._conradSawRunning = false;
      window._conradSubmittingTs = 0;
      window.unlockDownloadButtons();
    }
  });
  window._conradObserver.observe(document.body, { childList: true, subtree: true });
" />
""",
    unsafe_allow_html=True,
)

# Inicialização de Estados Reativos (Lazy — Zero Crash sem API Key)
if "engine" not in st.session_state:
    st.session_state.engine = ConradEngine()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_label" not in st.session_state or st.session_state.selected_model_label not in DEFINITIVE_MODELS:
    st.session_state.selected_model_label = list(DEFINITIVE_MODELS.keys())[0]
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "socratico"
if "active_artifact" not in st.session_state:
    st.session_state.active_artifact = None
if "canvas_collapsed" not in st.session_state:
    st.session_state.canvas_collapsed = False
if "cached_tokens" not in st.session_state:
    st.session_state.cached_tokens = 0
if "pending_upload" not in st.session_state:
    st.session_state.pending_upload = None
if "uploader_key_counter" not in st.session_state:
    st.session_state.uploader_key_counter = 0
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False


def _load_cognitive_profile():
    """Carrega o perfil cognitivo multidisciplinar do aluno a partir do banco SQLite."""
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


def _load_all_gems_map():
    """Carrega todas as Gems pedagógicas (oficiais + customizadas) do banco SQLite."""
    db = SessionLocal()
    try:
        gems = get_all_gems(db)
        return {
            g.gem_id: {
                "gem_id": g.gem_id,
                "name": g.name,
                "description": g.description,
                "system_directive": g.system_directive,
                "is_builtin": g.is_builtin,
            }
            for g in gems
        }
    finally:
        db.close()


cognitive_profile = _load_cognitive_profile()
gem_options = _load_all_gems_map()
if st.session_state.current_mode not in gem_options:
    st.session_state.current_mode = "socratico"


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
# --- SIDEBAR REESTRUTURADA (ORDEM ERGONÔMICA: BYOK NO TOPO -> MODELO -> GEMS) ---
# ==============================================================================
with st.sidebar:
    # 0. Cabeçalho Oficial
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;'>{CONRAD_AVATAR_SVG} <h3 style='margin:0;'>Configurações</h3></div>",
        unsafe_allow_html=True,
    )
    st.caption("Personalize sua chave de acesso, motor cognitivo e Gems de tutoria.")

    # =========================================================================
    # 1. CHAVE DE API GEMINI (BYOK) — TOPO ABSOLUTO
    # =========================================================================
    st.markdown("#### 🔑 Chave de API Gemini (BYOK)")
    api_key_input = st.text_input(
        "Insira sua chave do Google AI Studio:",
        value=st.session_state.engine.api_key or "",
        type="password",
        placeholder="AIzaSy...",
        label_visibility="collapsed",
    )
    col_k1, col_k2 = st.columns([0.65, 0.35])
    with col_k1:
        if st.button("Salvar Chave", use_container_width=True, type="primary"):
            clean_key = (api_key_input or "").strip()
            st.session_state.engine.set_api_key(clean_key)
            with st.spinner("Validando..."):
                if st.session_state.engine.validate_api_key():
                    try:
                        with open(".env", "w", encoding="utf-8") as env_file:
                            env_file.write(f"GEMINI_API_KEY={clean_key}\nGOOGLE_API_KEY={clean_key}\n")
                    except Exception:
                        pass
                    st.success("✅ Ativa!")
                else:
                    st.error("❌ Inválida.")
    with col_k2:
        if st.session_state.engine.api_key:
            st.markdown(
                "<div style='color:#4caf50;font-size:12px;margin-top:8px;'>● Conectado</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='color:#ff9800;font-size:12px;margin-top:8px;'>○ Aguardando</div>",
                unsafe_allow_html=True,
            )

    with st.expander("📘 Como Obter sua Chave Gratuita", expanded=not bool(st.session_state.engine.api_key)):
        st.markdown(
            """
            1. Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey) e faça login.
            2. Clique no botão azul **"Create API Key"**.
            3. Cole a chave (`AIza...`) acima e clique em **"Salvar e Validar Chave"**.

            💡 *100% gratuita para estudantes e professores!*
            """
        )

    st.divider()

    # =========================================================================
    # 2. SELETOR DE MODELO DE IA
    # =========================================================================
    st.markdown("#### 🤖 Modelo de IA")
    selected_label = st.selectbox(
        "Modelo de IA",
        options=list(DEFINITIVE_MODELS.keys()),
        index=list(DEFINITIVE_MODELS.keys()).index(st.session_state.selected_model_label),
        label_visibility="collapsed",
    )
    selected_model_id = DEFINITIVE_MODELS[selected_label]
    if selected_model_id != st.session_state.engine.model_name:
        st.session_state.selected_model_label = selected_label
        st.session_state.engine.set_model(selected_model_id)
        st.toast(f"Modelo alterado para {selected_model_id}!", icon="🤖")
        st.rerun()  # Força atualização imediata do ciclo de vida do Streamlit

    # Badge de confirmação transparente
    st.caption(f"⚡ Motor ativo no backend: `{st.session_state.engine.model_name}`")

    st.divider()

    # =========================================================================
    # 3. MODO PEDAGÓGICO / GEMS DINÂMICAS (CRUD COMPLETO)
    # =========================================================================
    st.markdown("#### 💎 Gem Pedagógica Ativa")
    gem_keys = list(gem_options.keys())
    selected_gem_id = st.selectbox(
        "Gem Pedagógica Ativa",
        options=gem_keys,
        index=gem_keys.index(st.session_state.current_mode),
        format_func=lambda k: gem_options[k]["name"],
        help="Selecione uma Gem oficial ou crie sua própria Gem personalizada para qualquer disciplina.",
        label_visibility="collapsed",
    )
    active_gem_data = gem_options[selected_gem_id]
    if st.session_state.get("current_mode") != selected_gem_id:
        st.session_state.current_mode = selected_gem_id
        st.session_state.engine.set_gem(selected_gem_id, active_gem_data["system_directive"])
        st.toast(f"Gem ativada: {active_gem_data['name']}!", icon="💎")
    st.caption(f"ℹ️ {active_gem_data['description']}")

    with st.expander("💎 Gerenciar Gems Pedagógicas (Criar / Editar)", expanded=False):
        tab_create, tab_manage = st.tabs(["✨ Criar Nova", "🗂️ Minhas Gems"])
        with tab_create:
            new_gem_name = st.text_input("Nome da Gem:", placeholder="Ex: Redação ENEM ✍️", key="new_gem_name")
            new_gem_desc = st.text_input(
                "Descrição curta:",
                placeholder="Ex: Guia estruturado nas 5 competências do ENEM",
                key="new_gem_desc",
            )
            new_gem_dir = st.text_area(
                "Diretrizes Pedagógicas da IA:",
                placeholder="Ex: [MODO ATIVO: REDAÇÃO ENEM] Avalie tese, repertório sociocultural e proposta de intervenção...",
                height=90,
                key="new_gem_dir",
            )
            if st.button("✨ Criar Gem Pedagógica", use_container_width=True):
                if new_gem_name.strip() and new_gem_dir.strip():
                    db = SessionLocal()
                    try:
                        created = create_custom_gem(
                            db,
                            name=new_gem_name,
                            description=new_gem_desc or "Gem pedagógica customizada",
                            system_directive=new_gem_dir,
                        )
                        st.session_state.current_mode = created.gem_id
                        st.session_state.engine.set_gem(created.gem_id, created.system_directive)
                    finally:
                        db.close()
                    st.success(f"Gem '{new_gem_name.strip()}' criada e ativada!")
                    st.rerun()
                else:
                    st.warning("Preencha o nome e as diretrizes da Gem.")

        with tab_manage:
            custom_gems = [g for g in gem_options.values() if g["is_builtin"] == 0]
            if not custom_gems:
                st.caption("Você ainda não criou Gems customizadas. As 4 Gems oficiais são protegidas (🔒).")
            for cg in custom_gems:
                cg_id = cg["gem_id"]
                st.markdown(f"**💎 {html.escape(cg['name'])}**")
                edit_name = st.text_input("Nome:", value=cg["name"], key=f"edit_name_{cg_id}")
                edit_desc = st.text_input("Descrição:", value=cg["description"], key=f"edit_desc_{cg_id}")
                edit_dir = st.text_area("Diretrizes:", value=cg["system_directive"], height=70, key=f"edit_dir_{cg_id}")
                c_up, c_del = st.columns(2)
                with c_up:
                    if st.button("💾 Salvar", key=f"btn_save_{cg_id}", use_container_width=True):
                        db = SessionLocal()
                        try:
                            update_custom_gem(db, cg_id, edit_name, edit_desc, edit_dir)
                            if st.session_state.current_mode == cg_id:
                                st.session_state.engine.set_gem(cg_id, edit_dir)
                        finally:
                            db.close()
                        st.success("Gem atualizada!")
                        st.rerun()
                with c_del:
                    if st.button("🗑️ Excluir", key=f"btn_del_{cg_id}", use_container_width=True):
                        db = SessionLocal()
                        try:
                            delete_custom_gem(db, cg_id)
                        finally:
                            db.close()
                        if st.session_state.current_mode == cg_id:
                            st.session_state.current_mode = "socratico"
                            st.session_state.engine.set_pedagogical_mode("socratico")
                        st.info("Gem excluída.")
                        st.rerun()

    st.divider()

    # =========================================================================
    # 4. MEMÓRIA PEDAGÓGICA (PERFIL COGNITIVO NEUTRO MULTIDISCIPLINAR)
    # =========================================================================
    with st.expander("🧠 Perfil de Aprendizado (Memória do Aluno)", expanded=False):
        st.markdown(
            f"**✅ Pontos Fortes:** {cognitive_profile['strengths']}\n\n"
            f"**🎯 Em Evolução:** {cognitive_profile['difficulties']}\n\n"
            f"**🎨 Estilo Preferido:** {cognitive_profile['learning_style']}\n\n"
            f"**📝 Notas do Tutor:** *{cognitive_profile['pedagogical_notes']}*"
        )
        new_strengths = st.text_input("Atualizar Pontos Fortes:", value=cognitive_profile["strengths"])
        new_difficulties = st.text_input("Atualizar Temas em Evolução:", value=cognitive_profile["difficulties"])
        new_style = st.text_input("Estilo de Aprendizado:", value=cognitive_profile["learning_style"])

        col_save_prof, col_reset_prof = st.columns([0.65, 0.35])
        with col_save_prof:
            if st.button("💾 Atualizar Perfil", use_container_width=True):
                _save_cognitive_profile(
                    strengths=new_strengths,
                    difficulties=new_difficulties,
                    learning_style=new_style,
                    pedagogical_notes=cognitive_profile["pedagogical_notes"],
                )
                st.success("Perfil atualizado!")
                st.rerun()
        with col_reset_prof:
            if st.button("🔄 Resetar", use_container_width=True, help="Restaurar perfil inicial neutro"):
                db = SessionLocal()
                try:
                    reset_profile_to_default(db)
                finally:
                    db.close()
                st.info("Perfil restaurado para padrão multidisciplinar!")
                st.rerun()

    st.divider()

    # =========================================================================
    # 5. RETENÇÃO DISCRETA (HOVER TOOLTIP) & MÉTRICAS COMPACTAS
    # =========================================================================
    stats_placeholder = st.empty()
    tokens_placeholder = st.empty()

    # 6. Botão Nova Conversa
    if st.button("🔄 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_artifact = None
        st.session_state.cached_tokens = 0
        st.session_state.pending_upload = None
        if st.session_state.engine.api_key:
            # Garante que o novo chat use estritamente o modelo configurado
            st.session_state.engine.set_model(st.session_state.engine.model_name)
        st.rerun()


# ==============================================================================
# --- POPOVER '+' DE UPLOAD E FLOATING INPUT DOCK (FORA DO FLUXO DESCENDENTE) ---
# ==============================================================================
with st.popover("➕", help="Anexar foto de caderno, lista de exercícios ou PDF"):
    st.markdown("**📎 Anexar Material de Estudo**")
    uploaded = st.file_uploader(
        "Selecione um arquivo:",
        type=["png", "jpg", "jpeg", "pdf"],
        key=f"dock_file_uploader_{st.session_state.uploader_key_counter}",
        label_visibility="collapsed",
    )
    if uploaded is not None:
        st.session_state.pending_upload = uploaded
    if st.session_state.pending_upload is not None:
        if st.button("🗑️ Remover anexo", use_container_width=True):
            st.session_state.pending_upload = None
            st.session_state.uploader_key_counter += 1
            st.rerun()

# Chip Flutuante de Pré-visualização se houver anexo carregado
if st.session_state.pending_upload is not None:
    chip_name = st.session_state.pending_upload.name
    st.markdown(
        f"""
        <div id="pending-upload-chip" style="position: fixed; bottom: 82px; left: calc(21rem + 2rem + 56px); z-index: 1002;
                    background: #252525; border: 1px solid #C59B27; border-radius: 16px; padding: 4px 12px;
                    display: flex; align-items: center; gap: 8px; font-size: 12px; color: #f0f0f0; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <span>📎 {html.escape(chip_name)}</span>
            <span style="color: #C59B27; font-weight: 600;">Pronto para envio</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

prompt = st.chat_input("Como posso ajudar seus estudos hoje? (digite 'fim' para encerrar)")

# Injeção dinâmica de CSS dependendo do estado do Canvas
if st.session_state.canvas_collapsed:
    st.markdown(
        """
    <style>
      [data-testid="stMainBlockContainer"] {
          max-width: 820px !important;
          margin-inline: auto !important;
          overflow-y: auto !important;
          scrollbar-gutter: stable !important;
          scrollbar-width: thin;
          scrollbar-color: #333333 transparent;
          padding-bottom: 140px !important;
      }
      div[data-testid="stColumn"]:first-child {
          height: auto !important;
          max-height: none !important;
          overflow: visible !important;
          padding-bottom: 0 !important;
      }
      div[data-testid="stPopover"] {
          left: calc(50% + 10rem - 395px) !important;
      }
      div[data-testid="stChatInput"],
      .stChatInput {
          width: 90% !important;
          max-width: 720px !important;
          left: calc(50% + 10rem) !important;
          transform: translateX(-50%) !important;
      }
      #jump-to-bottom-btn {
          left: calc(50% + 10rem) !important;
      }
    </style>
    """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# --- ÁREA PRINCIPAL: DIVISÃO ADAPTATIVA (SPLIT-VIEW OU MODO EXPANDIDO) ---
# ==============================================================================
# Botão Flutuante Persistente de Controle da Lousa (Acompanha o Viewport em qualquer nível de scroll)
btn_fixed_label = "📐 Abrir Lousa" if st.session_state.canvas_collapsed else "✖ Ocultar Lousa"
if st.button(btn_fixed_label, key="canvas_toggle_fixed_btn", help="Alternar visualização do Quadro Negro lateral a qualquer momento"):
    st.session_state.canvas_collapsed = not st.session_state.canvas_collapsed
    st.rerun()

if st.session_state.canvas_collapsed:
    # MODO EXPANDIDO: Chat ocupa a tela com largura confortável e centralizada
    col_chat = st.container()
    col_canvas = None
else:
    # MODO SPLIT-VIEW: Chat à esquerda e Quadro Negro à direita
    col_chat, col_canvas = st.columns([1.1, 0.9], gap="medium")

with col_chat:
    st.subheader("🎩 Diálogo com Conrad")

    st.caption(
        f"Gem: **{active_gem_data['name']}** | Modelo Ativo: `{st.session_state.engine.model_name}`"
    )

    # Renderização das mensagens em trilha única (sem container de scroll aninhado)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🎩" if msg["role"] == "assistant" else None):
            if msg["role"] == "assistant" and msg.get("show_cot", False):
                _render_cot_details(msg.get("thought") or "")
            if msg.get("media_bytes") and msg.get("mime_type", "").startswith("image/"):
                st.image(msg["media_bytes"], width=220)
            elif msg.get("media_name"):
                st.caption(f"📄 Arquivo anexado: `{msg['media_name']}`")
            st.markdown(msg["content"])

    # Processamento da nova mensagem submetida no Floating Input Dock
    if prompt:
        st.session_state.is_generating = True
        try:
            media_bytes = None
            mime_type = None
            media_name = None
            pending_file = st.session_state.pending_upload
            if pending_file is not None:
                media_bytes = pending_file.getvalue()
                mime_type = pending_file.type or (
                    "application/pdf" if pending_file.name.lower().endswith(".pdf") else "image/png"
                )
                media_name = pending_file.name
                st.session_state.pending_upload = None
                st.session_state.uploader_key_counter += 1

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt,
                    "media_bytes": media_bytes,
                    "mime_type": mime_type,
                    "media_name": media_name,
                }
            )
            with st.chat_message("user"):
                if media_bytes and mime_type and mime_type.startswith("image/"):
                    st.image(media_bytes, width=220)
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
                                    response_placeholder.markdown(full_text + "▌")
                                    last_render_time = now
                    except Exception as exc:
                        full_text = st.session_state.engine._format_resilient_error(exc)

                    # Ao terminar o streaming: executa o parse final completo de uma única vez
                    text_without_thought, extracted_thought = CanvasParser.parse_thought(full_text)
                    if extracted_thought:
                        with cot_slot.container():
                            _render_cot_details(extracted_thought)

                    clean_chat_text, artifact = CanvasParser.parse_message(text_without_thought)
                    response_placeholder.markdown(clean_chat_text)

                    was_collapsed = st.session_state.canvas_collapsed
                    if artifact is not None:
                        st.session_state.active_artifact = artifact
                        st.session_state.canvas_collapsed = False  # Auto-reveal estilo Claude Artifacts

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
                    if was_collapsed and artifact is not None:
                        st.session_state.is_generating = False
                        st.rerun()
        finally:
            st.session_state.is_generating = False

    # Âncora de espaçamento final e Botão Flutuante "Rolar para o Fim" (↓)
    st.markdown(
        """
<div id="chat-bottom-anchor" class="chat-bottom-spacer"></div>

<button id="jump-to-bottom-btn" title="Rolar para as mensagens recentes" onclick="
    const mainBlock = document.querySelector('[data-testid=\\'stMainBlockContainer\\']');
    const chatCol = document.querySelector('div[data-testid=\\'stColumn\\']:first-child');
    const target = (mainBlock && mainBlock.scrollHeight > mainBlock.clientHeight) ? mainBlock : chatCol;
    if (target) {
        target.scrollTo({ top: target.scrollHeight, behavior: 'smooth' });
    }
">
    ↓
</button>

<style>
#jump-to-bottom-btn {
    position: fixed;
    bottom: 95px;
    left: calc(21rem + 2rem + 22%);
    transform: translateX(-50%);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: #262626;
    color: #f0f0f0;
    border: 1px solid #444;
    cursor: pointer;
    z-index: 999;
    font-size: 16px;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transition: background-color 0.2s ease, transform 0.2s ease;
}
#jump-to-bottom-btn:hover {
    background-color: #333333;
    border-color: #C59B27;
    transform: translateX(-50%) scale(1.08);
}
</style>
""",
        unsafe_allow_html=True,
    )

# Atualiza o Micro-Termômetro de Retenção (Hover Tooltip) e Contador de Tokens na Sidebar
with stats_placeholder.container():
    stats = CognitiveRetentionTracker.evaluate_session(st.session_state.messages)
    retention_score = int(stats.get("score", 0))
    retention_status = html.escape(str(stats.get("status", "Iniciando")))
    retention_feedback = html.escape(str(stats.get("feedback", "Explore novos temas com o tutor.")))
    active_topic = html.escape(str(stats.get("active_topic", "Exploratório / Multidisciplinar")))

    st.markdown(
        f"""
        <div class="retention-micro-wrapper" title="Tema Ativo: {active_topic}&#10;Retenção Estimada: {retention_score}%&#10;Nível: {retention_status}&#10;Diagnóstico: {retention_feedback}">
          <button type="button" class="retention-trigger-btn" interestfor="retention-hint-popover">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; font-size:12px; color:#aaa;">
              <span>🌡️ Retenção do Tema</span>
              <span style="font-weight:bold; color:#C59B27;">{retention_score}%</span>
            </div>
            <div style="background:#262626; border-radius:4px; height:6px; width:100%; overflow:hidden;">
              <div style="background: linear-gradient(90deg, #C59B27, #4caf50); height:100%; width:{max(5, retention_score)}%; transition: width 0.4s ease;"></div>
            </div>
          </button>
          <div popover="hint" id="retention-hint-popover" class="retention-tooltip-card">
            <div><b>📌 Tema Ativo:</b> {active_topic}</div>
            <div><b>🌡️ Retenção:</b> {retention_score}% — {retention_status}</div>
            <div style="color:#bbb; margin-top:4px;">{retention_feedback}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tokens_placeholder.container():
    st.markdown(
        f"<div class='token-badge'><b>📊 Tokens na Sessão:</b> {st.session_state.cached_tokens:,} / 1.048.576</div>",
        unsafe_allow_html=True,
    )

session_artifacts = _collect_session_artifacts()

if col_canvas is not None:
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

        # Botões de Exportação do Caderno Digital no Rodapé do Canvas (Blindados contra cliques concorrentes)
        is_busy = st.session_state.get("is_generating", False)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            md_data = ConradNotebookCompiler.to_markdown(
                "Caderno Multidisciplinar",
                st.session_state.messages,
                session_artifacts,
            )
            st.download_button(
                "📥 Baixar Resumo (.md)",
                data=md_data,
                file_name="caderno_conrad.md",
                mime="text/markdown",
                use_container_width=True,
                disabled=is_busy,
            )
        with col_d2:
            pdf_data = ConradNotebookCompiler.to_pdf_bytes(
                "Caderno Multidisciplinar",
                st.session_state.messages,
                session_artifacts,
            )
            st.download_button(
                "📄 Baixar Caderno (.pdf)",
                data=pdf_data,
                file_name="caderno_conrad.pdf",
                mime="application/pdf",
                use_container_width=True,
                disabled=is_busy,
            )
