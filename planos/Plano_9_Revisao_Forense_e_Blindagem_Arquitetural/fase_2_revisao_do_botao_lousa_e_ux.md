# 📋 Especificação Técnica de Auditoria — Plano 9: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 9 — Dossiê de Auditoria Forense e Revisão Técnica para o Argon  
**Etapa:** Fase 2 — Revisão da Persistência do Botão da Lousa e UX (`app.py`)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Contexto & Diagnóstico da Falha Reportada pelo Usuário

### 1.1. O Erro Relatado
O usuário informou que o botão de abrir/ocultar a lousa (*Quadro Negro*) não mudou em nada e continuou sumindo ao rolar o chat para baixo:
> *"o botão de lousa não mudou em nada, não está acompanhando da forma que pedi... se vc vai conversando toda vez vc tem que subir la no inicio do chat para poder clicar no botão de abrir a lousa, ai fica ruim né."*

### 1.2. Diagnóstico da Causa Raiz
No `app.py`, o Argon havia inserido:
```python
# CÓDIGO ANTERIOR:
st.markdown('<div class="chat-sticky-header"></div>', unsafe_allow_html=True)
col_title, col_toggle = st.columns([0.68, 0.32])
```
E no CSS:
```css
.chat-sticky-header,
div[data-testid="stColumn"]:first-child div[data-testid="stHorizontalBlock"]:first-of-type {
    position: sticky !important;
    top: 0 !important;
}
```
**Por que falhou:** No Streamlit, cada chamada a `st.` (inclusive `st.columns`) é envolvida internamente por um container filho `<div data-testid="stElementContainer">` que possui altura fixa (~45px). No CSS padrão, uma regra `position: sticky` **nunca consegue ultrapassar o container pai imediato**. Assim que o container pai de 45px subiu com a rolagem do chat, o botão subiu e desapareceu junto.

---

## 2. Modificações Exatas Realizadas no `app.py`

Argon, revise as seguintes alterações implementadas no `app.py`:

### 2.1. Botão Flutuante Persistente com `position: fixed`
Para garantir que o botão nunca saia da tela, ele foi transformado em um componente flutuante fixo na viewport (idêntico à solução adotada com sucesso no botão de rolagem `↓` e no popover `+`):

```css
/* Botão Flutuante Persistente para Alternar o Quadro Negro (Acompanha 100% o Viewport) */
.st-key-canvas_toggle_fixed_btn,
div[data-testid="stElementContainer"]:has(.st-key-canvas_toggle_fixed_btn) {
    position: fixed !important;
    top: 18px !important;
    right: 28px !important;
    z-index: 1005 !important;
    width: auto !important;
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
.st-key-canvas_toggle_fixed_btn button:hover {
    border-color: #C59B27 !important;
    color: #C59B27 !important;
    transform: scale(1.05) !important;
}
```

### 2.2. Renderização Nativa do Botão Fixo no Fluxo do Streamlit
Antes da renderização condicional de colunas:
```python
# Botão Flutuante Persistente de Controle da Lousa (Acompanha o Viewport em qualquer nível de scroll)
btn_fixed_label = "📐 Abrir Lousa" if st.session_state.canvas_collapsed else "✖ Ocultar Lousa"
if st.button(btn_fixed_label, key="canvas_toggle_fixed_btn", help="Alternar visualização do Quadro Negro lateral a qualquer momento"):
    st.session_state.canvas_collapsed = not st.session_state.canvas_collapsed
    st.rerun()
```

### 2.3. Botão de Fechar Direto no Quadro Negro (`col_canvas`)
Para complementar a ergonomia, o cabeçalho da lousa lateral agora possui um botão próprio de recolhimento:
```python
if col_canvas is not None:
    with col_canvas:
        col_c_head, col_c_close = st.columns([0.72, 0.28])
        with col_c_head:
            st.subheader("📐 Quadro Negro do Conrad")
        with col_c_close:
            if st.button("✖ Ocultar", key="canvas_close_col_btn", use_container_width=True, help="Ocultar o Quadro Negro lateral"):
                st.session_state.canvas_collapsed = True
                st.rerun()
```

### 2.4. Proteção contra Stale Keys na Sessão
Para evitar quebra de interface caso o navegador do usuário contenha chaves antigas de modelos no `st.session_state`:
```python
if "selected_model_label" not in st.session_state or st.session_state.selected_model_label not in DEFINITIVE_MODELS:
    st.session_state.selected_model_label = list(DEFINITIVE_MODELS.keys())[0]
```

---

## 3. Checklist de Revisão para o Argon
- [ ] Inspecionar `app.py`, `repo/app.py` e `Conrad/app.py`.
- [ ] Confirmar que o seletor CSS `.st-key-canvas_toggle_fixed_btn` está ativo.
- [ ] Abrir o navegador, scrollar o chat para baixo e verificar se o botão `[ 📐 Abrir Lousa / ✖ Ocultar Lousa ]` permanece **visível no canto superior direito a qualquer momento**.
- [ ] Testar clique no botão com a lousa aberta e com a lousa recolhida.
