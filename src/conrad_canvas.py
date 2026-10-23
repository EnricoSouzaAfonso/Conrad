"""
Módulo de Gerenciamento do Canvas e Artifacts do Conrad.
Responsável pelo parsing, extração e estruturação de blocos <conrad_artifact>
e separação entre diálogo conversacional socrático e conteúdo denso da lousa.
"""
import re
from typing import Dict, List, Optional, Tuple


class ConradArtifact:
    """Representa um artefato pedagógico rico projetado no Quadro Negro do Conrad."""

    VALID_TYPES = ("math", "code", "mermaid", "summary")

    def __init__(self, artifact_type: str, title: str, content: str):
        self.type = (artifact_type or "summary").strip().lower()
        self.title = (title or "Quadro Negro").strip()
        self.content = (content or "").strip()

    def to_dict(self) -> Dict[str, str]:
        """Serializa o artefato para armazenamento em sessão ou histórico."""
        return {
            "type": self.type,
            "title": self.title,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ConradArtifact":
        """Reconstrói uma instância de ConradArtifact a partir de um dicionário."""
        return cls(
            artifact_type=data.get("type", "summary"),
            title=data.get("title", "Quadro Negro"),
            content=data.get("content", ""),
        )


class CanvasParser:
    """Parser que intercepta tags <conrad_artifact> e separa o chat conversacional do Canvas."""

    ARTIFACT_REGEX = re.compile(
        r'<conrad_artifact\s+type=["\'](.*?)["\']\s+title=["\'](.*?)["\']>(.*?)</conrad_artifact>',
        re.DOTALL | re.IGNORECASE,
    )

    THOUGHT_REGEX = re.compile(
        r'<(?:think|thought|conrad_thought)>(.*?)</(?:think|thought|conrad_thought)>',
        re.DOTALL | re.IGNORECASE,
    )

    @classmethod
    def parse_message(cls, raw_text: str) -> Tuple[str, Optional[ConradArtifact]]:
        """
        Separa a mensagem conversacional do chat do conteúdo projetado no Canvas.
        Retorna (texto_limpo_do_chat, artifact_encontrado).
        """
        if not raw_text:
            return "", None

        match = cls.ARTIFACT_REGEX.search(raw_text)
        if not match:
            return raw_text.strip(), None

        artifact_type = match.group(1).lower().strip()
        title = match.group(2).strip()
        content = match.group(3).strip()

        # Remove o artifact do texto do chat para manter o chat limpo e conversacional
        clean_chat_text = cls.ARTIFACT_REGEX.sub("", raw_text).strip()
        if not clean_chat_text:
            clean_chat_text = "*(Conteúdo projetado no Quadro Negro ao lado 🎩)*"

        artifact = ConradArtifact(artifact_type=artifact_type, title=title, content=content)
        return clean_chat_text, artifact

    @classmethod
    def parse_thought(cls, text: str) -> Tuple[str, Optional[str]]:
        """
        Extrai eventual bloco de pensamento pedagógico explícito (<think>...</think>),
        retornando (texto_sem_tags_think, pensamento_extraido).
        """
        if not text:
            return "", None

        match = cls.THOUGHT_REGEX.search(text)
        if not match:
            return text, None

        thought_content = match.group(1).strip()
        clean_text = cls.THOUGHT_REGEX.sub("", text).strip()
        return clean_text, thought_content
