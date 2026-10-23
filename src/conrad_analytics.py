"""
Módulo de Métricas e Termômetro de Retenção Cognitiva.
Avalia o grau de autonomia e engajamento do estudante durante a sessão socrática.
"""
from typing import List, Dict, Any


class CognitiveRetentionTracker:
    @classmethod
    def evaluate_session(cls, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula o índice de autonomia e retenção cognitiva da sessão."""
        total_user_msgs = sum(1 for m in messages if m.get("role") == "user")
        if total_user_msgs == 0:
            return {
                "score": 0,
                "status": "Iniciando",
                "feedback": "Envie sua primeira dúvida!",
            }

        # Medição heurística baseada no engajamento e tamanho médio de resposta do aluno
        user_words = sum(
            len(str(m.get("content", "")).split())
            for m in messages
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

        return {"score": score, "status": status, "feedback": feedback}
