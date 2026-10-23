import unittest
from src.conrad_canvas import ConradArtifact
from src.conrad_report import ConradNotebookCompiler
from src.conrad_analytics import CognitiveRetentionTracker


class TestCadernoAndAnalytics(unittest.TestCase):
    def setUp(self):
        self.sample_messages = [
            {
                "role": "user",
                "content": "Olá Conrad, gostaria de entender como funciona o princípio da conservação de energia mecânica.",
            },
            {
                "role": "assistant",
                "content": "Pense em uma montanha-russa no topo de uma colina. Que tipo de energia ela possui ali?",
            },
            {
                "role": "user",
                "content": "Ela possui energia potencial gravitacional máxima porque está na altura máxima e parada.",
            },
            {
                "role": "assistant",
                "content": "Perfeito! E à medida que ela desce sem atrito, no que essa energia potencial se transforma?",
            },
        ]
        self.sample_artifacts = [
            ConradArtifact(
                artifact_type="math",
                title="Conservação da Energia Mecânica",
                content="$$E_m = E_c + E_p = \\frac{1}{2}mv^2 + mgh = \\text{constante}$$",
            ),
            ConradArtifact(
                artifact_type="mermaid",
                title="Conversão Energética",
                content="graph LR;\n    Ep[Energia Potencial] --> Ec[Energia Cinética];",
            ),
        ]

    def test_geracao_caderno_markdown_com_artifacts_e_flashcards(self):
        md = ConradNotebookCompiler.to_markdown(
            topic="Física Clássica",
            messages=self.sample_messages,
            artifacts=self.sample_artifacts,
        )
        self.assertIn("# 🎩 Caderno de Estudos do Conrad — Física Clássica", md)
        self.assertIn("### 📐 Conservação da Energia Mecânica (MATH)", md)
        self.assertIn("$$E_m = E_c + E_p", md)
        self.assertIn("```mermaid", md)
        self.assertIn("## 🧠 Flashcards para Revisão Rápida", md)
        self.assertIn("Qual foi o modelo mental central aprendido hoje?", md)

    def test_geracao_caderno_pdf_bytes_valido(self):
        pdf_bytes = ConradNotebookCompiler.to_pdf_bytes(
            topic="Física & Matemática <Avançada>",
            messages=self.sample_messages,
            artifacts=self.sample_artifacts,
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 500)

    def test_termometro_retencao_cognitiva_niveis(self):
        # 1. Sessão vazia
        stats_empty = CognitiveRetentionTracker.evaluate_session([])
        self.assertEqual(stats_empty["score"], 0)
        self.assertEqual(stats_empty["status"], "Iniciando")

        # 2. Sessão inicial / respostas curtas (Em Construção)
        stats_building = CognitiveRetentionTracker.evaluate_session(
            [{"role": "user", "content": "Não sei por onde começar"}]
        )
        self.assertEqual(stats_building["score"], 60)
        self.assertEqual(stats_building["status"], "Em Construção 🧱")

        # 3. Boa compreensão (>= 2 mensagens, média > 12 palavras)
        stats_good = CognitiveRetentionTracker.evaluate_session(self.sample_messages)
        self.assertEqual(stats_good["score"], 75)
        self.assertEqual(stats_good["status"], "Boa Compreensão 💡")

        # 4. Excelente autonomia (>= 4 mensagens do usuário, média > 25 palavras)
        long_user_msg = (
            "Eu compreendi que quando o sistema é conservativo e não há forças dissipativas como o atrito, "
            "a soma da energia cinética com a energia potencial gravitacional e elástica permanece constante em qualquer ponto da trajetória."
        )
        rich_session = [
            {"role": "user", "content": long_user_msg},
            {"role": "assistant", "content": "Ótimo!"},
            {"role": "user", "content": long_user_msg},
            {"role": "assistant", "content": "Continue!"},
            {"role": "user", "content": long_user_msg},
            {"role": "assistant", "content": "Muito bem!"},
            {"role": "user", "content": long_user_msg},
        ]
        stats_excellent = CognitiveRetentionTracker.evaluate_session(rich_session)
        self.assertEqual(stats_excellent["score"], 90)
        self.assertEqual(stats_excellent["status"], "Excelente Autonomia 🌟")


if __name__ == "__main__":
    unittest.main()
