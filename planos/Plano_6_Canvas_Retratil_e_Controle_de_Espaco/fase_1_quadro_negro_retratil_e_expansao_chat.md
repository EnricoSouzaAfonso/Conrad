# 📋 Especificação Técnica de Engenharia — Plano 6: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 6 — Painel Lateral Retrátil (Collapsible Canvas Drawer) e Otimização de Espaço  
**Etapa:** Fase 1 — Quadro Negro Retrátil (Collapsible Toggle) e Expansão Dinâmica do Chat  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. O Espaço Espremido do Chat (Quadro Negro Estático)
* **Sintoma Relatado pelo Usuário:** O Quadro Negro fica permanentemente fixo na metade direita da tela, mesmo quando está limpo ou quando o estudante está apenas conversando em diálogo reflexivo. Isso espreme o chat em uma coluna central estreita, tornando a leitura desconfortável.
* **O Padrão da Indústria (Claude Artifacts & VS Code):**
  * No Claude (Anthropic), a lousa lateral de artefatos possui um botão de controle no topo (`[ ✕ ]` ou `[ Minimizar ]`). Quando o usuário fecha o artefato, o chat se expande suavemente para ocupar o centro da tela em largura total (`max-width: 820px`), garantindo leitura ampla e confortável.
  * Quando o assistente gera um novo artefato técnico (uma equação complexa ou diagrama), a lousa lateral se abre automaticamente (*auto-reveal*).

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Adicionar estado reativo `st.session_state.canvas_collapsed`, botão de alternância no cabeçalho, auto-abertura em novos artifacts e renderização condicional de colunas `[1.1, 0.9]` vs `[1.0]`).
* **Modificar:** `CHANGELOG.md` (Registrar versão 3.2.0 — Quadro Negro Retrátil e Expansão Dinâmica do Chat).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Gerenciamento de Estado e Auto-Reveal no `app.py`
Inicializar o estado no `st.session_state` e implementar a lógica de expansão:

```python
# 1. Inicialização do estado de visibilidade da lousa
if "canvas_collapsed" not in st.session_state:
    st.session_state.canvas_collapsed = False

# 2. No fluxo de processamento de novas mensagens (quando o Conrad responde):
# Se o Conrad gerou um artifact novo e a lousa estava oculta, abre automaticamente:
if artifact is not None:
    st.session_state.active_artifact = artifact
    st.session_state.canvas_collapsed = False  # Auto-reveal estilo Claude Artifacts
```

---

### 3.2. Renderização Condicional de Layout no `app.py`
Substituir a criação incondicional de duas colunas pela divisão adaptativa:

```python
# Cabeçalho do Chat com botão de alternância do Quadro Negro
col_title, col_toggle = st.columns([0.75, 0.25])
with col_title:
    st.subheader("🎩 Diálogo com Conrad")
with col_toggle:
    btn_label = "📐 Abrir Lousa" if st.session_state.canvas_collapsed else "✖ Ocultar Lousa"
    if st.button(btn_label, use_container_width=True, help="Oculte ou abra o Quadro Negro lateral"):
        st.session_state.canvas_collapsed = not st.session_state.canvas_collapsed
        st.rerun()

# Divisão Adaptativa de Colunas
if st.session_state.canvas_collapsed:
    # MODO EXPANDIDO: Chat ocupa a tela com largura confortável e centralizada
    col_chat = st.container()
    col_canvas = None
else:
    # MODO SPLIT-VIEW: Chat à esquerda e Quadro Negro à direita
    col_chat, col_canvas = st.columns([1.1, 0.9], gap="medium")
```

---

### 3.3. Ajuste Dinâmico do Floating Dock no CSS
Quando o Quadro Negro estiver oculto, a barra flutuante de perguntas deve se centralizar na tela:

```python
# Injeção dinâmica de CSS dependendo do estado do Canvas
if st.session_state.canvas_collapsed:
    st.markdown("""
    <style>
      div[data-testid="stChatInput"] {
          max-width: 760px !important;
          left: calc(50% + 10rem) !important;
          transform: translateX(-50%) !important;
      }
      #jump-to-bottom-btn {
          left: calc(50% + 10rem) !important;
      }
    </style>
    """, unsafe_allow_html=True)
```

---

## 4. Critério de Validação (Definition of Done)
1. **Ocultação e Expansão Manual:** Clicar em "✖ Ocultar Lousa" remove a coluna do Quadro Negro e expande o diálogo do Conrad ocupando o centro da tela com espaçamento generoso.
2. **Auto-Abertura (Auto-Reveal):** Com o Quadro Negro oculto, ao pedir *"Gere a equação da relatividade geral de Einstein"*, o Conrad emite o artifact e o Quadro Negro **se abre sozinho**, exibindo os tensores de Einstein na lousa.
3. **Commit & Push:** Commitar com a mensagem:  
   `feat(ui): implementacao do quadro negro retratil e expansao fluida do chat`
