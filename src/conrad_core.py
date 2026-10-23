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
