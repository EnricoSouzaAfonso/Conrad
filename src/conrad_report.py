"""
Módulo Compilador do Caderno Digital de Estudos do Conrad.
Reúne diálogos, deduções do Quadro Negro (fórmulas LaTeX, diagramas Mermaid e código)
e gera resumos estruturados de revisão com Flashcards em Markdown (.md) e PDF.
"""
import io
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
    Table,
    TableStyle,
    HRFlowable,
)


class ConradNotebookCompiler:
    @classmethod
    def to_markdown(
        cls,
        topic: str,
        messages: List[Dict[str, Any]],
        artifacts: List[Any],
    ) -> str:
        """Gera o Caderno Digital em Markdown estruturado para o aluno."""
        date_str = datetime.now().strftime("%d/%m/%Y às %H:%M")
        md = [
            f"# 🎩 Caderno de Estudos do Conrad — {topic}",
            f"> **Data da Sessão:** {date_str} | **Tutor:** Conrad (Método Socrático)",
            "\n---\n",
            "## 📌 Conceitos e Deduções Trabalhadas no Quadro Negro\n",
        ]

        if artifacts:
            for art in artifacts:
                md.append(f"### 📐 {art.title} ({art.type.upper()})")
                if art.type == "math":
                    md.append(f"\n{art.content}\n")
                elif art.type == "code":
                    md.append(f"```\n{art.content}\n```")
                elif art.type == "mermaid":
                    md.append(f"```mermaid\n{art.content}\n```")
                else:
                    md.append(f"\n{art.content}\n")
        else:
            md.append("*(Nenhum artifact específico foi gerado nesta sessão)*\n")

        md.append("\n---\n## 💬 Síntese do Diálogo Pedagógico\n")
        for msg in messages:
            sender = "Você" if msg["role"] == "user" else "Conrad 🎩"
            md.append(f"**{sender}:** {msg['content']}\n")

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
        """Compila o Caderno Digital em PDF elegante em memória."""
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
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=c_primary,
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
        )

        safe_topic = html.escape(topic or "Matemática & Física")
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

        if artifacts:
            story.append(Paragraph("<b>Quadro Negro (Conceitos & Deduções):</b>", section_style))
            for art in artifacts:
                safe_art_title = html.escape(str(art.title))
                safe_art_content = html.escape(str(art.content)[:400]).replace("\n", "<br/>")
                story.append(
                    Paragraph(
                        f"<b>[{html.escape(str(art.type).upper())}] {safe_art_title}:</b><br/>{safe_art_content}",
                        body_style,
                    )
                )
                story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Síntese das Deduções e Reflexões:</b>", section_style))
        story.append(Spacer(1, 4))

        for msg in messages[-6:]:  # Principais mensagens
            sender = "Aluno:" if msg["role"] == "user" else "Conrad:"
            safe_content = html.escape(str(msg.get("content", ""))[:250])
            story.append(Paragraph(f"<b>{sender}</b> {safe_content}...", body_style))
            story.append(Spacer(1, 4))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
