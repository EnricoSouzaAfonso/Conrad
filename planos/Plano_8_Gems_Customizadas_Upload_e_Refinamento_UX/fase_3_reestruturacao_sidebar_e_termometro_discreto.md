# 📋 Especificação Técnica de Engenharia — Plano 8: Fase 3
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 8 — Gems Pedagógicas Customizáveis, Upload Integrado e Refinamento de UX/UI  
**Etapa:** Fase 3 — Reestruturação Ergonômica da Sidebar e Termômetro de Retenção Discreto  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. Ordem Imediata de Acesso (Onboarding BYOK)
* **Sintoma:** O usuário novo entra no Conrad e precisa configurar sua chave de API para começar a falar com a IA. Atualmente, a chave está na metade inferior da sidebar, abaixo dos Modos Pedagógicos, Modelos e Perfil Cognitivo.
* **Ordem Solicitada pelo Usuário:**
  1. Chave de API Gemini (com tutorial imediato no topo);
  2. Modelo de IA;
  3. Modo Pedagógico / Gems;
  4. Perfil de Aprendizado;
  5. Métricas e Termômetro de Retenção (discreto);
  6. Nova Conversa.

### 1.2. O Termômetro de Retenção Intrínseco
* **Sintoma:** O termômetro de retenção ocupa muito espaço vertical estático na sidebar com textos explicativos longos que distraem o estudante durante o estudo fluído.
* **Solução de Design:**
  * Transformar o termômetro em um **micro-componente minimalista** (uma barra fina e elegante ou badge compacto com tooltip nativo em hover).
  * Ao passar o mouse por cima do badge ou da barrinha, exibe uma janela flutuante com o diagnóstico do tema ativo e o nível de retenção:
    * *"Tema Ativo: [Identificado na Conversa]"*
    * *"Retenção: 85% — Conceitos consolidados através de prática ativa"*
  * O termômetro mantém a inteligência de avaliação do `CognitiveRetentionTracker`, mas sem poluir a experiência visual.

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Reorganizar todo o bloco `with st.sidebar:`, aplicar classes CSS para o micro-termômetro com hover tooltip).
* **Modificar:** `src/conrad_analytics.py` (Adicionar inferência/resumo de tema corrente para exibição no tooltip).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Reordenação Estrita da Sidebar no `app.py`
A estrutura do `with st.sidebar:` deve seguir rigorosamente a nova ordem lógica:

```python
with st.sidebar:
    # 0. Cabeçalho Oficial
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;'>{CONRAD_AVATAR_SVG} <h3 style='margin:0;'>Configurações</h3></div>",
        unsafe_allow_html=True,
    )
    st.caption("Personalize sua chave de acesso, motor cognitivo e estilo de tutoria.")

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
            st.markdown("<div style='color:#4caf50;font-size:12px;margin-top:8px;'>● Conectado</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#ff9800;font-size:12px;margin-top:8px;'>○ Aguardando</div>", unsafe_allow_html=True)

    with st.expander("📘 Como Obter sua Chave Gratuita", expanded=not bool(st.session_state.engine.api_key)):
        st.markdown(
            """
            1. Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey) e faça login.
            2. Clique no botão azul **"Create API Key"**.
            3. Cole a chave (`AIza...`) acima e clique em **"Salvar Chave"**.
            
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
    # Lógica de troca de modelo...

    st.divider()

    # =========================================================================
    # 3. MODO PEDAGÓGICO / GEMS DINÂMICAS (CRUD)
    # =========================================================================
    st.markdown("#### 💎 Gem Pedagógica Ativa")
    # Selectbox dinâmico carregando do banco SQLite + Expander com CRUD de Gems...

    st.divider()

    # =========================================================================
    # 4. MEMÓRIA PEDAGÓGICA (PERFIL COGNITIVO NEUTRO)
    # =========================================================================
    with st.expander("🧠 Perfil de Aprendizado (Memória do Aluno)", expanded=False):
        # Campos atualizáveis e botão de reset multidisciplinar...

    st.divider()

    # =========================================================================
    # 5. RETENÇÃO DISCRETA (HOVER TOOLTIP) & UTILS
    # =========================================================================
    stats = CognitiveRetentionTracker.evaluate_session(st.session_state.messages)
    # Renderização da barra compacta com Tooltip CSS (ver seção 3.2)

    # 6. Botão Nova Conversa
    if st.button("🔄 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_artifact = None
        st.session_state.cached_tokens = 0
        if st.session_state.engine.api_key:
            st.session_state.engine._init_chat()
        st.rerun()
```

---

### 3.2. Micro-Componente de Retenção com Tooltip CSS
Implementar uma barra discreta com dados no atributo `title` nativo ou micro-popover estilizado:

```python
retention_score = int(stats.get("score", 0))
retention_status = stats.get("status", "Iniciando")
retention_feedback = html.escape(stats.get("feedback", "Explore novos temas com o tutor."))

st.markdown(
    f"""
    <div style="margin-bottom: 12px;" title="Retenção Estimada: {retention_score}%\nNível: {retention_status}\nDiagnóstico: {retention_feedback}">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; font-size:12px; color:#aaa;">
        <span>🌡️ Retenção do Tema</span>
        <span style="font-weight:bold; color:#C59B27;">{retention_score}%</span>
      </div>
      <div style="background:#262626; border-radius:4px; height:6px; width:100%; overflow:hidden;">
        <div style="background: linear-gradient(90deg, #C59B27, #4caf50); height:100%; width:{max(5, retention_score)}%; transition: width 0.4s ease;"></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
```

---

## 4. Critérios de Aceite & Validação
* [ ] A Chave API e o tutorial estão no topo imediato da sidebar.
* [ ] O Termômetro de Retenção não ocupa blocos verticais invasivos; apresenta barra compacta de 6px com tooltip informativo ao passar o mouse.
* [ ] A ordem visual segue 100% o padrão especificado.
