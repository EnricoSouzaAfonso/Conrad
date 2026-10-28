# 📋 Especificação Técnica de Engenharia — Fase 5
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Etapa:** Fase 5 — Upgrade para Gemini 3.8 Flash, Seletor de Modelos Definitivos, Onboarding BYOK e Recursos Pedagógicos Web  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Modernizar o motor cognitivo do Conrad adotando o modelo de ponta **Gemini 3.8 Flash** como padrão (1M tokens de contexto e raciocínio de alta velocidade), implementar um seletor dinâmico de **modelos de IA definitivos e estáveis**, construir um fluxo completo de **Onboarding & BYOK (Bring Your Own Key)** com tutorial interativo integrado no site, tratamento gracioso para usuários sem chave (resposta pré-programada da persona da Cartola 🎩) e incorporar novos recursos tecnológicos essenciais (renderização de diagramas Mermaid, métricas de tokens no web app, botão de nova conversa e exportação de resumo de estudos em Markdown).

---

## 2. Arquivos Afetados
* **Modificar:** `src/conrad_core.py` (Atualizar modelo padrão para `gemini-3.8-flash`, flexibilizar inicialização sem chave imediata com validação lazy, e adicionar lista curada de modelos suportados).
* **Modificar:** `src/conrad_persona.py` (Adicionar mensagem pré-programada oficial da Cartola para ausência de API Key e instruções para geração de diagramas conceituais Mermaid).
* **Modificar:** `app.py` (Interface Streamlit com: seletor de modelos no sidebar, input de API Key com validação em tempo real, tutorial visual expansível do Google AI Studio, alerta gracioso no chat, contador de tokens e botão de exportar histórico).
* **Modificar:** `Conrad.ipynb` (Atualizar variável de modelo padrão na Célula 2).
* **Modificar:** `tests/test_persona_and_rules.py` (Adicionar testes para a resposta pré-programada e validação de chaves).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 2.1.0 — Upgrade Gemini 3.8 Flash, Seletor de Modelos, Onboarding BYOK e Mermaid).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Atualização do Motor e Modelos Suportados (`src/conrad_core.py`)
O Argon deve atualizar o `ConradEngine` com a lista curada de modelos definitivos e suporte a validação de chave:

```python
# Lista oficial de modelos definitivos (sem previews temporários que expiram)
DEFINITIVE_MODELS = {
    "Gemini 3.8 Flash (Padrão — Rápido, 1M Tokens)": "gemini-3.8-flash",
    "Gemini 2.5 Flash (Estável)": "gemini-2.5-flash",
    "Gemini 2.5 Pro (Raciocínio Profundo & Exatas)": "gemini-2.5-pro",
    "Gemini 1.5 Flash (Legado Estável)": "gemini-1.5-flash",
    "Gemini 1.5 Pro (Legado Pro)": "gemini-1.5-pro",
}

DEFAULT_MODEL_NAME = "gemini-3.8-flash"

class ConradEngine:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_MODEL_NAME,
        system_instruction: Optional[str] = None
    ):
        self.api_key = api_key or self._resolve_api_key()
        self.model_name = model_name
        self.system_instruction = system_instruction or get_system_instruction()
        self.client = None
        self.chat = None

        if self.api_key:
            self._init_client_and_chat()

    def set_api_key(self, new_key: str):
        """Atualiza a chave de API e reinicializa o cliente e a sessão de chat."""
        self.api_key = new_key.strip()
        self._init_client_and_chat()

    def set_model(self, model_name: str):
        """Altera o modelo e preserva as configurações do chat."""
        self.model_name = model_name
        if self.api_key:
            self._init_chat()

    def validate_api_key(self) -> bool:
        """Testa se a chave atual é válida realizando uma requisição mínima de teste."""
        if not self.api_key:
            return False
        try:
            test_client = genai.Client(api_key=self.api_key)
            test_res = test_client.models.generate_content(
                model=self.model_name,
                contents="ping"
            )
            return bool(test_res)
        except Exception:
            return False

    def _init_client_and_chat(self):
        self.client = genai.Client(api_key=self.api_key)
        self._init_chat()
```

---

### 3.2. Mensagem Pré-Programada da Persona (`src/conrad_persona.py`)
Adicionar em `src/conrad_persona.py` a resposta amigável e educativa para quando o usuário tentar conversar sem ter fornecido uma chave de API:

