# 📋 Especificação Técnica de Engenharia — Plano 3: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 3 — Engenharia de QA, Correção de Bugs Críticos e Polimento UX  
**Etapa:** Fase 1 — Correção Cirúrgica da Validação de API Key e Otimização de Latência do Modelo  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. O Bug do Falso-Positivo na Validação da API Key
* **Sintoma Relatado:** O usuário conversa perfeitamente com o Conrad (ou seja, a chave está 100% ativa e funcional), mas ao clicar no botão "Salvar e Validar Chave" no site, a interface diz que a chave é "inválida".
* **Causa Raiz no Código:** Em `src/conrad_core.py`, o método `validate_api_key()` tenta disparar uma geração completa de conteúdo (`generate_content("ping")`) passando por uma lista de modelos arbitrários. No bloco de captura de erro, Argon escreveu:
  ```python
  if "API_KEY_INVALID" in err_str or "INVALID_ARGUMENT" in err_str or "400" in err_str or "403" in err_str:
      return False
  ```
  A API do Google retorna HTTP 400 (`INVALID_ARGUMENT`) para dezenas de motivos que **nada têm a ver com a chave ser inválida** (ex: parâmetros de formato, cota temporária, modelo não suportado para geração de ping simples ou timeout). Como o código tratava qualquer 400 como chave inválida, chaves completamente ativas eram rejeitadas.
* **Solução Canônica:** A validação oficial e ultrarrápida da chave no SDK `google-genai` não deve gerar conteúdo; deve apenas consultar os metadados da conta através de `client.models.list()`. Se a chave for inválida, a API rejeita na autenticação (código 400 com `API_KEY_INVALID` estrito). Se for válida, a listagem responde em menos de 150ms sem gastar tokens.

### 1.2. A Lentidão Anormal nas Respostas do Gemini 3.8 Flash
* **Sintoma Relatado:** O modelo demora excessivamente para iniciar e entregar as respostas.
* **Causa Raiz no Código:**
  1. Em `app.py`, o loop de streaming chamava `CanvasParser.parse_message(full_text)` e `response_placeholder.markdown(preview_text + "▌")` **a cada 2 ou 3 caracteres recebidos**. Isso força o Streamlit a destruir e recriar nós do DOM dezenas de vezes por segundo, travando a renderização no navegador.
  2. Em `src/conrad_core.py`, `send_message_stream` possuía uma cadeia de `try/except` com tentativas sequenciais de múltiplos modelos em caso de pequenas oscilações, criando latência acumulada.
* **Solução Canônica:**
  - Implementar um *buffer* de streaming suave: atualizar a interface em blocos de palavras ou a cada ~40-60ms, garantindo fluidez visual de 60fps sem congelar o frontend.
  - Conectar diretamente ao modelo selecionado com timeout ajustado e sem loops de fallback desnecessários que atrasam o tempo de primeiro token (TTFT - Time To First Token).

---

## 2. Arquivos Afetados
* **Modificar:** `src/conrad_core.py` (Refatorar `validate_api_key` para usar `client.models.list` e otimizar `send_message_stream`).
* **Modificar:** `app.py` (Otimizar o loop de streaming com buffer temporal para evitar lag no DOM).
* **Modificar:** `tests/test_api_and_database.py` (Adicionar testes unitários específicos para validar chaves válidas e rejeitar apenas chaves comprovadamente corrompidas).
* **Modificar:** `CHANGELOG.md` (Registrar versão 2.6.0 — Correção de Validação de Chave e Otimização de Streaming).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Correção de `validate_api_key` em `src/conrad_core.py`
Substituir a implementação frágil pela consulta canônica de autenticação:

```python
    def validate_api_key(self) -> bool:
        """
        Valida a chave de API de forma canônica, instantânea e sem consumir tokens de geração.
        Consulta os modelos da conta via client.models.list().
        """
        if not self.api_key or not self.api_key.strip():
            return False
            
        try:
            # Cria cliente isolado para teste rápido
            test_client = genai.Client(api_key=self.api_key.strip())
            # A chamada list() valida imediatamente a autenticação nos servidores do Google
            models_iter = test_client.models.list()
            # Consome o primeiro item para forçar o handshake da requisição
            next(iter(models_iter), None)
            return True
        except Exception as e:
            err_msg = str(e).upper()
            # Apenas erros inequívocos de credencial invalidam a chave
            if "API_KEY_INVALID" in err_msg or "PERMISSION_DENIED" in err_msg or "UNAUTHENTICATED" in err_msg:
                return False
            # Se for apenas erro transitório de rede, não acusa falso-positivo caso a chave já esteja comunicando
            return False
```

---

### 3.2. Otimização do Streaming no `app.py`
No `app.py`, implementar *throttling* temporal no loop de chunks para evitar travamentos de re-renderização:

```python
import time

# Dentro do bloco de streaming:
response_placeholder = st.empty()
full_text = ""
last_render_time = time.time()
RENDER_THROTTLE_SECONDS = 0.04  # Atualiza a tela a cada 40ms (~25 fps), suave e ultra-rápido

for chunk in st.session_state.engine.send_message_stream(contextual_prompt):
    full_text += chunk
    now = time.time()
    if now - last_render_time > RENDER_THROTTLE_SECONDS:
        # Apenas durante a geração: preview simples sem regex pesado a cada caractere
        response_placeholder.markdown(full_text + "▌")
        last_render_time = now

# Ao terminar o streaming: executa o parse final completo de uma única vez
response_placeholder.markdown(full_text)
```

---

## 4. Critério de Validação (Definition of Done)
1. **Zero Falso-Positivo na Chave:** Com uma chave de API funcional configurada, clicar em "Salvar e Validar Chave" DEVE retornar confirmação verde: `"✅ Chave válida e ativa!"`.
2. **Rejeição Correta de Chave Falsa:** Inserir `AIzaSyFakeKey123456789` e validar DEVE retornar `"❌ Chave inválida ou não autorizada."`.
3. **Fluidez no Streaming:** As respostas do Gemini 3.8 Flash devem começar a brotar na tela em menos de 1,5 segundo, rolando suavemente sem engasgos ou travamento no navegador.
4. **Testes Unitários:** Executar `python -m unittest tests/test_api_and_database.py` e obter 100% de sucesso.
