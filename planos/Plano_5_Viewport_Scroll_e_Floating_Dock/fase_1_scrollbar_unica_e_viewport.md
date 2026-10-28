# 📋 Especificação Técnica de Engenharia — Plano 5: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 5 — Viewport de Alta Precisão, Scrollbar Unificada e Floating Input Dock  
**Etapa:** Fase 1 — Extinção da Barra Dupla de Rolagem e Scrollbar Unificada Padrão Big Tech  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. O Bug da Barra Dupla de Rolagem (Double Scrollbar)
* **Sintoma Visual Relatado:** Na interface atual do Conrad (visível nas capturas de tela), o usuário se depara com **duas barras de rolagem verticais paralelas** na mesma tela: uma rola a janela inteira e a outra rola o bloco de mensagens. Ao tentar rolar com o mouse, a página engasga, o cabeçalho desaparece e a experiência fica truncada.
* **Comparativo com a Indústria (Gemini, Claude e Grok):**
  * Conforme evidenciado nas capturas de referência enviadas por Enrico:
    * **Google Gemini:** Exibe rigorosamente **apenas uma barra de scroll lateral**, limpa e integrada.
    * **Claude (Anthropic):** Utiliza um container de 100dvh onde a conversa rola em trilha única com `scrollbar-gutter: stable`.
    * **Grok (xAI):** Possui rolagem única vertical centralizada, mantendo a janela sem repuxos.
* **Causa Raiz Técnica no Streamlit:**
  Por padrão, o Streamlit injeta `overflow: auto` no elemento raiz `.main` ou `.stApp`. Quando adicionamos classes com `overflow-y: auto` dentro da coluna de chat (`.chat-scroll-area`), o navegador cria dois contextos de rolagem aninhados (*nested scroll containers*). O resultado são duas barras concorrentes no desktop.

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Remover os wrappers de scroll conflitantes e aplicar as regras CSS de contenção de rolagem unificada com `100dvh`).
* **Modificar:** `CHANGELOG.md` (Registrar versão 3.1.0 — Scrollbar Unificada e Correção de Viewport).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Reset de Viewport e Desativação do Scroll Duplo no `app.py`
O Argon deve injetar no bloco `<style>` do `app.py` o reset estrutural que unifica a rolagem:

```css
/* ==============================================================================
   RESET DE VIEWPORT E UNIFICAÇÃO DE SCROLLBAR (PADRÃO GEMINI / CLAUDE)
   ============================================================================== */

/* 1. Trava a raiz para evitar scroll duplo no body da página */
html, body, [data-testid="stAppViewContainer"] {
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
    height: calc(100dvh - 90px) !important;
    overflow-y: auto !important;
    scrollbar-gutter: stable !important;
    overscroll-behavior: contain !important;
    padding-right: 12px !important;
    padding-bottom: 140px !important; /* Espaço reservado para o Floating Dock */
}

/* 4. Coluna do Quadro Negro: Altura proporcional e scroll independente */
div[data-testid="stColumn"]:last-child {
    height: calc(100dvh - 90px) !important;
    overflow-y: auto !important;
    scrollbar-gutter: stable !important;
    overscroll-behavior: contain !important;
    padding-right: 8px !important;
}

/* 5. Customização da Scrollbar (Ultra-fina, elegante e discreta) */
::-webkit-scrollbar {
    width: 6px !important;
    height: 6px !important;
}
::-webkit-scrollbar-track {
    background: transparent !important;
}
::-webkit-scrollbar-thumb {
    background: #333333 !important;
    border-radius: 4px !important;
}
::-webkit-scrollbar-thumb:hover {
    background: #555555 !important;
}
```

---

## 4. Critério de Validação (Definition of Done)
1. **Extinção da Barra Dupla:** Ao abrir o site no navegador (desktop ou notebook), o usuário deve visualizar **rigorosamente apenas UMA barra de scroll** na coluna do chat e **UMA barra de scroll** na lousa do Quadro Negro caso o conteúdo ultrapasse a altura da tela.
2. **Janela Estável:** Rolar com o mouse ou trackpad não deve causar "pulos" ou rolar a barra do navegador.
3. **Commit & Push:** Commitar com a mensagem padronizada:  
   `fix(layout): eliminacao de scrollbar dupla e unificacao de viewport 100dvh`
