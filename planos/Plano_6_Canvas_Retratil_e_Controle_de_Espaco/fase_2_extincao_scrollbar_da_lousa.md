# 📋 Especificação Técnica de Engenharia — Plano 6: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 6 — Painel Lateral Retrátil (Collapsible Canvas Drawer) e Otimização de Espaço  
**Etapa:** Fase 2 — Extinção da Scrollbar Dupla e Altura Auto-Ajustável da Lousa  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. A Scrollbar Concorrente no Quadro Negro
* **Sintoma Relatado pelo Usuário:** Mesmo quando o Quadro Negro está limpo (apenas com o aviso azul informativo) ou com uma equação simples, uma barra de rolagem vertical fica visível e ativa na lateral da lousa. O usuário fica olhando para duas barras cinzas competindo no meio da interface.
* **Causa Raiz Técnica no CSS do `app.py`:**
  Na Fase anterior, aplicou-se `div[data-testid="stColumn"]:last-child { overflow-y: auto !important; height: calc(100dvh - 90px) !important; }`. Ao forçar altura fixa com `overflow-y: auto`, o navegador desenha a calha da scrollbar na coluna direita, mesmo quando o conteúdo cabe com folga na tela.
* **Solução Canônica:**
  - A coluna da direita não deve ser um container de scroll rígido permanente.
  - O card do Quadro Negro (`canvas_card`) deve se auto-ajustar ao conteúdo até um limite máximo (`max-height: calc(100dvh - 180px); overflow-y: auto;`), e sua barra de rolagem deve ser estilizada com `scrollbar-width: none;` (ou visível estritamente em *hover* quando houver dedução longa), mantendo a tela **com apenas UMA barra visível (a do chat)**.

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Substituir o scroll forçado da coluna direita por rolagem interna em hover no card do Canvas).
* **Modificar:** `CHANGELOG.md` (Registrar versão 3.2.1 — Otimização de Scroll da Lousa e Eliminação de Calha Dupla).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Ajuste do CSS no `app.py`
Substituir a regra rígida da coluna direita por contenção suave com barra invisível por padrão:

```css
/* ==============================================================================
   REMOÇÃO DA SCROLLBAR DUPLA NA COLUNA DO QUADRO NEGRO
   ============================================================================== */

/* 1. Coluna direita não força scrollbar permanente */
div[data-testid="stColumn"]:last-child {
    height: auto !important;
    max-height: calc(100dvh - 90px) !important;
    overflow: visible !important;
    padding-right: 4px !important;
}

/* 2. O Card do Quadro Negro só rola se a dedução for muito longa, com barra discreta */
div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlockBorderWrapper"] {
    max-height: calc(100dvh - 160px) !important;
    overflow-y: auto !important;
    scrollbar-gutter: stable !important;
    scrollbar-width: thin !important;
    scrollbar-color: transparent transparent !important; /* Invisível por padrão */
    transition: scrollbar-color 0.2s ease !important;
}

/* 3. A barra da lousa só ganha cor sutil quando o usuário passar o mouse por cima dela */
div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    scrollbar-color: #444444 transparent !important;
}
```

---

## 4. Critério de Validação (Definition of Done)
1. **Zero Calha Concorrente:** Ao carregar o site com o Quadro Negro limpo, **nenhuma barra de rolagem cinza** deve ser visível na metade direita da tela.
2. **Rolagem Suave Apenas em Deduções Extensas:** Caso uma dedução matemática tenha 30 linhas, o card da lousa permite rolar o conteúdo internamente sem quebrar a posição dos botões de download.
3. **Commit & Push:** Commitar com a mensagem:  
   `fix(ui): remocao da scrollbar rigida no quadro negro e estilizacao em hover`
