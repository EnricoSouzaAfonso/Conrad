# 📐 Especificação Técnica de Engenharia — Plano 11: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 11 — Polimento de UX: Unificação da Lousa, Selectbox Read-Only e Desativação Instantânea dos Downloads  
**Etapa:** Fase 1 — Unificação e Simplificação dos Botões de Controle da Lousa  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Objetivo da Fase
Eliminar a redundância de botões de controle da lousa lateral ("Quadro Negro do Conrad"), removendo os botões inline duplicados no cabeçalho do chat e no cabeçalho da própria lousa, mantendo **exclusivamente o botão flutuante persistente no canto superior direito do site**.

---

## 2. Diagnóstico Atual

Atualmente existem 3 botões competindo pelo controle da lousa:
1. `canvas_toggle_inline_btn` localizado no cabeçalho do chat (`col_chat`).
2. `canvas_close_col_btn` localizado no topo do container da lousa (`col_canvas`).
3. `canvas_toggle_fixed_btn` botão flutuante persistente com `position: fixed; top: 14px; right: 28px; z-index: 1005`.

Essa duplicidade sobrecarrega visualmente o topo do chat e gera confusão de interface.

---

## 3. Instruções Técnicas Passo a Passo para o Argon

Argon, edite o arquivo [`app.py`](file:///c:/Users/enric/Downloads/ProjetoConrad/app.py) aplicando as seguintes alterações:

### 3.1. Limpeza no Cabeçalho do Chat (`col_chat`)

**Localizar (em torno das linhas 882–891):**
```python
with col_chat:
    col_title, col_toggle = st.columns([0.70, 0.30])
    with col_title:
        st.subheader("🎩 Diálogo com Conrad")
    with col_toggle:
        btn_inline_label = "📐 Abrir Lousa" if st.session_state.canvas_collapsed else "✕ Ocultar Lousa"
        if st.button(btn_inline_label, key="canvas_toggle_inline_btn", use_container_width=True, help="Alternar visualização da lousa técnica lateral"):
            st.session_state.canvas_collapsed = not st.session_state.canvas_collapsed
            st.rerun()
```

**Substituir por:**
```python
with col_chat:
    st.subheader("🎩 Diálogo com Conrad")
```

### 3.2. Limpeza no Cabeçalho da Lousa (`col_canvas`)

**Localizar (em torno das linhas 1126–1135):**
```python
if col_canvas is not None:
    with col_canvas:
        col_c_head, col_c_close = st.columns([0.72, 0.28])
        with col_c_head:
            st.subheader("📐 Quadro Negro do Conrad")
        with col_c_close:
            if st.button("✕ Ocultar", key="canvas_close_col_btn", use_container_width=True, help="Ocultar o Quadro Negro lateral"):
                st.session_state.canvas_collapsed = True
                st.rerun()
```

**Substituir por:**
```python
if col_canvas is not None:
    with col_canvas:
        st.subheader("📐 Quadro Negro do Conrad")
```

### 3.3. Preservação do Botão Flutuante Persistente

O botão flutuante persistente no topo de `app.py` deve ser preservado intacto:
```python
# Botão Flutuante Persistente de Controle da Lousa (Acompanha o Viewport em qualquer nível de scroll)
btn_fixed_label = "📐 Abrir Lousa" if st.session_state.canvas_collapsed else "✖ Ocultar Lousa"
if st.button(btn_fixed_label, key="canvas_toggle_fixed_btn", help="Alternar visualização do Quadro Negro lateral a qualquer momento"):
    st.session_state.canvas_collapsed = not st.session_state.canvas_collapsed
    st.rerun()
```
Ele continuará estilizado com:
```css
.st-key-canvas_toggle_fixed_btn,
div[data-testid="stElementContainer"]:has(.st-key-canvas_toggle_fixed_btn) {
    position: fixed !important;
    top: 14px !important;
    right: 28px !important;
    z-index: 1005 !important;
    width: auto !important;
}
```

---

## 4. Critérios de Aceite
1. O cabeçalho "🎩 Diálogo com Conrad" deve exibir apenas o título limpo, sem nenhum botão ao lado.
2. O cabeçalho "📐 Quadro Negro do Conrad" deve exibir apenas o título limpo, sem o botão "✕ Ocultar".
3. O único botão de controle da lousa visível em toda a tela deve ser o botão flutuante no canto superior direito (`canvas_toggle_fixed_btn`).
4. Ao clicar no botão flutuante, a lousa alterna perfeitamente entre aberta e oculta.
