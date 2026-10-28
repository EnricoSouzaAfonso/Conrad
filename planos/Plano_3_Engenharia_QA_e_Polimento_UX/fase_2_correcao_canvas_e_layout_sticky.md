# 📋 Especificação Técnica de Engenharia — Plano 3: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 3 — Engenharia de QA, Correção de Bugs Críticos e Polimento UX  
**Etapa:** Fase 2 — Arquitetura Visual do Quadro Negro (Canvas) e Input Fixo Inferior (Sticky Bottom)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico dos Problemas de Layout & UX

### 1.1. O Bug do Quadro Negro (Fórmulas renderizadas abaixo do retângulo)
* **Sintoma Relatado:** Ao solicitar uma equação ao Conrad, a fórmula não é exibida dentro da lousa do Quadro Negro; em vez disso, aparece um quadrado preto vazio e as fórmulas renderizam jogadas embaixo dele.
* **Causa Raiz no Código:** Em `app.py`, Argon escreveu:
  ```python
  st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
  if st.session_state.active_artifact:
      st.markdown(art.content) # Fórmulas aqui
  st.markdown('</div>', unsafe_allow_html=True)
  ```
  O Streamlit renderiza cada comando `st.markdown()` dentro de um contêiner DOM independente. Quando o navegador encontra `<div class="canvas-container">` sem fechamento no mesmo bloco, o interpretador HTML **auto-fecha a tag imediatamente**. O resultado é um retângulo escuro vazio de altura mínima e, em seguida, as fórmulas aparecem soltas no DOM, completamente fora da caixa.
* **Solução Canônica:** Utilizar os componentes estruturais nativos do Streamlit (`st.container(border=True)`) com classes CSS injetadas no contêiner pai, garantindo que o cabeçalho, as equações em MathJax, diagramas Mermaid e botões de código fiquem **100% contidos dentro da moldura da lousa**.

### 1.2. Área de Perguntas Desorganizada (Falta de Fixação no Rodapé)
* **Sintoma Relatado:** Conforme a conversa cresce, a área de perguntas desce junto com as mensagens e fica confusa na tela, obrigando o aluno a rolar até o fundo para poder digitar.
* **Solução Canônica (Alinhada ao Modern Web Guidance `css-layout`):**
  - Delimitar um contêiner de mensagens com rolagem independente (`max-height: calc(100dvh - 240px); overflow-y: auto; scrollbar-gutter: stable; overscroll-behavior: contain;`).
  - Fixar o campo de input no rodapé com CSS `position: sticky; bottom: 0; z-index: 100; backdrop-filter: blur(12px);`, idêntico ao padrão dos melhores chats da indústria (ChatGPT, Claude e Perplexity).

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Reestruturar o container do Quadro Negro e aplicar regras CSS de layout sticky e scroll independente).
* **Modificar:** `src/conrad_canvas.py` (Garantir sanitização e renderização íntegra de blocos matemáticos).
* **Modificar:** `CHANGELOG.md` (Registrar versão 2.6.1 — Correção do Canvas e Layout Sticky Bottom).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Reestruturação do Quadro Negro no `app.py`
Substituir a injeção falha de HTML aberto/fechado por contêineres nativos estilizados:

```python
with col_canvas:
    st.subheader("📐 Quadro Negro do Conrad")
    
    # Contêiner nativo com borda integrada — conteúdo 100% encapsulado
    canvas_card = st.container(border=True)
    with canvas_card:
        if st.session_state.active_artifact:
            art = st.session_state.active_artifact
            # Cabeçalho da Lousa com Badge
            st.markdown(
                f"""
                <div style="border-bottom: 2px solid #C59B27; padding-bottom: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 15px; font-weight: bold; color: #f5f5f5;">📌 {art.title}</span>
                    <span style="background: #2A2A2A; border: 1px solid #444; font-size: 11px; padding: 2px 8px; border-radius: 4px; color: #C59B27;">{art.type.upper()}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Renderização interna estritamente DENTRO do container
            if art.type == "math":
                st.markdown(art.content)
            elif art.type == "code":
                st.code(_clean_code_or_mermaid_fence(art.content))
            elif art.type == "mermaid":
                clean_mermaid = _clean_code_or_mermaid_fence(art.content, "mermaid")
                st.markdown(f"```mermaid\n{clean_mermaid}\n```")
            else:
                st.markdown(art.content)
        else:
            st.info("🎩 **O Quadro Negro está limpo.** Conforme você conversar com o Conrad sobre matemática, física ou programação, as fórmulas, diagramas e códigos aparecerão aqui dentro automaticamente!")
```

---

### 3.2. Implementação do Layout Sticky Bottom para a Área de Perguntas
Injetar CSS no topo do `app.py` para travar o input no rodapé e criar rolagem suave nas mensagens:

```python
st.markdown("""
<style>
  /* Contêiner de mensagens com scroll independente e estabilidade */
  .chat-scroll-area {
      max-height: calc(100dvh - 220px);
      overflow-y: auto;
      scrollbar-gutter: stable;
      overscroll-behavior: contain;
      padding-right: 8px;
      margin-bottom: 16px;
  }
  
  /* Barra de perguntas fixa no rodapé com efeito vidro (glassmorphism) */
  .stChatInput {
      position: sticky !important;
      bottom: 0 !important;
      z-index: 999 !important;
      background: rgba(18, 18, 18, 0.85) !important;
      backdrop-filter: blur(12px) !important;
      -webkit-backdrop-filter: blur(12px) !important;
      padding-top: 10px !important;
      padding-bottom: 10px !important;
  }
  
  /* Estilização elegante da moldura do Quadro Negro */
  div[data-testid="stVerticalBlockBorderWrapper"] {
      background-color: #161616 !important;
      border: 1px solid #333333 !important;
      border-radius: 10px !important;
  }
</style>
""", unsafe_allow_html=True)
```

---

## 4. Critério de Validação (Definition of Done)
1. **Fórmulas Rigorosamente Dentro da Lousa:** Ao pedir uma equação (ex: Teorema de Pitágoras ou Integral de Gauss), a fórmula deve renderizar **100% no interior da moldura do Quadro Negro**, sem elementos órfãos embaixo da caixa.
2. **Input Fixo no Rodapé:** Ao rolar uma conversa com 10 ou mais mensagens, a barra de digitação deve permanecer travada no rodapé da tela, sempre pronta para uso.
3. **Rolagem Independente:** O chat rola suavemente sem afetar a posição do Quadro Negro nem causar repuxos de tela (*layout shifts* zero).
4. **Git Commit & Push:** Commitar com a mensagem:  
   `fix(ui): encapsulamento correto do canvas no container e chat input sticky bottom`
