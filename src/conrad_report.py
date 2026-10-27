"""
Módulo Compilador do Caderno Digital de Estudos do Conrad.
Reúne diálogos, deduções do Quadro Negro (fórmulas LaTeX, diagramas Mermaid e código)
e gera resumos estruturados de revisão com Flashcards em Markdown (.md) e PDF.
Blindado contra entradas extremas (strings de 20k+ caracteres, bytes de controle e tags XML).
"""
import io
import re
import html
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)


class ConradNotebookCompiler:
    @staticmethod
    def _clean_xml_text(value: Any) -> str:
        """Remove caracteres de controle ilegais em XML (Expat) e aplica html.escape com segurança."""
        if value is None:
            return ""
        raw = str(value)
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", raw)
        return html.escape(cleaned)

    @staticmethod
    def _extract_artifact_fields(art: Any) -> Dict[str, str]:
        if isinstance(art, dict):
            return {
                "type": str(art.get("type") or "summary"),
                "title": str(art.get("title") or "Quadro Negro"),
                "content": str(art.get("content") or ""),
            }
        return {
            "type": str(getattr(art, "type", "summary") or "summary"),
            "title": str(getattr(art, "title", "Quadro Negro") or "Quadro Negro"),
            "content": str(getattr(art, "content", "") or ""),
        }

    @classmethod
    def to_markdown(
        cls,
        topic: str,
        messages: List[Dict[str, Any]],
        artifacts: List[Any],
    ) -> str:
        """Gera o Caderno Digital em Markdown estruturado para o aluno."""
        date_str = datetime.now().strftime("%d/%m/%Y às %H:%M")
        safe_topic = str(topic or "Matemática & Física").strip() or "Matemática & Física"
        md = [
            f"# 🎩 Caderno de Estudos do Conrad — {safe_topic}",
            f"> **Data da Sessão:** {date_str} | **Tutor:** Conrad (Método Socrático)",
            "\n---\n",
            "## 📌 Conceitos e Deduções Trabalhadas no Quadro Negro\n",
        ]

        valid_artifacts = [a for a in (artifacts or []) if a is not None]
        if valid_artifacts:
            for art in valid_artifacts:
                fields = cls._extract_artifact_fields(art)
                art_type = fields["type"].lower()
                art_title = fields["title"]
                art_content = fields["content"]
                md.append(f"### 📐 {art_title} ({art_type.upper()})")
                if art_type == "math":
                    md.append(f"\n{art_content}\n")
                elif art_type == "code":
                    md.append(f"```\n{art_content}\n```")
                elif art_type == "mermaid":
                    md.append(f"```mermaid\n{art_content}\n```")
                else:
                    md.append(f"\n{art_content}\n")
        else:
            md.append("*(Nenhum artifact específico foi gerado nesta sessão)*\n")

        md.append("\n---\n## 💬 Síntese do Diálogo Pedagógico\n")
        for msg in (messages or []):
            if not isinstance(msg, dict):
                continue
            sender = "Você" if msg.get("role") == "user" else "Conrad 🎩"
            content = str(msg.get("content") or "")
            md.append(f"**{sender}:** {content}\n")

        md.append("\n---\n## 🧠 Flashcards para Revisão Rápida")
        md.append("1. **Pergunta:** Qual foi o modelo mental central aprendido hoje?")
        md.append("   - *Resposta:* Reveja as deduções no Quadro Negro acima.")
        md.append(
            "2. **Desafio:** Como você explicaria este conceito com suas próprias palavras para um colega?"
        )

        return "\n".join(md)

    @classmethod
    def to_pdf_bytes(
        cls,
        topic: str,
        messages: List[Dict[str, Any]],
        artifacts: List[Any],
    ) -> bytes:
        """Compila o Caderno Digital em PDF elegante em memória (100% resiliente a entradas extremas)."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )
        styles = getSampleStyleSheet()

        c_primary = colors.HexColor("#1A2B4C")
        c_accent = colors.HexColor("#C59B27")

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=c_primary,
            wordWrap="CJK",
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=c_primary,
            spaceBefore=10,
            spaceAfter=6,
            wordWrap="CJK",
        )
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            wordWrap="CJK",
        )

        safe_topic = cls._clean_xml_text(topic or "Matemática & Física")[:160]
        story = [
            Paragraph(f"🎩 Caderno de Estudos — {safe_topic}", title_style),
            Paragraph(
                f"Sessão de Aprendizado Socrático com Conrad | {datetime.now().strftime('%d/%m/%Y')}",
                body_style,
            ),
            HRFlowable(
                width="100%",
                thickness=1.5,
                color=c_accent,
                spaceBefore=6,
                spaceAfter=12,
            ),
        ]

        valid_artifacts = [a for a in (artifacts or []) if a is not None]
        if valid_artifacts:
            story.append(Paragraph("<b>Quadro Negro (Conceitos &amp; Deduções):</b>", section_style))
            for art in valid_artifacts:
                fields = cls._extract_artifact_fields(art)
                safe_art_type = cls._clean_xml_text(fields["type"].upper())[:30]
                safe_art_title = cls._clean_xml_text(fields["title"])[:140]
                safe_art_content = cls._clean_xml_text(fields["content"][:400]).replace("\n", "<br/>")
                story.append(
                    Paragraph(
                        f"<b>[{safe_art_type}] {safe_art_title}:</b><br/>{safe_art_content}",
                        body_style,
                    )
                )
                story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Síntese das Deduções e Reflexões:</b>", section_style))
        story.append(Spacer(1, 4))

        valid_msgs = [m for m in (messages or []) if isinstance(m, dict)]
        for msg in valid_msgs[-6:]:
            sender = "Aluno:" if msg.get("role") == "user" else "Conrad:"
            safe_content = cls._clean_xml_text(str(msg.get("content") or "")[:250]).replace("\n", " ")
            story.append(Paragraph(f"<b>{sender}</b> {safe_content}...", body_style))
            story.append(Spacer(1, 4))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
