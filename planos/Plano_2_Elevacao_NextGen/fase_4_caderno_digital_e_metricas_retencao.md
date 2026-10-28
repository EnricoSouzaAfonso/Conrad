# 📋 Especificação Técnica de Engenharia — Plano 2: Fase 4
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 2 — Elevação Next-Gen & Arquitetura Comercial de Alto Nível  
**Etapa:** Fase 4 — Caderno Digital de Estudos (Exportação MD/PDF) e Termômetro de Retenção Cognitiva  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Concluir o ciclo do **Plano 2 (Elevação Next-Gen)** entregando as ferramentas que convertem as sessões de tutoria socrática em **ativos educacionais permanentes**:
1. **Caderno Digital de Estudos:** Um compilador automatizado que reúne os diálogos, as deduções do Quadro Negro (fórmulas LaTeX, diagramas Mermaid e blocos de código) e gera um resumo estruturado de revisão acompanhado de **Flashcards de Auto-Avaliação**. O aluno pode exportar seu material em Markdown (`.md`) ou em PDF diagramado com 1 clique.
2. **Termômetro de Retenção Cognitiva:** Uma camada analítica que avalia o grau de autonomia do estudante durante a sessão (quantas pistas foram necessárias, se houve articulação própria de conceitos e capacidade de identificar *edge cases*), exibindo um diagnóstico formativo de domínio do tema e registrando os dados para relatórios escolares.

---

## 2. Arquivos Afetados
* **Criar:** `src/conrad_report.py` (Compilador de resumos de aula e gerador de PDF/Markdown estilizado).
* **Criar:** `src/conrad_analytics.py` (Avaliador de autonomia e cálculo do Termômetro de Retenção).
* **Modificar:** `app.py` (Adicionar botões de download direto no Canvas/Sidebar e exibir o widget do Termômetro de Retenção ao final da sessão).
* **Criar:** `tests/test_caderno_and_analytics.py` (Testes unitários garantindo a geração limpa de PDFs e compilação de flashcards).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 2.5.0 — Lançamento do Caderno Digital e Termômetro de Retenção).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Compilador do Caderno Digital (`src/conrad_report.py`)
O Argon deve implementar a classe `ConradNotebookCompiler` para gerar tanto Markdown limpo quanto PDFs com ReportLab:

```python
"""
Módulo Compilador do Caderno Digital de Estudos do Conrad.
"""
import io
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

class ConradNotebookCompiler:
    @classmethod
    def to_markdown(cls, topic: str, messages: List[Dict[str, str]], artifacts: List[Any]) -> str:
        """Gera o Caderno Digital em Markdown estruturado para o aluno."""
        date_str = datetime.now().strftime("%d/%m/%Y às %H:%M")
        md = [
            f"# 🎩 Caderno de Estudos do Conrad — {topic}",
            f"> **Data da Sessão:** {date_str} | **Tutor:** Conrad (Método Socrático)",
            "\n---\n",
            "## 📌 Conceitos e Deduções Trabalhadas no Quadro Negro\n"
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
        md.append("2. **Desafio:** Como você explicaria este conceito com suas próprias palavras para um colega?")

        return "\n".join(md)

    @classmethod
    def to_pdf_bytes(cls, topic: str, messages: List[Dict[str, str]], artifacts: List[Any]) -> bytes:
        """Compila o Caderno Digital em PDF elegante em memória."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()

        c_primary = colors.HexColor("#1A2B4C")
        c_accent = colors.HexColor("#C59B27")

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=c_primary)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13)

        story = [
            Paragraph(f"🎩 Caderno de Estudos — {topic}", title_style),
            Paragraph(f"Sessão de Aprendizado Socrático com Conrad | {datetime.now().strftime('%d/%m/%Y')}", body_style),
            HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=6, spaceAfter=12),
            Paragraph("<b>Síntese das Deduções e Reflexões:</b>", body_style),
            Spacer(1, 8)
        ]

        for msg in messages[-6:]:  # Principais mensagens
            sender = "Aluno:" if msg["role"] == "user" else "Conrad:"
            story.append(Paragraph(f"<b>{sender}</b> {msg['content'][:250]}...", body_style))
            story.append(Spacer(1, 4))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
```

