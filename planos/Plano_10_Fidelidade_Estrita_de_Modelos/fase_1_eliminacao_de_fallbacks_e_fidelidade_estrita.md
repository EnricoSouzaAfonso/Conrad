# 📋 Especificação Técnica de Engenharia — Plano 10: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 10 — Fidelidade Estrita de Modelos e Eliminação de Substituições Silenciosas  
**Etapa:** Fase 1 — Eliminação de Fallbacks Ocultos e Vinculação Estrita 1:1 no Motor (`src/conrad_core.py`)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. O Problema Relatado pelo Usuário
O usuário selecionou explicitamente o modelo `Gemini 3.8 Flash` nas configurações do Conrad, mas o backend trocou silenciosamente para outro modelo durante a execução:
> *"ele trocou para outro modelo, simplesmente não está usando o 3.8 flash não sei porque, mande o argon usar a versão correta de acordo com oque o usuário selecionar na lista de modelos que fica nas configurações, temos que resolver esse buf"*

### 1.2. Causa Raiz Arquitetural
1. **Existência de Fallbacks Ocultos:** No método `send_message_stream` (e em `send_message`), havia blocos `except` que capturavam erros transitórios (como `503 UNAVAILABLE` ou `TIMEOUT`) e reinicializavam o chat trocando o modelo ativo para um fallback (`FALLBACK_MODEL_NAME = "gemini-3.5-flash"` ou `gemini-2.5-flash-lite`).
2. **Violação da Intenção do Usuário:** Quando o usuário escolhe `Gemini 3.8 Flash`, ele quer testar e utilizar o `gemini-3.8-flash`. Substituir o modelo por baixo dos panos é inaceitável. O controle sobre qual modelo utilizar deve pertencer 100% ao usuário.

---

## 2. Instruções Técnicas Passo a Passo para o Argon

Argon, aplique rigorosamente as seguintes instruções no arquivo `src/conrad_core.py` (e replique em `repo/src/conrad_core.py` e `Conrad/src/conrad_core.py`):

### 2.1. Eliminar Qualquer Constante ou Roteamento de Fallback
1. **Remover** a constante `FALLBACK_MODEL_NAME = "gemini-3.5-flash"`.
2. **Remover** qualquer menção a `RUNTIME_MODEL_MAP`.
3. Manter o catálogo oficial limpo e direto:
```python
DEFINITIVE_MODELS = {
    "Gemini 3.8 Flash (Padrão — Rápido, 1M Tokens)": "gemini-3.8-flash",
    "Gemini 3.6 Flash (Alta Estabilidade & Velocidade)": "gemini-3.6-flash",
    "Gemini 3.5 Flash (Estável & Multimodal)": "gemini-3.5-flash",
    "Gemini 3.1 Flash Lite (Ultra-Rápido & Econômico)": "gemini-3.1-flash-lite",
    "Gemini 3.1 Pro Preview (Raciocínio Avançado & Exatas)": "gemini-3.1-pro-preview",
}

DEFAULT_MODEL_NAME = "gemini-3.8-flash"
```

4. Garantir que `_get_runtime_model` apenas retorne o modelo solicitado, sem desvios:
```python
@staticmethod
def _get_runtime_model(model_name: str) -> str:
    """Retorna rigorosamente o modelo solicitado pelo usuário."""
    return model_name or DEFAULT_MODEL_NAME
```

---

### 2.2. Garantir Criação Estrita do Chat no `_init_chat`
O método `_init_chat` deve instanciar o chat SEMPRE com `self.model_name`:
```python
def _init_chat(self, history=None):
    """Inicializa a sessão de chat estritamente com o modelo selecionado pelo usuário."""
    config = self._build_chat_config()
    target_model = self.model_name or DEFAULT_MODEL_NAME
    self._active_runtime_model = target_model
    if history:
        self.chat = self.client.chats.create(model=target_model, config=config, history=history)
    else:
        self.chat = self.client.chats.create(model=target_model, config=config)
```

---

### 2.3. Eliminar Troca Oculta de Modelos nos Métodos de Envio
Em `send_message`, `send_message_multimodal` e `send_message_stream`, **NUNCA** reinicializar o chat com outro modelo.
Se a API do Google retornar `503 UNAVAILABLE` (alta demanda) ou `TIMEOUT`:
1. Executar 1 tentativa de *retry* com backoff curto (2 segundos) no **MESMO** modelo (`self.model_name`).
2. Se persistir, levantar a exceção e permitir que `_format_resilient_error` exiba a mensagem pedagógica clara para o usuário, deixando a decisão de trocar de modelo na mão dele:

```python
# Em send_message_stream:
def send_message_stream(self, prompt: str):
    if not self.api_key or not self.chat:
        yield get_missing_key_message()
        return

    clean_prompt = self._sanitize_prompt(prompt)
    if not clean_prompt.strip():
        yield MSG_EMPTY_PROMPT
        return

    try:
        yielded_any = False
        try:
            response_stream = self.chat.send_message_stream(clean_prompt)
            for chunk in response_stream:
                if getattr(chunk, "text", None):
                    yielded_any = True
                    yield chunk.text
        except Exception as err:
            err_up = str(err).upper()
            # Retry pontual de 2 segundos NO MESMO MODELO em caso de 503 momentâneo
            if not yielded_any and any(k in err_up for k in ("503", "UNAVAILABLE", "HIGH DEMAND")):
                time.sleep(2)
                response_stream = self.chat.send_message_stream(clean_prompt)
                for chunk in response_stream:
                    if getattr(chunk, "text", None):
                        yielded_any = True
                        yield chunk.text
            else:
                raise err

        if not yielded_any:
            yield "(O modelo concluiu a requisição sem gerar texto adicional.)"
    except Exception as e:
        yield self._format_resilient_error(e)
```

E no método `_format_resilient_error`:
```python
if "503" in upper or "HIGH DEMAND" in upper or "UNAVAILABLE" in upper:
    return (
        f"⚡ **Alta Demanda no Modelo {self.model_name} (Erro 503):** "
        "O modelo selecionado está enfrentando pico temporário de requisições no Google AI Studio. "
        "Por favor, tente enviar novamente em alguns segundos ou, se preferir, selecione outro modelo na barra lateral! 🎩"
    )
```

---

## 3. Checklist de Validação para o Argon
- [ ] Verificar que não existe nenhuma linha contendo `FALLBACK_MODEL_NAME` no `conrad_core.py`.
- [ ] Confirmar que `self.chat` é criado exclusivamente com `self.model_name`.
- [ ] Executar script de teste verificando que ao selecionar `gemini-3.8-flash`, a propriedade `engine.model_name` e `engine._active_runtime_model` são ambos `gemini-3.8-flash`.
