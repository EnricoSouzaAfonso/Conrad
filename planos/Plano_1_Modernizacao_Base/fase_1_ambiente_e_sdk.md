# 📋 Especificação Técnica de Engenharia — Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Etapa:** Fase 1 — Modernização do SDK do Gemini, Autenticação Híbrida e Desacoplamento do Core  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Eliminar a dependência do pacote legado `google-generativeai`, migrar integralmente para o SDK oficial e atualizado `google-genai` (v1.x), garantir compatibilidade com os modelos atuais (ex: `gemini-2.5-flash`), flexibilizar a autenticação para aceitar tanto Colab Secrets quanto variáveis de ambiente locais (`GEMINI_API_KEY` / `GOOGLE_API_KEY`), e desacoplar o motor conversacional do Conrad em um módulo Python limpo (`src/conrad_core.py`), permitindo testes e execução fora do notebook.

---

## 2. Arquivos Afetados
* **Criar:** `src/__init__.py`
* **Criar:** `src/conrad_core.py` (Módulo com o cliente da API, gerenciamento de sessão de chat, contagem de tokens e tratamento de safety).
* **Modificar:** `Conrad.ipynb` (Atualizar Célula 1, Célula 2 e Célula 3 para refletir o novo SDK e importar as abstrações).
* **Criar:** `requirements.txt` (Para permitir execução e testes em ambiente local ou servidor).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 1.6.0-dev da migração do SDK).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Padronização de Dependências (`requirements.txt` e Célula 1)
Substituir a lista desordenada de pacotes. As dependências do projeto agora devem ser:
```text
google-genai>=1.0.0
markdown2>=2.4.10
beautifulsoup4>=4.12.0
lxml>=5.0.0
Pygments>=2.17.0
ipywidgets>=8.0.0
IPython>=8.0.0
```

No `Conrad.ipynb`, a Célula 1 deve executar:
```python
!pip -q install google-genai markdown2 beautifulsoup4 lxml Pygments ipywidgets
```

---

### 3.2. Implementação do Motor Conversacional (`src/conrad_core.py`)
Implementar a classe `ConradEngine` utilizando os padrões do novo SDK `google-genai`:

```python
import os
import html
from typing import Optional
from google import genai
from google.genai import types

class ConradEngine:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        system_instruction: Optional[str] = None
    ):
        self.api_key = api_key or self._resolve_api_key()
        if not self.api_key:
            raise ValueError(
                "API Key não encontrada. Configure a variável de ambiente GEMINI_API_KEY / GOOGLE_API_KEY "
                "ou forneça nos Secrets do Google Colab."
            )
            
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.client = genai.Client(api_key=self.api_key)
        self.chat = None
        self._init_chat()

    def _resolve_api_key(self) -> Optional[str]:
        # 1. Checa variáveis de ambiente de sistema
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if key:
            return key
        # 2. Fallback para Google Colab Secrets
        try:
            from google.colab import userdata
            return userdata.get("GOOGLE_API_KEY")
        except Exception:
            return None

    def _init_chat(self):
        config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            candidate_count=1,
            system_instruction=self.system_instruction,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
            ]
        )
        self.chat = self.client.chats.create(model=self.model_name, config=config)

    def send_message(self, prompt: str) -> str:
        """Envia mensagem para a sessão ativa de chat e trata bloqueios ou erros."""
        if not self.chat:
            raise RuntimeError("Sessão de chat não inicializada.")
        
        try:
            response = self.chat.send_message(prompt)
            if response.text:
                return response.text
            
            # Tratamento de bloqueio por filtros de segurança
            block_reason = "Filtro de segurança ativado"
            if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                block_reason = str(getattr(response.prompt_feedback, "block_reason", block_reason))
            return f"(Resposta indisponível: {block_reason}. Por favor, reformule sua pergunta.)"

        except Exception as e:
            raise RuntimeError(f"Erro na comunicação com a API Gemini: {str(e)}")

    def count_tokens(self, contents=None) -> int:
        """Calcula o consumo de tokens atual via client.models.count_tokens."""
        try:
            if contents is None and self.chat:
                # Usa o histórico do chat atual se nenhum conteúdo for passado
                history = self.chat.get_history()
                if not history:
                    return 0
                res = self.client.models.count_tokens(model=self.model_name, contents=history)
                return getattr(res, "total_tokens", 0)
            
            res = self.client.models.count_tokens(model=self.model_name, contents=contents)
            return getattr(res, "total_tokens", 0)
        except Exception:
            return 0
```

---

### 3.3. Refatoração da Célula 2 do Notebook (`Conrad.ipynb`)
Remover completamente qualquer import de `google.generativeai` ou chamadas a `genai.configure()`.  
A Célula 2 deve focar em carregar a chave e preparar a inicialização:
```python
# -- Imports e Configuração Inicial (Modernizado para google-genai v1.x) --
import os
import sys

# Garante acesso ao diretório src/ caso esteja rodando local ou clonado
if "." not in sys.path:
    sys.path.append(".")

try:
    from google.colab import userdata
    GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
except Exception:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')

if not GOOGLE_API_KEY:
    raise SystemExit("Erro: Chave da API não configurada nos Secrets do Colab ou nas Variáveis de Ambiente.")

model_name_conrad = "gemini-2.5-flash"
print(f"Ambiente configurado com sucesso! Modelo ativo: {model_name_conrad}")
```

---

### 3.4. Refatoração da Célula 3 (Listagem de Modelos)
Atualizar a listagem de modelos para a API do novo SDK:
```python
# -- Célula Utilitária: Listar Modelos Disponíveis com google-genai --
from google import genai

client = genai.Client(api_key=GOOGLE_API_KEY)

print("=" * 70)
print("MODELOS DISPONÍVEIS (suporte a generateContent):")
print("=" * 70)

for model in client.models.list():
    actions = getattr(model, "supported_actions", []) or []
    if "generateContent" in actions:
        print(f"Nome de Exibição: {model.display_name}")
        print(f"  Nome Técnico    : {model.name}")
        print(f"  Entrada Máx     : {getattr(model, 'input_token_limit', 'N/D')}")
        print(f"  Saída Máx       : {getattr(model, 'output_token_limit', 'N/D')}")
        print("-" * 40)
```

---

## 4. Critério de Validação (Definition of Done)
O Argon saberá que a Fase 1 foi concluída com sucesso quando todos os seguintes itens forem validados:

1. **Varredura de Código Morto:** Não deve restar nenhuma ocorrência de `import google.generativeai` nem de `genai.configure()` no repositório.
2. **Execução de Teste Unitário:** A execução do comando abaixo no terminal deve imprimir a mensagem com sucesso sem erros de importação:
   ```bash
   python -c "from src.conrad_core import ConradEngine; print('Core importado com sucesso!')"
   ```
3. **Teste de Envio Real:** Instanciar o `ConradEngine` em script local ou notebook, enviar `"Olá, Conrad!"` via `send_message()` e receber uma resposta íntegra da API.
4. **Contagem de Tokens Operacional:** `engine.count_tokens()` retorna um número inteiro positivo representando o consumo da sessão.
5. **Registro e Git Push:** Atualizar o `CHANGELOG.md` e realizar o commit no repositório com a mensagem padronizada:
   `feat(core): migracao para novo SDK google-genai e desacoplamento do motor`