---

### 3.2. Termômetro de Retenção Cognitiva (`src/conrad_analytics.py`)
Módulo analítico que avalia a autonomia do aluno com base na densidade do diálogo:

```python
"""
Módulo de Métricas e Termômetro de Retenção Cognitiva.
"""
from typing import List, Dict

class CognitiveRetentionTracker:
    @classmethod
    def evaluate_session(cls, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calcula o índice de autonomia e retenção cognitiva da sessão."""
        total_user_msgs = sum(1 for m in messages if m["role"] == "user")
        if total_user_msgs == 0:
            return {"score": 0, "status": "Iniciando", "feedback": "Envie sua primeira dúvida!"}

        # Medição heurística baseada no engajamento e tamanho médio de resposta do aluno
        user_words = sum(len(m["content"].split()) for m in messages if m["role"] == "user")
        avg_words = user_words / total_user_msgs

        if avg_words > 25 and total_user_msgs >= 4:
            score = 90
            status = "Excelente Autonomia 🌟"
            feedback = "Você articulou explicações ricas com suas próprias palavras. O modelo mental foi assimilado com solidez!"
        elif avg_words > 12 and total_user_msgs >= 2:
            score = 75
            status = "Boa Compreensão 💡"
            feedback = "Você acompanhou bem os andaimes cognitivos. Experimente praticar mais exercícios para consolidar."
        else:
            score = 60
            status = "Em Construção 🧱"
            feedback = "O conceito foi introduzido. Continue questionando e explorando as analogias do Conrad!"

        return {"score": score, "status": status, "feedback": feedback}
```

---

### 3.3. Integração na Interface (`app.py`)
No `app.py`, o Argon deve:
1. No cabeçalho ou rodapé do Canvas lateral, adicionar botões de exportação:
   ```python
   col_d1, col_d2 = st.columns(2)
   with col_d1:
       md_data = ConradNotebookCompiler.to_markdown("Matemática & Física", st.session_state.messages, [st.session_state.active_artifact] if st.session_state.active_artifact else [])
       st.download_button("📥 Baixar Resumo (.md)", data=md_data, file_name="caderno_conrad.md", mime="text/markdown", use_container_width=True)
   with col_d2:
       pdf_data = ConradNotebookCompiler.to_pdf_bytes("Matemática & Física", st.session_state.messages, [])
       st.download_button("📄 Baixar Caderno (.pdf)", data=pdf_data, file_name="caderno_conrad.pdf", mime="application/pdf", use_container_width=True)
   ```
2. Adicionar o Termômetro de Retenção no menu lateral:
   ```python
   stats = CognitiveRetentionTracker.evaluate_session(st.session_state.messages)
   st.sidebar.markdown(f"### 🌡️ Termômetro de Retenção")
   st.sidebar.progress(stats["score"] / 100)
   st.sidebar.caption(f"**Nível:** {stats['status']}\n\n*{stats['feedback']}*")
   ```
3. Estilos de Impressão `@media print` para quem quiser imprimir a página diretamente com `Ctrl+P`:
   ```css
   @media print {
       header, footer, [data-testid="stSidebar"], .stChatInput { display: none !important; }
       .stApp { background: white !important; color: black !important; }
   }
   ```

---

## 4. Critério de Validação (Definition of Done)
1. **Download do Arquivo Markdown:** Clicar no botão "Baixar Resumo (.md)" gera um arquivo válido contendo todos os artifacts, fórmulas em LaTeX e histórico limpo.
2. **Geração do Caderno em PDF:** Clicar em "Baixar Caderno (.pdf)" compila e entrega um documento PDF diagramado com tipografia formal e cabeçalho executivo.
3. **Termômetro em Tempo Real:** O widget no menu lateral atualiza sua pontuação e feedback conforme o aluno dialoga e formula hipóteses na sessão.
4. **Testes Unitários:** A suíte `tests/test_caderno_and_analytics.py` valida com sucesso a montagem do Markdown e o cálculo das métricas.
5. **Git Commit & Push:** Commitar com a mensagem padronizada:  
   `feat(analytics): conclusao do plano 2 com caderno digital e termometro de retencao cognitiva v2.5.0`
