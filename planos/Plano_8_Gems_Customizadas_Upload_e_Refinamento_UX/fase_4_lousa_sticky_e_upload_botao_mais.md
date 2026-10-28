# 📋 Especificação Técnica de Engenharia — Plano 8: Fase 4
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 8 — Gems Pedagógicas Customizáveis, Upload Integrado e Refinamento de UX/UI  
**Etapa:** Fase 4 — Lousa Sticky Persistente e Upload Integrado com Botão "+" no Input Dock  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. Botão de Lousa Perdido no Scroll
* **Sintoma:** O botão `[ 📐 Abrir Lousa ]` foi colocado no cabeçalho comum do chat. Conforme o estudante dialoga com o Conrad e a conversa cresce, o cabeçalho sobe junto com a primeira mensagem. Para reabrir a lousa oculta, o usuário precisa rolar o chat inteiro de volta para o topo.
* **Causa Raiz:** Ausência de ancoragem fixa (`position: sticky` ou `position: fixed`) no container de cabeçalho do chat.

### 1.2. Upload Deslocado e Invasivo no Fluxo de Mensagens
* **Sintoma:** O campo `st.file_uploader` está inserido no meio da coluna de mensagens, consumindo espaço vertical e forçando o estudante a olhar para o topo toda vez que quer enviar um anexo.
* **O Padrão Universal da Indústria (ChatGPT, Gemini, Claude):**
  * O botão de anexo fica como um ícone `+` ou clipe `📎` diretamente acoplado à barra inferior de digitação (Floating Dock).
  * Ao anexar uma imagem ou PDF, um badge flutuante (*file chip*) surge logo acima do campo de texto com o nome do arquivo e botão de descarte `[ ✕ ]`.

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Implementar cabeçalho Sticky para controle da lousa, mover o upload para um popover `+` posicionado no Floating Dock e adicionar o chip de anexo flutuante).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Cabeçalho Sticky Persistente no `app.py`
1. Envolver o cabeçalho do chat em um container sticky ou fixar o botão via CSS:
```css
/* Cabeçalho Sticky do Chat com efeito Glassmorphism */
.chat-sticky-header {
    position: sticky !important;
    top: 0 !important;
    z-index: 900 !important;
    background: rgba(18, 18, 18, 0.92) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    padding-bottom: 8px !important;
    margin-bottom: 12px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}
```

2. No código Python de renderização do topo do chat:
```python
st.markdown('<div class="chat-sticky-header">', unsafe_allow_html=True)
col_title, col_toggle = st.columns([0.70, 0.30])
with col_title:
    st.markdown("### 🎩 Diálogo com Conrad")
    st.caption(f"Gem: **{active_gem_name}** | Modelo: `{st.session_state.engine.model_name}`")
with col_toggle:
    btn_label = "📐 Abrir Lousa" if st.session_state.canvas_collapsed else "✖ Ocultar Lousa"
    if st.button(btn_label, use_container_width=True, help="Alternar visualização da lousa técnica lateral"):
        st.session_state.canvas_collapsed = not st.session_state.canvas_collapsed
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
```
*Resultado:* Mesmo se o chat tiver 50 mensagens, o topo permanece visível com efeito fosco transparente e o botão de abrir/fechar lousa está sempre a 1 clique.

---

### 3.2. Botão "+" de Upload Ancorado ao Floating Dock
1. No Streamlit, inicializar o estado de anexo pendente:
```python
if "pending_upload" not in st.session_state:
    st.session_state.pending_upload = None
```

2. Posicionar o botão `➕` adjacente ao campo de chat através de um container dockado com CSS moderno:
```css
/* Ancoragem do botão '+' de upload diretamente à esquerda da barra de chat */
div[data-testid="stPopover"] {
    position: fixed !important;
    bottom: 24px !important;
    left: calc(21rem + 2rem) !important;
    z-index: 1005 !important;
}
div[data-testid="stPopover"] > button {
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    background-color: #262626 !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    color: #C59B27 !important;
    font-size: 20px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
}
div[data-testid="stPopover"] > button:hover {
    border-color: #C59B27 !important;
    transform: scale(1.05) !important;
}

/* Desloca a barra stChatInput para dar espaço ao botão '+' */
div[data-testid="stChatInput"],
.stChatInput {
    left: calc(21rem + 2rem + 54px) !important;
    width: calc(44% - 54px) !important;
}
```

3. Renderizar o popover com upload e o chip de anexo:
```python
# Popover de Anexo estilo Gemini/Claude
with st.popover("➕", help="Anexar foto de caderno, lista de exercícios ou PDF"):
    st.markdown("**📎 Anexar Material de Estudo**")
    uploaded = st.file_uploader(
        "Selecione um arquivo:",
        type=["png", "jpg", "jpeg", "pdf"],
        key="dock_file_uploader",
        label_visibility="collapsed"
    )
    if uploaded:
        st.session_state.pending_upload = uploaded

# Chip Flutuante de Pré-visualização se houver anexo carregado
if st.session_state.pending_upload:
    chip_name = st.session_state.pending_upload.name
    st.markdown(
        f"""
        <div style="position: fixed; bottom: 82px; left: calc(21rem + 2rem + 54px); z-index: 1002;
                    background: #252525; border: 1px solid #C59B27; border-radius: 16px; padding: 4px 12px;
                    display: flex; align-items: center; gap: 8px; font-size: 12px; color: #f0f0f0; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <span>📎 {html.escape(chip_name)}</span>
            <span style="color: #ff5555; cursor: pointer; font-weight: bold;" onclick="/* Limpar anexo */">✕</span>
        </div>
        """,
        unsafe_allow_html=True
    )
```

4. Ao submeter a mensagem via `st.chat_input`, se `st.session_state.pending_upload` existir, consome os bytes do anexo e reseta para `None`.

---

## 4. Critérios de Aceite & Validação
* [ ] O botão de Abrir/Fechar lousa nunca desaparece, mesmo rolando centenas de pixels no histórico.
* [ ] O bloco invasivo de upload no topo do chat é removido por completo.
* [ ] O botão `+` abre o menu flutuante para anexar imagens ou PDFs.
* [ ] O arquivo anexado aparece como um chip elegante e é enviado junto com o prompt do usuário.
