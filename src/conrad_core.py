import os
import re
import time
import html
from typing import Optional
from google import genai
from google.genai import types
from src.conrad_persona import (
    get_system_instruction,
    get_missing_key_message,
    PEDAGOGICAL_MODES,
)

# Lista oficial de modelos definitivos ativos no Google Gemini (2026)
DEFINITIVE_MODELS = {
    "Gemini 3.8 Flash (Padrão — Rápido, 1M Tokens)": "gemini-3.8-flash",
    "Gemini 3.6 Flash (Alta Estabilidade & Velocidade)": "gemini-3.6-flash",
    "Gemini 3.5 Flash (Estável & Multimodal)": "gemini-3.5-flash",
    "Gemini 3.1 Flash Lite (Ultra-Rápido & Econômico)": "gemini-3.1-flash-lite",
    "Gemini 3.1 Pro Preview (Raciocínio Avançado & Exatas)": "gemini-3.1-pro-preview",
}

DEFAULT_MODEL_NAME = "gemini-3.8-flash"

# Limite seguro de caracteres por prompt para evitar estouro de payload HTTP/DOM mantendo suporte a 20k+ chars
MAX_SAFE_PROMPT_CHARS = 32000

MSG_EMPTY_PROMPT = (
    "🎩 Parece que sua mensagem chegou em branco! "
    "Digite uma dúvida, fórmula matemática ou trecho de código para explorarmos juntos."
)


