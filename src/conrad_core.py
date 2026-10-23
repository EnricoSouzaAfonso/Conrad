import os
import html
from typing import Optional
from google import genai
from google.genai import types
from src.conrad_persona import (
    get_system_instruction,
    get_missing_key_message,
    PEDAGOGICAL_MODES,
)

# Lista oficial de modelos definitivos (sem previews temporários que expiram)
DEFINITIVE_MODELS = {
    "Gemini 3.8 Flash (Padrão — Rápido, 1M Tokens)": "gemini-3.8-flash",
    "Gemini 2.5 Flash (Estável)": "gemini-2.5-flash",
    "Gemini 2.5 Pro (Raciocínio Profundo & Exatas)": "gemini-2.5-pro",
    "Gemini 1.5 Flash (Legado Estável)": "gemini-1.5-flash",
    "Gemini 1.5 Pro (Legado Pro)": "gemini-1.5-pro",
}

DEFAULT_MODEL_NAME = "gemini-3.8-flash"

# Mapeamento de roteamento ativo para evitar 503 (sobrecarga) ou 404 (modelos legados) no endpoint AI Studio
RUNTIME_MODEL_MAP = {
    "gemini-3.8-flash": "gemini-2.5-flash",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-pro": "gemini-3.5-flash",
    "gemini-1.5-flash": "gemini-2.5-flash",
    "gemini-1.5-pro": "gemini-3.5-flash",
}

FALLBACK_MODELS = ("gemini-2.5-flash", "gemini-3.5-flash-lite", "gemini-3.5-flash")


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
        self.system_instruction = system_instruction or get_system_instruction(self.pedagogical_mode)
        self.client = None
        self.chat = None
        self._active_runtime_model = self._get_runtime_model(self.model_name)

        if self.api_key:
            self._init_client_and_chat()

    @staticmethod
    def _get_runtime_model(model_name: str) -> str:
        """Retorna o modelo efetivo de baixa latência disponível na API."""
        return RUNTIME_MODEL_MAP.get(model_name, "gemini-2.5-flash")

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
        self.api_key = new_key.strip() if new_key else None
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
            self.system_instruction = get_system_instruction(mode)
            if self.client and self.api_key:
                self._init_chat()

    def build_context_with_memory(self, memory_notes: str) -> str:
        """Gera injeção de contexto com o histórico pedagógico do aluno."""
        return f"[HISTÓRICO PEDAGÓGICO DO ESTUDANTE]: {memory_notes}\n"

    def _create_client(self, api_key: str):
        """Cria instância do genai.Client com timeout curto e sem loop infinito de retry."""
        try:
            http_opts = types.HttpOptions(
                timeout=15000,
                retry_options=types.HttpRetryOptions(attempts=1),
            )
            return genai.Client(api_key=api_key, http_options=http_opts)
        except Exception:
            return genai.Client(api_key=api_key)

    def validate_api_key(self) -> bool:
        """Testa se a chave atual é válida realizando uma requisição rápida sem bloqueio."""
        if not self.api_key:
            return False
        try:
            test_client = self._create_client(self.api_key)
            for candidate_model in FALLBACK_MODELS:
                try:
                    test_res = test_client.models.generate_content(
                        model=candidate_model,
                        contents="ping",
                    )
                    if test_res:
                        return True
                except Exception as err:
                    err_str = str(err).upper()
                    if "API_KEY_INVALID" in err_str or "INVALID_ARGUMENT" in err_str or "400" in err_str or "403" in err_str:
                        return False
                    continue
            return False
        except Exception:
            return False

    def _init_client_and_chat(self):
        self.client = self._create_client(self.api_key)
        self._init_chat()

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

    def _init_chat(self, effective_model: Optional[str] = None):
        config = self._build_chat_config()
        target_model = effective_model or self._get_runtime_model(self.model_name)
        self._active_runtime_model = target_model
        self.chat = self.client.chats.create(model=target_model, config=config)

    def send_message(self, prompt: str) -> str:
        """Envia mensagem para a sessão ativa de chat e trata bloqueios, ausência de chave ou erros."""
        if not self.api_key or not self.chat:
            return get_missing_key_message()

        try:
            response = None
            last_err = None
            try:
                response = self.chat.send_message(prompt)
            except Exception as err:
                last_err = err
                for fb_model in FALLBACK_MODELS:
                    try:
                        self._init_chat(effective_model=fb_model)
                        response = self.chat.send_message(prompt)
                        last_err = None
                        break
                    except Exception as inner_err:
                        last_err = inner_err

            if last_err is not None and response is None:
                raise last_err

            if response and response.text:
                return response.text

            # Tratamento de bloqueio por filtros de segurança
            block_reason = "Filtro de segurança ativado"
            if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                block_reason = str(getattr(response.prompt_feedback, "block_reason", block_reason))
            return f"(Resposta indisponível: {block_reason}. Por favor, reformule sua pergunta.)"

        except Exception as e:
            raise RuntimeError(f"Erro na comunicação com a API Gemini: {str(e)}")

    def send_message_multimodal(
        self,
        prompt: str,
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> str:
        """Envia prompt acompanhado de mídia binária (imagem ou PDF)."""
        if not self.chat:
            raise RuntimeError("Sessão de chat não inicializada.")

        contents = []
        if media_bytes and mime_type:
            part = types.Part.from_bytes(data=media_bytes, mime_type=mime_type)
            contents.append(part)

        contents.append(prompt or "Por favor, analise este material e me guie no entendimento do exercício.")

        try:
            response = None
            last_err = None
            try:
                response = self.chat.send_message(contents)
            except Exception as err:
                last_err = err
                for fb_model in FALLBACK_MODELS:
                    try:
                        self._init_chat(effective_model=fb_model)
                        response = self.chat.send_message(contents)
                        last_err = None
                        break
                    except Exception as inner_err:
                        last_err = inner_err

            if last_err is not None and response is None:
                raise last_err

            return response.text if (response and response.text) else "(Sem resposta textual da API)"
        except Exception as e:
            raise RuntimeError(f"Erro ao processar conteúdo multimodal: {str(e)}")

    def send_message_stream(self, prompt: str):
        """Envia mensagem e gera chunks de texto em streaming (tempo real) com fallback automático."""
        if not self.api_key or not self.chat:
            yield get_missing_key_message()
            return

        try:
            yielded_any = False
            try:
                response_stream = self.chat.send_message_stream(prompt)
                for chunk in response_stream:
                    if chunk.text:
                        yielded_any = True
                        yield chunk.text
                if yielded_any:
                    return
            except Exception as first_err:
                last_err = first_err
                for fb_model in FALLBACK_MODELS:
                    try:
                        self._init_chat(effective_model=fb_model)
                        response_stream = self.chat.send_message_stream(prompt)
                        for chunk in response_stream:
                            if chunk.text:
                                yielded_any = True
                                yield chunk.text
                        if yielded_any:
                            return
                    except Exception as inner_err:
                        last_err = inner_err
                raise last_err
        except Exception as e:
            yield f"(Erro no streaming: {str(e)})"

    def count_tokens(self, contents=None) -> int:
        """Calcula o consumo de tokens atual de forma resiliente e rápida."""
        if not self.api_key or not self.client:
            return 0
        try:
            target_model = self._active_runtime_model or "gemini-2.5-flash"
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
