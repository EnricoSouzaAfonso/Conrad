# 📋 Especificação Técnica de Engenharia — Plano 2: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 2 — Elevação Next-Gen & Arquitetura Comercial de Alto Nível  
**Etapa:** Fase 1 — Interface Split-View com Canvas Interativo (Artifacts do Conrad), CoT Visível e Mermaid Nativo  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Implementar no Conrad o padrão de experiência de usuário mais sofisticado da indústria moderna de IA (inspirado no **Claude Artifacts** e **OpenAI Canvas**): o **"Quadro Negro do Conrad" (Split-View Canvas)**.  
O objetivo é eliminar definitivamente a poluição visual do "pergaminho infinito". O diálogo socrático, caloroso e acolhedor permanece no painel conversacional à esquerda, enquanto todo conteúdo cognitivo denso (fórmulas matemáticas em LaTeX, diagramas conceituais Mermaid, blocos de código e resumos de estudo) é projetado e atualizado dinamicamente em um **painel lateral reativo à direita**. Adicionalmente, incorporar o bloco expansível de **Pensamento Socrático (CoT Visível)** inspirado no DeepSeek-R1 para dar transparência ao método pedagógico.

---

## 2. Arquivos Afetados
* **Criar:** `src/conrad_canvas.py` (Módulo responsável pelo parsing, extração e estruturação de blocos `<conrad_artifact>` e separação entre diálogo conversacional e conteúdo da lousa).
* **Modificar:** `src/conrad_persona.py` (Instruir o Conrad a emitir metatags estruturadas `<conrad_artifact type="math|code|mermaid|summary" title="...">` para conteúdos ricos).
* **Modificar:** `app.py` (Reestruturar a interface para o layout Split-View com 2 colunas dinâmicas: Chat à esquerda e Canvas interativo à direita com abas de visualização).
* **Criar:** `tests/test_canvas_artifacts.py` (Bateria de testes unitários validando a extração correta de artifacts sem quebrar o texto do chat).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 2.2.0 — Lançamento do Conrad Canvas e Split-View).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Especificação do Protocolo de Artifacts nas System Instructions (`src/conrad_persona.py`)
Adicionar às diretrizes de sistema a instrução para segregação de conteúdo denso:

```text
==============================================================================
7. O QUADRO NEGRO DO CONRAD (PROTOCOL DE ARTIFACTS / CANVAS)
==============================================================================
Você possui uma lousa digital interativa lateral chamada "Quadro Negro do Conrad".
Sempre que sua resposta envolver:
1. Uma dedução matemática completa ou sistema de equações em LaTeX.
2. Um bloco substancial de código em qualquer linguagem.
3. Um mapa mental ou fluxograma conceitual em Mermaid.
4. Um resumo estruturado de aula com tópicos e flashcards.

Você NÃO deve despejar esse conteúdo longo diretamente no fluxo de conversa.
Em vez disso, mantenha no chat um diálogo socrático breve e acolhedor (1 a 3 parágrafos) e projete o conteúdo estruturado dentro de uma tag de artifact:

<conrad_artifact type="math|code|mermaid|summary" title="Título do Conceito">
... conteúdo técnico rico aqui ...
</conrad_artifact>

Exemplo de uso:
"Excelente reflexão! Note como a taxa de variação se conecta à inclinação da reta tangente. Projetei a dedução passo a passo no nosso Quadro Negro ao lado para que você visualize cada etapa. O que você nota no limite quando h se aproxima de zero?"

<conrad_artifact type="math" title="Definição Formal de Derivada">
$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$$
Onde:
- $f'(x)$: Taxa de variação instantânea da função no ponto $x$.
- $h$: Incremento infinitesimal na variável independente.
</conrad_artifact>
```

---

### 3.2. Implementação do Motor de Canvas (`src/conrad_canvas.py`)
Criar o parser que intercepta as tags de artifact e entrega os dados limpos para a interface:

```python
"""
Módulo de Gerenciamento do Canvas e Artifacts do Conrad.
"""
import re
from typing import Dict, List, Optional, Tuple

class ConradArtifact:
    def __init__(self, artifact_type: str, title: str, content: str):
        self.type = artifact_type  # 'math', 'code', 'mermaid', 'summary'
        self.title = title
        self.content = content.strip()

class CanvasParser:
    ARTIFACT_REGEX = re.compile(
        r'<conrad_artifact\s+type=["\'](.*?)["\']\s+title=["\'](.*?)["\']>(.*?)</conrad_artifact>',
        re.DOTALL | re.IGNORECASE
    )

    @classmethod
    def parse_message(cls, raw_text: str) -> Tuple[str, Optional[ConradArtifact]]:
        """
        Separa a mensagem conversacional do chat do conteúdo projetado no Canvas.
        Retorna (texto_limpo_do_chat, artifact_encontrado).
        """
        match = cls.ARTIFACT_REGEX.search(raw_text)
        if not match:
            return raw_text.strip(), None

        artifact_type = match.group(1).lower()
        title = match.group(2).strip()
        content = match.group(3).strip()

        # Remove o artifact do texto do chat para manter o chat limpo e conversacional
        clean_chat_text = cls.ARTIFACT_REGEX.sub("", raw_text).strip()
        if not clean_chat_text:
            clean_chat_text = "*(Conteúdo projetado no Quadro Negro ao lado 🎩)*"

        artifact = ConradArtifact(artifact_type=artifact_type, title=title, content=content)
        return clean_chat_text, artifact
```