```python
MSG_CONRAD_SEM_API_KEY = """
Olá! Eu sou o **Conrad** 🎩, seu assistente pessoal de estudos!

Para que possamos começar a explorar o conhecimento juntos, você precisa apenas informar a sua chave de API gratuita do **Google Gemini**.

É um processo **100% gratuito**, oficial do Google e leva menos de 1 minuto!
👉 **Dê uma olhada no menu à esquerda**: você encontrará um tutorial passo a passo explicando onde pegar sua chave e como salvá-la aqui no site.

Assim que você inserir sua chave, estarei pronto para guiá-lo em qualquer dúvida, cálculo ou desafio de programação! 📚
"""

def get_missing_key_message() -> str:
    return MSG_CONRAD_SEM_API_KEY.strip()
```

E adicionar nas `SYSTEM_INSTRUCTION_CONRAD` o suporte a diagramas conceituais:
```text
==============================================================================
6. DIAGRAMAS E MAPAS MENTAIS (MERMAID)
==============================================================================
Quando julgar benéfico para o modelo mental do aluno (ex: fluxos lógicos, árvores genealógicas de conceitos, arquiteturas ou ciclos de processos), você pode gerar diagramas usando blocos de código com a tag 'mermaid' (ex: ```mermaid ... ```).
Mantenha os diagramas legíveis, compactos e com rótulos explicativos.
```

---

### 3.3. Refatoração Completa da Interface Autônoma (`app.py`)
O Argon deve reconstruir o `app.py` integrando:
1. **Sidebar com Seletor de Modelos Definitivos:** Selectbox com `DEFINITIVE_MODELS`.
2. **Área de Gerenciamento da API Key:**
   - Input tipo senha (`st.sidebar.text_input(..., type="password")`).
   - Botão "Salvar e Validar Chave" que roda `engine.validate_api_key()`.
   - Feedback visual: ✅ "Chave válida e ativa!" ou ❌ "Chave inválida. Verifique os caracteres."
3. **Tutorial Interativo (Expander no Sidebar):**
   - Passo 1: Link direto para [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Passo 2: Clique em **"Create API Key"**.
   - Passo 3: Copie e cole no campo acima.
   - Dica: Ressaltar que o Google oferece cota gratuita para uso pessoal e estudantil.
4. **Alerta Gracioso no Chat:**
   - Se o usuário enviar uma mensagem sem chave cadastrada, o app adiciona a mensagem do usuário e em seguida renderiza `get_missing_key_message()` com o avatar da Cartola 🎩, sem disparar erros de sistema ou quebrar a tela.
5. **Métricas de Tokens e Utilitários:**
   - Exibir contador de tokens consumidos na sessão (`engine.count_tokens()`).
   - Botão **"Nova Conversa"** (limpa `st.session_state.messages` e reinicia o chat).
   - Botão **"Baixar Resumo de Estudos"** (permite download do histórico em `.md`).

---

### 3.4. Refatoração do `Conrad.ipynb`
Na Célula 2 de `Conrad.ipynb`:
Atualizar o modelo padrão de fallback para `gemini-3.8-flash`.

---

## 4. Critério de Validação (Definition of Done)
1. **Padrão Gemini 3.8 Flash:** A inicialização padrão do motor usa `gemini-3.8-flash` sem erros.
2. **Seletor de Modelos Operacional:** No Streamlit, trocar o selectbox para `Gemini 2.5 Pro` ou `Gemini 2.5 Flash` atualiza o motor sem perder o histórico do chat.
3. **Comportamento Sem Chave (Zero Crash):**
   - Iniciar o app sem nenhuma variável de ambiente ou `.env`.
   - Digitar *"Olá, Conrad"* no chat input.
   - O Conrad deve responder suavemente com a mensagem `MSG_CONRAD_SEM_API_KEY` instruindo o usuário a olhar o tutorial no menu lateral, sem gerar tracebacks no terminal.
4. **Validação de Chave BYOK:**
   - Inserir uma chave válida no campo da sidebar e clicar em "Validar": a interface confirma sucesso.
   - Próxima mensagem enviada gera streaming real com a persona socrática.
5. **Tutorial Visual Presente:** O expander "📘 Como Obter sua Chave Gratuita" está visível, com links clicáveis e instruções claras.
6. **Git Commit & Push:** Commitar com a mensagem padronizada:  
   `feat(app): upgrade gemini-3.8-flash, seletor de modelos, onboarding BYOK e tutorial`
