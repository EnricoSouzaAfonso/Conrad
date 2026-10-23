"""
Interface Web Autônoma do Conrad (Demonstração Comercial & Uso Prático).
"""
import streamlit as st
from src.conrad_core import ConradEngine
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

st.set_page_config(page_title="Conrad — Tutor Educativo", page_icon="🎩", layout="centered")

# CSS e Identidade Visual Dark Elegante
st.markdown("""
<style>
  .stApp { background-color: #1e1e1e; color: #f0f0f0; }
  .chat-header { text-align: center; margin-bottom: 20px; }
  .stChatMessage { border-radius: 8px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# Injeção de MathJax CDN
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
""", unsafe_allow_html=True)

st.title("🎩 Conrad — Assistente Pedagógico")
st.caption("Tutor Socrático & Construtivista de Alta Performance")

if "engine" not in st.session_state:
    st.session_state.engine = ConradEngine()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibição do histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🎩" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Como posso ajudar seus estudos hoje? (digite 'fim' para encerrar)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎩"):
        response_placeholder = st.empty()
        full_text = ""
        for chunk in st.session_state.engine.send_message_stream(prompt):
            full_text += chunk
            response_placeholder.markdown(full_text + "▌")
        response_placeholder.markdown(full_text)

    st.session_state.messages.append({"role": "assistant", "content": full_text})
