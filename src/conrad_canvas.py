"""
Módulo de Gerenciamento do Canvas e Artifacts do Conrad.
Responsável pelo parsing resiliente, extração, sanitização matemática (LaTeX complexo),
validação/reparo de diagramas Mermaid corrompidos e separação entre diálogo socrático e lousa.
"""
import re
from typing import Dict, Optional, Tuple


class ConradArtifact:
    """Representa um artefato pedagógico rico projetado no Quadro Negro do Conrad."""

    VALID_TYPES = ("math", "code", "mermaid", "summary")

    def __init__(self, artifact_type: str, title: str, content: str):
        raw_type = str(artifact_type or "summary").strip().lower()
        self.type = raw_type if raw_type in self.VALID_TYPES else "summary"
        self.title = str(title or "Quadro Negro").strip() or "Quadro Negro"
        raw_content = str(content or "").strip()
        if self.type == "math":
            self.content = self._sanitize_math(raw_content)
        elif self.type == "mermaid":
            repaired_mermaid, _, _ = CanvasParser.validate_and_repair_mermaid(raw_content)
            self.content = repaired_mermaid
        else:
            self.content = raw_content

    @staticmethod
    def _sanitize_math(text: str) -> str:
        """
        Garante integridade de blocos matemáticos (LaTeX/MathJax/KaTeX) simples ou complexos
        (matrizes, sistemas de equações, integrais múltiplas e delimitadores desbalanceados).
        """
        if not text:
            return ""
        cleaned = re.sub(r"\\\[(.*?)\\\]", lambda m: f"$${m.group(1).strip()}$$", text, flags=re.DOTALL)
        cleaned = re.sub(r"\\\((.*?)\\\)", lambda m: f"${m.group(1).strip()}$", cleaned, flags=re.DOTALL)

        # Se houver número ímpar de delimitadores $$, fecha automaticamente para evitar quebra do KaTeX
        if cleaned.count("$$") % 2 != 0:
            cleaned = cleaned + "$$"

        # Equações LaTeX puras ou ambientes (\begin{matrix}, \begin{cases}, etc.) sem cifrão
        if "$" not in cleaned and any(tok in cleaned for tok in ("\\", "=", "^", "_")):
            cleaned = f"$${cleaned}$$"

        # Balanceia \left sem \right correspondente dentro de blocos $$...$$
        def _balance_left_right(match: re.Match) -> str:
            inner = match.group(1)
            left_count = len(re.findall(r"\\left\b", inner))
            right_count = len(re.findall(r"\\right\b", inner))
            if left_count > right_count:
                inner = inner + (" \\right." * (left_count - right_count))
            return f"$${inner}$$"

        cleaned = re.sub(r"\$\$(.*?)\$\$", _balance_left_right, cleaned, flags=re.DOTALL)
        return cleaned

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
        if not isinstance(data, dict):
            return cls("summary", "Quadro Negro", str(data or ""))
        return cls(
            artifact_type=data.get("type", "summary"),
            title=data.get("title", "Quadro Negro"),
            content=data.get("content", ""),
        )


