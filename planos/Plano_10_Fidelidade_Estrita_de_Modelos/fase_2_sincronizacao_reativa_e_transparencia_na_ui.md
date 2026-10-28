# 📋 Especificação Técnica de Engenharia — Plano 10: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 10 — Fidelidade Estrita de Modelos e Eliminação de Substituições Silenciosas  
**Etapa:** Fase 2 — Sincronização Reativa e Transparência de Modelo na UI (`app.py`)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Diagnóstico e Requisitos de Interface

### 1.1. O Problema
Na interface web, o usuário seleciona um modelo na barra lateral (ex: `Gemini 3.8 Flash`), mas se a re-instanciação do chat não for forçada com `st.rerun()`, ou se o estado `selected_model_label` não sincronizar perfeitamente com a instância `st.session_state.engine.model_name`, pode haver descompasso entre o que o selectbox mostra e o que o motor de chat está usando.

### 1.2. Requisitos de Transparência
* O modelo selecionado deve ser reativo: alterou no selectbox $\rightarrow$ re-instancia imediatamente o chat com o novo model ID e executa `st.rerun()`.
* O cabeçalho do chat deve exibir de forma clara e visível o modelo real em uso: `Modelo: gemini-3.8-flash`.
* A barra lateral deve exibir o badge de confirmação do modelo conectado.

---

## 2. Instruções Técnicas Passo a Passo para o Argon

Argon, revise e aplique as seguintes instruções no arquivo `app.py` (e replique em `repo/app.py` e `Conrad/app.py`):

### 2.1. Reatividade Imediata no Seletor de Modelos da Sidebar
No bloco `with st.sidebar:` em `app.py`:

```python
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
```

---

### 2.2. Transparência no Cabeçalho do Chat
No topo da coluna de chat (`with col_chat:`), garantir que a legenda identifique sem ambiguidades o modelo ativo:

```python
    st.caption(
        f"Gem: **{active_gem_data['name']}** | Modelo Ativo: `{st.session_state.engine.model_name}`"
    )
```

---

### 2.3. Inicialização e Reset na "Nova Conversa"
No botão `🔄 Nova Conversa`:
```python
    if st.button("🔄 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_artifact = None
        st.session_state.cached_tokens = 0
        if st.session_state.engine.api_key:
            # Garante que o novo chat use estritamente o modelo configurado
            st.session_state.engine.set_model(st.session_state.engine.model_name)
        st.rerun()
```

---

## 3. Checklist de Validação para o Argon
- [ ] No navegador, alterar o modelo no selectbox para `Gemini 3.5 Flash`.
- [ ] Confirmar que o toast surge e que a legenda abaixo do título do chat muda para `Modelo Ativo: gemini-3.5-flash`.
- [ ] Alterar de volta para `Gemini 3.8 Flash`.
- [ ] Confirmar que a legenda muda imediatamente para `Modelo Ativo: gemini-3.8-flash`.
- [ ] Enviar mensagem e validar que a requisição é feita no modelo exibido.
