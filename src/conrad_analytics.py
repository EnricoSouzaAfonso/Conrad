"""
Módulo de Métricas e Termômetro de Retenção Cognitiva.
Avalia o grau de autonomia, engajamento e tema ativo do estudante durante a sessão socrática.
"""
from typing import List, Dict, Any, Optional


class CognitiveRetentionTracker:
    @classmethod
    def infer_active_topic(cls, messages: Optional[List[Dict[str, Any]]]) -> str:
        """Extrai um resumo conciso do tema ativo a partir da última interação do estudante."""
        safe_msgs = [m for m in (messages or []) if isinstance(m, dict) and m.get("role") == "user"]
        if not safe_msgs:
            return "Exploratório / Multidisciplinar"
        last_text = str(safe_msgs[-1].get("content") or "").strip()
        if not last_text or last_text.lower() == "fim":
            return "Exploratório / Multidisciplinar"
        words = last_text.split()
        snippet = " ".join(words[:6])
        return f"{snippet}..." if len(words) > 6 else snippet

    @classmethod
    def evaluate_session(cls, messages: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calcula o índice de autonomia e retenção cognitiva da sessão com resiliência a entradas vazias/nulas."""
        safe_msgs = [m for m in (messages or []) if isinstance(m, dict)]
        active_topic = cls.infer_active_topic(safe_msgs)
        total_user_msgs = sum(1 for m in safe_msgs if m.get("role") == "user")
        if total_user_msgs == 0:
            return {
                "score": 0,
                "status": "Iniciando",
                "feedback": "Envie sua primeira dúvida!",
                "active_topic": active_topic,
            }

        # Medição heurística baseada no engajamento e tamanho médio de resposta do aluno
        user_words = sum(
            len(str(m.get("content") or "").split())
            for m in safe_msgs
            if m.get("role") == "user"
        )
        avg_words = user_words / total_user_msgs

        if avg_words > 25 and total_user_msgs >= 4:
            score = 90
            status = "Excelente Autonomia 🌟"
            feedback = (
                "Você articulou explicações ricas com suas próprias palavras. "
                "O modelo mental foi assimilado com solidez!"
            )
        elif avg_words > 12 and total_user_msgs >= 2:
            score = 75
            status = "Boa Compreensão 💡"
            feedback = (
                "Você acompanhou bem os andaimes cognitivos. "
                "Experimente praticar mais exercícios para consolidar."
            )
        else:
            score = 60
            status = "Em Construção 🧱"
            feedback = (
                "O conceito foi introduzido. Continue questionando e "
                "explorando as analogias do Conrad!"
            )

        return {
            "score": score,
            "status": status,
            "feedback": feedback,
            "active_topic": active_topic,
        }
