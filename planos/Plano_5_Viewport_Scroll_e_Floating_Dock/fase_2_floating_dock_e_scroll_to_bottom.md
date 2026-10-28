# 📋 Especificação Técnica de Engenharia — Plano 5: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 5 — Viewport de Alta Precisão, Scrollbar Unificada e Floating Input Dock  
**Etapa:** Fase 2 — Floating Input Dock (Barra Flutuante Fixa no Rodapé) e Botão Scroll-to-Bottom  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. A Área de Digitação que Foge da Tela (Input Empurrado para Baixo)
* **Sintoma Relatado pelo Usuário:** No Conrad atual, toda vez que o assistente envia uma resposta (ex: a explicação de Lavoisier), a área de digitação desce junto com o texto e **some da tela**. O usuário é obrigado a rolar a página inteira até o fundo toda vez que deseja fazer uma nova pergunta ou continuar a conversa.
* **O Padrão da Indústria (Gemini, Claude e Grok):**
  * Conforme as 3 imagens de referência fornecidas:
    * **Google Gemini (Imagem 1):** A barra de digitação fica permanentemente ancorada e flutuando no rodapé da janela (`floating pill dock`), centralizada, com cantos arredondados e fundo translúcido escuro (`backdrop-filter`). As mensagens fluem e rolam suavemente por trás dela.
    * **Claude (Imagem 4):** A caixa de texto é fixa no rodapé; o usuário pode rolar a tela inteira para cima para ler a explicação e a barra permanece exatamente no mesmo lugar, pronta para receber a próxima mensagem.
    * **Grok (Imagem 3):** Barra flutuante tipo cápsula com cantos ovais no rodapé, sem jamais sair do viewport.
* **Causa Raiz Técnica no Streamlit:**
  Argon chamou `st.chat_input()` dentro da coluna de layout (`with col_chat:`). O Streamlit trata essa chamada como um elemento comum de fluxo em bloco, fazendo o input ser renderizado no final do conteúdo de mensagens. Conforme novas mensagens são injetadas, a caixa é empurrada para fora do viewport visível.

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Mover `st.chat_input` para fora do fluxo descendente, estilizá-lo como Floating Dock e implementar o botão flutuante de scroll-to-bottom).
* **Modificar:** `CHANGELOG.md` (Registrar versão 3.1.1 — Floating Input Dock e Botão Scroll-to-Bottom).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Estilização do Floating Dock no `app.py`
O Argon deve transformar o contêiner do `st.chat_input` em uma barra flutuante elegante que permanece fixa no rodapé da tela, alinhada à coluna de diálogo:

```css
/* ==============================================================================
   FLOATING INPUT DOCK ESTILO GEMINI / CLAUDE / GROK
   ============================================================================== */

/* 1. Fixa a barra de input permanentemente no rodapé da tela */
div[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 24px !important;
    z-index: 1000 !important;
    max-width: 54% !important; /* Proporcional à coluna de chat */
    left: calc(21rem + 2rem) !important; /* Alinhado após a Sidebar */
    background: rgba(22, 22, 22, 0.85) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 28px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    padding: 4px 10px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

/* 2. Destaque ao focar no campo de digitação */
div[data-testid="stChatInput"]:focus-within {
    border-color: #C59B27 !important;
    box-shadow: 0 10px 35px rgba(197, 155, 39, 0.25) !important;
}

/* 3. Ajuste responsivo caso a sidebar esteja colapsada */
@media (max-width: 1024px) {
    div[data-testid="stChatInput"] {
        max-width: 90% !important;
        left: 5% !important;
    }
}

/* 4. Espaçamento de segurança no final do chat (Garante que a última mensagem não seja coberta) */
.chat-bottom-spacer {
    height: 120px !important;
    width: 100% !important;
    clear: both !important;
}
```

---

### 3.2. Implementação do Botão Flutuante "Rolar para o Fim" (↓)
Assim como visto na imagem do Google Gemini (Imagem 1), incluir uma âncora e um botão flutuante circular logo acima da barra de digitação para permitir retorno imediato à mensagem mais recente quando o usuário estiver rolando mensagens anteriores:

```python
# No app.py, injetar o script leve de retorno ao fim do chat:
st.markdown("""
<div id="chat-bottom-anchor" class="chat-bottom-spacer"></div>

<button id="jump-to-bottom-btn" title="Rolar para as mensagens recentes" onclick="
    const chatCol = document.querySelector('div[data-testid=\"stColumn\"]:first-child');
    if (chatCol) {
        chatCol.scrollTo({ top: chatCol.scrollHeight, behavior: 'smooth' });
    }
">
    ↓
</button>

<style>
#jump-to-bottom-btn {
    position: fixed;
    bottom: 95px;
    left: calc(21rem + 2rem + 25%);
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
""", unsafe_allow_html=True)
```

---

## 4. Critério de Validação (Definition of Done)
1. **Área de Digitação Imóvel:**
   - Enviar uma mensagem e esperar o Conrad responder uma explicação longa (como a da conservação de massas de Lavoisier).
   - A barra de digitação DEVE permanecer **estática e perfeitamente ancorada no rodapé da janela**, sem descer nem se mover 1 pixel.
2. **Leitura Desimpedida:**
   - O usuário pode rolar para cima para ler o histórico antigo enquanto a barra continua no rodapé, permitindo digitar a resposta a qualquer momento.
3. **Visibilidade da Última Mensagem:**
   - Rolar até o fundo deve exibir o último parágrafo da resposta do Conrad com folga visual acima da barra flutuante (graças ao `chat-bottom-spacer`).
4. **Botão de Salto Operacional:**
   - Clicar no botão `↓` rola a coluna de chat suavemente de volta até a última mensagem recebida.
5. **Commit & Push:** Commitar com a mensagem:  
   `feat(ui): implementacao de floating input dock estilo gemini/claude e botao scroll-to-bottom`