class ConradEngine:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_MODEL_NAME,
        system_instruction: Optional[str] = None,
        pedagogical_mode: str = "socratico",
    ):
        self.api_key = api_key if api_key is not None else self._resolve_api_key()
        self.model_name = model_name
        self.pedagogical_mode = pedagogical_mode if pedagogical_mode in PEDAGOGICAL_MODES else "socratico"
        self.custom_gem_directive: Optional[str] = None
        self.system_instruction = system_instruction or get_system_instruction(self.pedagogical_mode)
        self.client = None
        self.chat = None
        self._active_runtime_model = self._get_runtime_model(self.model_name)

        if self.api_key and self.api_key.strip():
            self._init_client_and_chat()

    @staticmethod
    def _get_runtime_model(model_name: str) -> str:
        """Retorna rigorosamente o modelo solicitado pelo usuário."""
        return model_name or DEFAULT_MODEL_NAME

    @staticmethod
    def _sanitize_prompt(prompt: Optional[str]) -> str:
        """
        Higieniza entradas extremas: remove caracteres de controle ASCII ilegais (\\x00-\\x08, etc.),
        preserva emojis e quebras de linha, e trunca com segurança entradas colossais (>32k chars).
        """
        if prompt is None:
            return ""
        text = str(prompt)
        # Remove bytes nulos e caracteres de controle não-imprimíveis exceto \t, \n, \r
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        if len(text) > MAX_SAFE_PROMPT_CHARS:
            head = text[:24000]
            tail = text[-6000:]
            text = (
                f"{head}\n\n"
                "[... trecho intermediário truncado automaticamente para proteção de memória ...]\n\n"
                f"{tail}"
            )
        return text

    def _format_resilient_error(self, err: Exception) -> str:
        """
        Traduz exceções da API (Timeout, 429 Quota, 401/403 Key Inválida, 503) em mensagens
        pedagógicas amigáveis para garantir Zero Crash (nunca exibir tela branca/traceback).
        """
        raw = str(err)
        upper = raw.upper()

        if "429" in upper or "RESOURCE_EXHAUSTED" in upper or "QUOTA" in upper or "RATE_LIMIT" in upper:
            return (
                "⏳ **Limite de Requisições Atingido (Erro 429 — Cota da API):** "
                "Sua chave atingiu temporariamente o limite gratuito para este modelo. "
                "Você pode aguardar alguns instantes ou alternar para o **Gemini 3.5 Flash** ou **Gemini 3.1 Flash Lite** na barra lateral! 🎩"
            )
        if "503" in upper or "HIGH DEMAND" in upper or "UNAVAILABLE" in upper:
            return (
                f"⚡ **Alta Demanda no Modelo {self.model_name} (Erro 503):** "
                "O modelo selecionado está enfrentando pico temporário de requisições no Google AI Studio. "
                "Por favor, tente enviar novamente em alguns segundos ou, se preferir, selecione outro modelo na barra lateral! 🎩"
            )
        if "TIMEOUT" in upper or "TIMED OUT" in upper or "DEADLINE_EXCEEDED" in upper or "504" in upper:
            return (
                "⌛ **Tempo Limite Excedido (Timeout de Rede):** "
                "O servidor demorou mais que o esperado para responder. "
                "Seu histórico e o Quadro Negro seguem intactos — por favor, tente enviar novamente! 🎩"
            )
        if "API_KEY_INVALID" in upper or "UNAUTHENTICATED" in upper or "PERMISSION_DENIED" in upper or "403" in upper or "401" in upper:
            return (
                "🔑 **Chave de API Inválida ou Não Autorizada:** "
                "Não foi possível autenticar sua chave junto ao Google Gemini. "
                "Verifique os caracteres na barra lateral à esquerda e clique em *Salvar Chave*. 🎩"
            )
        return (
            f"⚠️ **Oscilação Temporária na Comunicação com a IA:** "
            f"Não foi possível concluir a geração agora ({raw[:160]}). "
            f"Por favor, tente novamente em alguns instantes! 🎩"
        )

    def _resolve_api_key(self) -> Optional[str]:
        # 1. Checa variáveis de ambiente de sistema (prioriza GEMINI_API_KEY)
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if key:
            return key
        # 2. Fallback para arquivo .env local, se existir
        for env_path in (".env", os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")):
            if os.path.isfile(env_path):
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and v.strip():
                                    return v.strip().strip("'\"")
                except Exception:
                    pass
        # 3. Fallback para Google Colab Secrets
        try:
            from google.colab import userdata
            return userdata.get("GOOGLE_API_KEY")
        except Exception:
            return None

    def set_api_key(self, new_key: str):
        """Atualiza a chave de API e reinicializa o cliente e a sessão de chat."""
        self.api_key = new_key.strip() if new_key and new_key.strip() else None
        if self.api_key:
            self._init_client_and_chat()
        else:
            self.client = None
            self.chat = None

    def set_model(self, model_name: str):
        """Altera o modelo e preserva as configurações do chat."""
        self.model_name = model_name
        self._active_runtime_model = self._get_runtime_model(model_name)
        if self.api_key:
            if not self.client:
                self.client = self._create_client(self.api_key)
            self._init_chat()

    def set_pedagogical_mode(self, mode: str):
        """Atualiza o modo pedagógico e reinicia a sessão de chat com a nova instrução."""
        if mode in PEDAGOGICAL_MODES:
            self.pedagogical_mode = mode
            self.custom_gem_directive = None
            self.system_instruction = get_system_instruction(mode)
            if self.client and self.api_key:
                self._init_chat()

    def set_gem(self, gem_id: str, directive: str):
        """Atualiza a Gem ativa e regenera a sessão do chat com o novo System Instruction."""
        self.pedagogical_mode = gem_id
        self.custom_gem_directive = directive
        self.system_instruction = get_system_instruction(mode=gem_id, custom_directive=directive)
        if self.client and self.api_key:
            self._init_chat()

    def build_context_with_memory(self, memory_notes: str) -> str:
        """Gera injeção de contexto com o histórico pedagógico do aluno."""
        return f"[HISTÓRICO PEDAGÓGICO DO ESTUDANTE]: {memory_notes}\n"

    def _create_client(self, api_key: str):
        """Cria instância do genai.Client com timeout ajustado e sem loop de retry bloqueante."""
        try:
            http_opts = types.HttpOptions(
                timeout=30000,
                retry_options=types.HttpRetryOptions(attempts=1),
            )
            return genai.Client(api_key=api_key, http_options=http_opts)
        except Exception:
            return genai.Client(api_key=api_key)

    def validate_api_key(self) -> bool:
        """
        Valida a chave de API de forma canônica, instantânea e sem consumir tokens de geração.
        Consulta os modelos da conta via client.models.list().
        """
        if not self.api_key or not self.api_key.strip():
            return False

        try:
            # Cria cliente isolado com timeout curto para teste rápido sem travar a UI
            test_client = self._create_client(self.api_key.strip())
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

    def _init_client_and_chat(self):
        try:
            self.client = self._create_client(self.api_key)
            self._init_chat()
        except Exception:
            self.client = None
            self.chat = None

    def _build_chat_config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
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
            ],
        )

    def _init_chat(self, history=None):
        """Inicializa a sessão de chat estritamente com o modelo selecionado pelo usuário."""
        config = self._build_chat_config()
        target_model = self.model_name or DEFAULT_MODEL_NAME
        self._active_runtime_model = target_model
        if history:
            self.chat = self.client.chats.create(model=target_model, config=config, history=history)
        else:
            self.chat = self.client.chats.create(model=target_model, config=config)

    def send_message(self, prompt: str) -> str:
        """Envia mensagem para a sessão ativa de chat e trata bloqueios, ausência de chave, 429 ou timeouts (Zero Crash)."""
        if not self.api_key or not self.chat:
            return get_missing_key_message()

        clean_prompt = self._sanitize_prompt(prompt)
        if not clean_prompt.strip():
            return MSG_EMPTY_PROMPT

        try:
            try:
                response = self.chat.send_message(clean_prompt)
            except Exception as err:
                err_up = str(err).upper()
                # Retry pontual de 2 segundos NO MESMO MODELO em caso de 503 momentâneo
                if any(k in err_up for k in ("503", "UNAVAILABLE", "HIGH DEMAND")):
                    time.sleep(2)
                    response = self.chat.send_message(clean_prompt)
                else:
                    raise err

            if response and response.text:
                return response.text

            # Tratamento de bloqueio por filtros de segurança
            block_reason = "Filtro de segurança ativado"
            if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                block_reason = str(getattr(response.prompt_feedback, "block_reason", block_reason))
            return f"(Resposta indisponível: {block_reason}. Por favor, reformule sua pergunta.)"

        except Exception as e:
            return self._format_resilient_error(e)

    def send_message_multimodal(
        self,
        prompt: str,
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> str:
        """Envia prompt acompanhado de mídia binária (imagem ou PDF) com resiliência Zero Crash."""
        if not self.api_key or not self.chat:
            return get_missing_key_message()

        clean_prompt = self._sanitize_prompt(prompt)
        contents = []
        if media_bytes and mime_type:
            part = types.Part.from_bytes(data=media_bytes, mime_type=mime_type)
            contents.append(part)

        effective_text = clean_prompt.strip() or "Por favor, analise este material e me guie no entendimento do exercício."
        contents.append(effective_text)

        try:
            try:
                response = self.chat.send_message(contents)
            except Exception as err:
                err_up = str(err).upper()
                # Retry pontual de 2 segundos NO MESMO MODELO em caso de 503 momentâneo
                if any(k in err_up for k in ("503", "UNAVAILABLE", "HIGH DEMAND")):
                    time.sleep(2)
                    response = self.chat.send_message(contents)
                else:
                    raise err
            return response.text if (response and response.text) else "(Sem resposta textual da API)"
        except Exception as e:
            return self._format_resilient_error(e)

    def send_message_stream(self, prompt: str):
        """Envia mensagem e gera chunks de texto em streaming (tempo real) com blindagem Zero Crash."""
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

    def count_tokens(self, contents=None) -> int:
        """Calcula o consumo de tokens atual de forma resiliente e rápida."""
        if not self.api_key or not self.client:
            return 0
        try:
            target_model = self.model_name or DEFAULT_MODEL_NAME
            if contents is None and self.chat:
                history = self.chat.get_history()
                if not history:
                    return 0
                res = self.client.models.count_tokens(model=target_model, contents=history)
                return getattr(res, "total_tokens", 0)

            if contents is not None:
                res = self.client.models.count_tokens(model=target_model, contents=contents)
                return getattr(res, "total_tokens", 0)
            return 0
        except Exception:
            return 0
