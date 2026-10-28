# ⚙️ Especificação Técnica de Engenharia — Plano 11: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 11 — Polimento de UX: Unificação da Lousa, Selectbox Read-Only e Desativação Instantânea dos Downloads  
**Etapa:** Fase 2 — Bloqueio de Digitação no Seletor de Modelo e Desativação Instantânea dos Botões de Download  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Objetivos da Fase
1. **Seletor de Modelo Read-Only:** Impedir digitação ou cursor piscante no `st.selectbox` de modelos na barra lateral, transformando-o em um dropdown de pura seleção (sem abrir teclado virtual no mobile e sem aceitar digitação no desktop).
2. **Desativação Instantânea dos Downloads:** Eliminar o delay de ~2 segundos na desativação dos botões "📥 Baixar Resumo (.md)" e "📄 Baixar Caderno (.pdf)", fazendo com que eles sejam bloqueados fisicamente (`disabled` e `pointer-events: none`) no exato milissegundo em que o usuário submete uma mensagem (Enter ou botão Enviar), sem discrepâncias visuais.

---

## 2. Diagnóstico Técnico

### 2.1. O Seletor de Modelos
O componente `st.selectbox` do Streamlit encapsula um componente React BaseWeb contendo um `<input role="combobox">`. Por padrão, esse input aceita digitação para filtrar as opções. Como o catálogo de modelos é fixo e definitivo (5 opções), permitir digitação causa confusão de usabilidade. Torná-lo estritamente `readOnly` via JavaScript e CSS remove o cursor de texto e impede qualquer entrada pelo teclado, preservando 100% da capacidade de clique para abrir o menu de seleção.

### 2.2. O Delay nos Botões de Download
Quando o usuário envia um prompt, o Streamlit inicia uma re-execução do script. No navegador, o Streamlit aplica uma transição de opacidade aos elementos antigos antes de processar o streaming. Porém, o elemento DOM do botão de download continuava fisicamente habilitado para cliques até que a conexão com o servidor completasse a primeira fase de streaming (~2 segundos). Além disso, havia animações CSS com transições que atrasavam a percepção do estado bloqueado.

---

## 3. Instruções Técnicas Passo a Passo para o Argon

Argon, edite o arquivo [`app.py`](file:///c:/Users/enric/Downloads/ProjetoConrad/app.py):

### 3.1. Estilos CSS para o Selectbox e Download Instantâneo

No bloco `<style>` injetado em `app.py`:

1. **Adicionar regra para o Selectbox (ocultar cursor de digitação):**
```css
/* Bloqueio do cursor de digitação no selectbox para experiência de dropdown puro */
div[data-testid="stSelectbox"] input {
    caret-color: transparent !important;
    cursor: pointer !important;
    user-select: none !important;
}
```

2. **Ajustar as regras dos botões de download para resposta imediata sem atraso:**
```css
/* ==============================================================================
   BLINDAGEM E DESATIVAÇÃO INSTANTÂNEA DOS BOTÕES DE DOWNLOAD (ZERO DELAY)
   ============================================================================== */
div[data-testid="stDownloadButton"] button:disabled,
body:has(button[data-testid="stChatInputSubmitButton"]:disabled) div[data-testid="stDownloadButton"] button,
body:has(div[data-testid="stChatInput"] textarea:disabled) div[data-testid="stDownloadButton"] button,
.stApp:has([data-testid="stStatusWidget"]) div[data-testid="stDownloadButton"] button {
    pointer-events: none !important;
    opacity: 0.35 !important;
    cursor: not-allowed !important;
    filter: grayscale(80%) !important;
    transition: none !important; /* Elimina qualquer atraso de transição na desativação */
}
```

### 3.2. Script JavaScript Reativo no Navegador

No bloco `<script>` injetado em `app.py` (linhas 410–428):

Adicionar as seguintes rotinas de controle do DOM:

```javascript
// 1. Bloqueia digitação em todos os inputs de selectbox (Dropdown Puro / Read-Only)
function enforceReadonlySelectboxes() {
  const inputs = document.querySelectorAll('div[data-testid="stSelectbox"] input');
  inputs.forEach(inp => {
    if (!inp.readOnly) {
      inp.readOnly = true;
      inp.setAttribute('readonly', 'readonly');
      inp.style.cursor = 'pointer';
      inp.style.caretColor = 'transparent';
    }
  });
}

// 2. Trava instantânea dos botões de download no milissegundo do envio
function lockDownloadButtonsImmediately() {
  const dlButtons = document.querySelectorAll('div[data-testid="stDownloadButton"] button');
  dlButtons.forEach(btn => {
    btn.disabled = true;
    btn.setAttribute('disabled', 'disabled');
    btn.setAttribute('aria-disabled', 'true');
    btn.style.pointerEvents = 'none';
    btn.style.opacity = '0.35';
    btn.style.cursor = 'not-allowed';
    btn.style.filter = 'grayscale(80%)';
  });
}

// Escuta eventos de submissão do chat (tecla Enter e clique no botão de envio)
document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey && e.target.closest('div[data-testid="stChatInput"]')) {
    lockDownloadButtonsImmediately();
  }
}, true);

document.addEventListener('click', function(e) {
  if (e.target.closest('button[data-testid="stChatInputSubmitButton"]')) {
    lockDownloadButtonsImmediately();
  }
}, true);

// Observador contínuo para manter os selects read-only após re-renderizações do Streamlit
enforceReadonlySelectboxes();
if (window._conradObserver) {
  window._conradObserver.disconnect();
}
window._conradObserver = new MutationObserver(() => {
  enforceReadonlySelectboxes();
  // Se o botão de envio estiver desabilitado (IA gerando), mantém botões de download travados
  const submitBtn = document.querySelector('button[data-testid="stChatInputSubmitButton"]');
  if (submitBtn && submitBtn.disabled) {
    lockDownloadButtonsImmediately();
  }
});
window._conradObserver.observe(document.body, { childList: true, subtree: true });
```

---

## 4. Critérios de Aceite
1. Ao clicar no seletor de "Modelo de IA", o dropdown se abre imediatamente para escolha com clique, mas **nenhum cursor de digitação pisca** e nenhuma tecla altera o texto do campo.
2. No momento em que o usuário digita uma mensagem e pressiona Enter (ou clica na seta de enviar), os botões "📥 Baixar Resumo (.md)" e "📄 Baixar Caderno (.pdf)" ficam **imediatamente escurecidos e fisicamente travados** (clique bloqueado instantaneamente, sem delay de 2 segundos).
3. Ao término da resposta da IA, os botões voltam automaticamente ao estado ativo e funcional.
