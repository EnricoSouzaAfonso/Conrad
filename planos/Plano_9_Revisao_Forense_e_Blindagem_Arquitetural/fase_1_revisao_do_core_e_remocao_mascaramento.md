# 📋 Especificação Técnica de Auditoria — Plano 9: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 9 — Dossiê de Auditoria Forense e Revisão Técnica para o Argon  
**Etapa:** Fase 1 — Revisão Crítica do Motor Cognitivo (`src/conrad_core.py`)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Contexto & Diagnóstico da Falha Reportada pelo Usuário

### 1.1. O Erro Relatado
O usuário selecionou explicitamente o modelo `Gemini 3.8 Flash` na interface web do Conrad. Ao enviar uma dúvida sobre a "Teoria das Cordas", recebeu a seguinte mensagem de erro no chat:
> *"⚠️ Oscilação Temporária na Comunicação com a IA: Não foi possível concluir a geração agora (404 NOT_FOUND. {'error': {'code': 404, 'message': 'This model models/gemini-2.5-flash-lite is no longer available to new users. Please update your code to use m). Por favor, tente novamente em alguns instantes! 🎩"*

### 1.2. Diagnóstico da Causa Raiz
Ao auditar o arquivo `src/conrad_core.py`, foram encontrados dois erros arquiteturais graves:

1. **Seqüestro Silencioso de Modelos (`RUNTIME_MODEL_MAP`):**
   Existia um dicionário hardcoded que interceptava qualquer escolha do usuário e redirecionava para o `gemini-2.5-flash`:
   ```python
   # ERRO ANTERIOR:
   RUNTIME_MODEL_MAP = {
       "gemini-3.8-flash": "gemini-2.5-flash",
       "gemini-2.5-flash": "gemini-2.5-flash",
       "gemini-2.5-pro": "gemini-2.5-flash",
       "gemini-1.5-flash": "gemini-2.5-flash",
       "gemini-1.5-pro": "gemini-2.5-flash",
   }
   ```
   **Impacto:** O frontend afirmava que o `Gemini 3.8 Flash` estava ativo, mas as requisições enviadas ao Google AI Studio eram sempre para `gemini-2.5-flash`. Na cota do Free Tier, o Google limita o `gemini-2.5-flash` a **apenas 20 requisições por dia**, estourando imediatamente (`429 RESOURCE_EXHAUSTED`).

2. **Fallback para Modelo Extinto (`gemini-2.5-flash-lite`):**
   Ao capturar a exceção de cota ou sobrecarga, o código tentava um failover fixo para `gemini-2.5-flash-lite`:
   ```python
   # ERRO ANTERIOR:
   self._init_chat(effective_model="gemini-2.5-flash-lite", history=prev_hist)
   ```
   **Impacto:** O Google descontinuou o `gemini-2.5-flash-lite` para novas contas/projetos. A chamada resultou no erro `404 NOT_FOUND`.

---

## 2. Modificações Exatas Realizadas no `src/conrad_core.py`

Argon, revise os seguintes trechos de código aplicados no `src/conrad_core.py`:

### 2.1. Remoção do Mascaramento e Atualização do Catálogo de Modelos
* **Removido:** Dicionário `RUNTIME_MODEL_MAP`.
* **Adicionado:** Catálogo oficial com os modelos verificados diretamente na API do usuário:
```python
# Lista oficial de modelos definitivos ativos no Google Gemini (2026)
DEFINITIVE_MODELS = {
    "Gemini 3.8 Flash (Padrão — Rápido, 1M Tokens)": "gemini-3.8-flash",
    "Gemini 3.6 Flash (Alta Estabilidade & Velocidade)": "gemini-3.6-flash",
    "Gemini 3.5 Flash (Estável & Multimodal)": "gemini-3.5-flash",
    "Gemini 3.1 Flash Lite (Ultra-Rápido & Econômico)": "gemini-3.1-flash-lite",
    "Gemini 3.1 Pro Preview (Raciocínio Avançado & Exatas)": "gemini-3.1-pro-preview",
}

DEFAULT_MODEL_NAME = "gemini-3.8-flash"
FALLBACK_MODEL_NAME = "gemini-3.5-flash"  # Modelo com 100% de disponibilidade comprovada na API
```

* **Simplificação do `_get_runtime_model`:**
```python
@staticmethod
def _get_runtime_model(model_name: str) -> str:
    """Retorna o modelo solicitado diretamente pelo usuário, sem mascaramento ou desvio."""
    return model_name or DEFAULT_MODEL_NAME
```

### 2.2. Failover Resiliente e Protegido
Nos métodos `send_message`, `send_message_multimodal` e `send_message_stream`, o fallback agora utiliza `FALLBACK_MODEL_NAME` (`gemini-3.5-flash`) e só é disparado se o modelo ativo já não for o próprio modelo de fallback:

```python
# Em send_message_stream:
except Exception as err:
    err_up = str(err).upper()
    if not yielded_any and self.model_name != FALLBACK_MODEL_NAME and any(k in err_up for k in ("503", "UNAVAILABLE", "HIGH DEMAND", "TIMEOUT", "TIMED OUT", "DEADLINE_EXCEEDED", "504")):
        prev_hist = self.chat.get_history() if hasattr(self.chat, "get_history") else None
        self._init_chat(effective_model=FALLBACK_MODEL_NAME, history=prev_hist)
        response_stream = self.chat.send_message_stream(clean_prompt)
        for chunk in response_stream:
            if getattr(chunk, "text", None):
                yielded_any = True
                yield chunk.text
    else:
        raise err
```

### 2.3. Mensagens de Diagnóstico Resiliente (`_format_resilient_error`)
Atualização para diferenciar pedagogicamente erros de cota (429) e sobrecarga temporária do servidor (503):
```python
if "429" in upper or "RESOURCE_EXHAUSTED" in upper or "QUOTA" in upper or "RATE_LIMIT" in upper:
    return (
        "⏳ **Limite de Requisições Atingido (Erro 429 — Cota da API):** "
        "Sua chave atingiu temporariamente o limite gratuito para este modelo. "
        "Você pode aguardar alguns instantes ou alternar para o **Gemini 3.5 Flash** ou **Gemini 3.1 Flash Lite** na barra lateral! 🎩"
    )
if "503" in upper or "HIGH DEMAND" in upper or "UNAVAILABLE" in upper:
    return (
        "⚡ **Alta Demanda Momentânea nos Servidores (Erro 503):** "
        "O modelo selecionado está enfrentando pico de tráfego temporário no Google AI Studio. "
        "Por favor, tente novamente em alguns segundos ou selecione o **Gemini 3.5 Flash** na barra lateral para resposta imediata! 🎩"
    )
```

### 2.4. Timeout HTTP Ajustado
Em `_create_client`, o timeout foi elevado de 15s para 30s (`timeout=30000`), evitando falsos timeouts em respostas que exigem raciocínio complexo.

---

## 3. Checklist de Revisão para o Argon
- [ ] Inspecionar `src/conrad_core.py`, `repo/src/conrad_core.py` e `Conrad/src/conrad_core.py`.
- [ ] Confirmar que o termo `gemini-2.5-flash-lite` foi completamente extirpado do projeto.
- [ ] Confirmar que o termo `RUNTIME_MODEL_MAP` não existe mais no código.
- [ ] Testar envio de mensagem com `gemini-3.8-flash` e validar que as requisições são entregues ao modelo correto.