---

### 3.3. Refatoração da Interface Split-View (`app.py`)
O Argon deve reestruturar a tela principal do Streamlit em um layout moderno de duas colunas balanceadas:

```python
import streamlit as st
from src.conrad_core import ConradEngine
from src.conrad_canvas import CanvasParser
from src.assets.conrad_avatar import CONRAD_AVATAR_SVG

st.set_page_config(page_title="Conrad — Tutor Socrático", page_icon="🎩", layout="wide")

# CSS para Dark Mode e Estilização do Quadro Negro
st.markdown("""
<style>
  .stApp { background-color: #121212; color: #e0e0e0; }
  .canvas-container {
      background-color: #1a1a1a;
      border: 1px solid #333333;
      border-radius: 12px;
      padding: 18px;
      min-height: 520px;
  }
  .canvas-header {
      border-bottom: 2px solid #C59B27;
      padding-bottom: 8px;
      margin-bottom: 14px;
      font-weight: 600;
      color: #f5f5f5;
  }
</style>
""", unsafe_allow_html=True)

# Inicialização de estados
if "active_artifact" not in st.session_state:
    st.session_state.active_artifact = None

# Divisão em Colunas: Coluna Esquerda (Chat Socrático) e Coluna Direita (Canvas / Lousa)
col_chat, col_canvas = st.columns([1.1, 0.9], gap="medium")

with col_chat:
    st.subheader("🎩 Diálogo com Conrad")
    # Renderização das mensagens de chat (apenas diálogo limpo)
    ...
    # Input do aluno
    ...

with col_canvas:
    st.subheader("📐 Quadro Negro do Conrad")
    with st.container():
        st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
        if st.session_state.active_artifact:
            art = st.session_state.active_artifact
            st.markdown(f'<div class="canvas-header">📌 {art.title} ({art.type.upper()})</div>', unsafe_allow_html=True)
            
            if art.type == "math":
                st.markdown(art.content)
            elif art.type == "code":
                st.code(art.content)
            elif art.type == "mermaid":
                # Renderiza diagrama Mermaid nativo
                st.markdown(f"```mermaid\n{art.content}\n```")
            else:
                st.markdown(art.content)
        else:
            st.info("O Quadro Negro está limpo. Conforme o Conrad apresentar fórmulas, diagramas ou códigos, eles aparecerão aqui automaticamente!")
        st.markdown('</div>', unsafe_allow_html=True)
```

---

### 3.4. Pensamento Pedagógico Visível (CoT - Chain of Thought)
Ao receber a resposta do Gemini 3.8 Flash, se houver blocos delimitados por pensamentos ou raciocínio interno, renderizá-los dentro de um componente expansível discreto no topo da mensagem:
```python
with st.expander("🧠 Raciocínio Pedagógico do Conrad (Estratégia Socrática)", expanded=False):
    st.caption("O Conrad avaliou o nível conceitual da sua dúvida e selecionou pistas indutivas em vez de respostas prontas.")
```

---

## 4. Critério de Validação (Definition of Done)
1. **Layout Split-View Operacional:** A tela se divide harmoniosamente em duas colunas sem sobreposição ou rolagem horizontal.
2. **Segregação Perfeita de Conteúdo:** Ao perguntar *"Como funciona a equação de Bernoulli em hidrodinâmica?"*, o chat à esquerda exibe apenas o diálogo estimulante do Conrad, enquanto a dedução matemática e a fórmula são projetadas no Canvas à direita com MathJax nítido.
3. **Suporte a Diagramas Mermaid:** Um artifact do tipo `mermaid` renderiza graficamente o diagrama sem falhas de sintaxe.
4. **Resiliência a Mensagens Normais:** Conversas puramente conceituais sem fórmulas continuam fluindo no chat sem afetar o Canvas.
5. **Suíte de Testes Aprovada:** O script `tests/test_canvas_artifacts.py` roda e valida a extração das tags com 100% de sucesso.
6. **Git Commit & Push:** Commitar com a mensagem padronizada:  
   `feat(canvas): implementacao do split-view com quadro negro reativo e protocolo de artifacts`