class CanvasParser:
    """Parser resiliente que intercepta tags <conrad_artifact> e separa o chat conversacional do Canvas."""

    ARTIFACT_OPEN_TAG_REGEX = re.compile(
        r"<conrad_artifact\b([^>]*)>(.*?)(?:</conrad_artifact>|$)",
        re.DOTALL | re.IGNORECASE,
    )
    ATTR_TYPE_REGEX = re.compile(r'\btype\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    ATTR_TITLE_REGEX = re.compile(r'\btitle\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

    THOUGHT_REGEX = re.compile(
        r"<(?:think|thought|conrad_thought)\b[^>]*>(.*?)(?:</(?:think|thought|conrad_thought)>|$)",
        re.DOTALL | re.IGNORECASE,
    )

    MERMAID_HEADERS = (
        "graph ",
        "graph\n",
        "flowchart ",
        "flowchart\n",
        "sequencediagram",
        "classdiagram",
        "statediagram",
        "erdiagram",
        "mindmap",
        "gantt",
        "pie",
        "timeline",
        "journey",
    )

    @classmethod
    def validate_and_repair_mermaid(cls, raw_mermaid: str) -> Tuple[str, bool, Optional[str]]:
        """
        Valida e repara diagramas Mermaid com sintaxe corrompida (cercas redundantes,
        ausência de cabeçalho graph/flowchart ou colchetes/parênteses não fechados).
        Retorna (mermaid_reparado, sintaxe_integra, aviso_reparo).
        """
        if not raw_mermaid or not str(raw_mermaid).strip():
            return "flowchart TD\n    A[Quadro Negro] --> B[Diagrama em Construção]", False, "Diagrama vazio."

        text = str(raw_mermaid).strip()
        # Remove cercas markdown ```mermaid ... ```
        fence_match = re.match(r"^```(?:mermaid|\w+)?\s*\n(.*?)(?:\n```)?$", text, flags=re.DOTALL | re.IGNORECASE)
        if fence_match:
            text = fence_match.group(1).strip()

        warnings = []
        lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            return "flowchart TD\n    A[Conceito Inicial]", False, "Diagrama sem nós válidos."

        first_lower = lines[0].strip().lower()
        if not any(first_lower.startswith(h) for h in cls.MERMAID_HEADERS):
            lines.insert(0, "flowchart TD")
            warnings.append("Cabeçalho 'flowchart TD' inserido automaticamente.")

        repaired_lines = []
        for idx, line in enumerate(lines):
            if idx == 0:
                repaired_lines.append(line)
                continue
            fixed_line = line
            # Se houver colchete aberto antes de uma seta (ex: A[Início --> B[Fim), fecha antes da seta
            fixed_line = re.sub(
                r"(\[[^\]\n]+?)(\s*(?:-->|---|-\.-|==>))",
                r"\1]\2",
                fixed_line,
            )
            # Balanceia colchetes, parênteses e chaves na linha
            open_sq, close_sq = fixed_line.count("["), fixed_line.count("]")
            if open_sq > close_sq:
                fixed_line += "]" * (open_sq - close_sq)
                warnings.append(f"Colchete fechado automaticamente na linha {idx + 1}.")

            open_par, close_par = fixed_line.count("("), fixed_line.count(")")
            if open_par > close_par:
                fixed_line += ")" * (open_par - close_par)
                warnings.append(f"Parêntese fechado automaticamente na linha {idx + 1}.")

            open_cur, close_cur = fixed_line.count("{"), fixed_line.count("}")
            if open_cur > close_cur:
                fixed_line += "}" * (open_cur - close_cur)
                warnings.append(f"Chave fechada automaticamente na linha {idx + 1}.")

            repaired_lines.append(fixed_line)

        repaired_text = "\n".join(repaired_lines)
        warning_msg = " ".join(warnings) if warnings else None
        return repaired_text, (warning_msg is None), warning_msg

    @classmethod
    def parse_message(cls, raw_text: str) -> Tuple[str, Optional[ConradArtifact]]:
        """
        Separa a mensagem conversacional do chat do conteúdo projetado no Canvas.
        Suporta atributos em qualquer ordem e tags <conrad_artifact> truncadas.
        Retorna (texto_limpo_do_chat, artifact_encontrado).
        """
        if not raw_text or not str(raw_text).strip():
            return "", None

        text_str = str(raw_text)
        match = cls.ARTIFACT_OPEN_TAG_REGEX.search(text_str)
        if not match:
            return text_str.strip(), None

        attrs_str = match.group(1) or ""
        content = (match.group(2) or "").strip()

        type_match = cls.ATTR_TYPE_REGEX.search(attrs_str)
        title_match = cls.ATTR_TITLE_REGEX.search(attrs_str)

        artifact_type = type_match.group(1).lower().strip() if type_match else "summary"
        title = title_match.group(1).strip() if title_match else "Quadro Negro"

        # Remove todas as tags <conrad_artifact> do texto do chat para manter o chat limpo
        clean_chat_text = cls.ARTIFACT_OPEN_TAG_REGEX.sub("", text_str).strip()
        if not clean_chat_text:
            clean_chat_text = "*(Conteúdo projetado no Quadro Negro ao lado 🎩)*"

        artifact = ConradArtifact(artifact_type=artifact_type, title=title, content=content)
        return clean_chat_text, artifact

    @classmethod
    def parse_thought(cls, text: str) -> Tuple[str, Optional[str]]:
        """
        Extrai eventual bloco de pensamento pedagógico explícito (<think>...</think>),
        inclusive se truncado, retornando (texto_sem_tags_think, pensamento_extraido).
        """
        if not text:
            return "", None

        text_str = str(text)
        match = cls.THOUGHT_REGEX.search(text_str)
        if not match:
            return text_str, None

        thought_content = (match.group(1) or "").strip()
        clean_text = cls.THOUGHT_REGEX.sub("", text_str).strip()
        return clean_text, thought_content
