import unittest
from src.conrad_canvas import CanvasParser, ConradArtifact
from src.conrad_persona import get_system_instruction, CONRAD_VERSION


class TestCanvasArtifacts(unittest.TestCase):
    def test_persona_possui_protocolo_quadro_negro(self):
        instruction = get_system_instruction()
        self.assertEqual(CONRAD_VERSION, "2.2.0")
        self.assertIn("O QUADRO NEGRO DO CONRAD (PROTOCOL DE ARTIFACTS / CANVAS)", instruction)
        self.assertIn('<conrad_artifact type="math|code|mermaid|summary"', instruction)

    def test_extracao_artifact_math_bernoulli(self):
        raw_message = (
            "Excelente pergunta sobre hidrodinâmica! Imagine um fluido incompressível escoando por uma tubulação que muda de altura e diâmetro. "
            "Projetei a equação de conservação de energia de Bernoulli no nosso Quadro Negro ao lado. "
            "O que acontece com a pressão estática quando a velocidade do fluido aumenta?\n\n"
            '<conrad_artifact type="math" title="Equação de Bernoulli em Hidrodinâmica">\n'
            r"$$P + \frac{1}{2}\rho v^2 + \rho g h = \text{constante}$$" "\n"
            "Onde:\n"
            "- $P$: Pressão estática do fluido (em Pascal);\n"
            r"- $\rho$: Massa específica do fluido ($\text{kg/m}^3$);" "\n"
            "- $v$: Velocidade de escoamento ($\\text{m/s}$);\n"
            "- $g$: Aceleração da gravidade ($\\text{m/s}^2$);\n"
            "- $h$: Altura em relação ao referencial ($\\text{m}$).\n"
            "</conrad_artifact>"
        )

        clean_chat, artifact = CanvasParser.parse_message(raw_message)

        self.assertIsNotNone(artifact)
        self.assertIsInstance(artifact, ConradArtifact)
        self.assertEqual(artifact.type, "math")
        self.assertEqual(artifact.title, "Equação de Bernoulli em Hidrodinâmica")
        self.assertIn(r"$$P + \frac{1}{2}\rho v^2 + \rho g h = \text{constante}$$", artifact.content)
        self.assertNotIn("<conrad_artifact", clean_chat)
        self.assertNotIn("$$P", clean_chat)
        self.assertIn("O que acontece com a pressão estática", clean_chat)

    def test_extracao_artifact_mermaid(self):
        raw_message = (
            "Para visualizar as etapas do ciclo termodinâmico de Carnot, desenhei um fluxograma no Quadro Negro ao lado!\n\n"
            "<conrad_artifact type='mermaid' title='Ciclo de Carnot'>\n"
            "graph TD;\n"
            "    A[Expansão Isotérmica] --> B[Expansão Adiabática];\n"
            "    B --> C[Compressão Isotérmica];\n"
            "    C --> D[Compressão Adiabática];\n"
            "    D --> A;\n"
            "</conrad_artifact>"
        )

        clean_chat, artifact = CanvasParser.parse_message(raw_message)

        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.type, "mermaid")
        self.assertEqual(artifact.title, "Ciclo de Carnot")
        self.assertIn("graph TD;", artifact.content)
        self.assertNotIn("<conrad_artifact", clean_chat)
        self.assertEqual(
            clean_chat,
            "Para visualizar as etapas do ciclo termodinâmico de Carnot, desenhei um fluxograma no Quadro Negro ao lado!",
        )

    def test_extracao_artifact_code_e_summary(self):
        raw_code_msg = (
            "Observe a estrutura recursiva que coloquei no Quadro Negro:\n"
            '<conrad_artifact type="code" title="Busca Binária Recursiva">\n'
            "def busca_binaria(lista, alvo, ini, fim):\n"
            "    if ini > fim:\n"
            "        return -1\n"
            "</conrad_artifact>"
        )
        clean_chat, artifact = CanvasParser.parse_message(raw_code_msg)
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.type, "code")
        self.assertEqual(artifact.title, "Busca Binária Recursiva")
        self.assertIn("def busca_binaria", artifact.content)
        self.assertEqual(clean_chat, "Observe a estrutura recursiva que coloquei no Quadro Negro:")

    def test_fallback_quando_mensagem_possui_apenas_artifact(self):
        raw_only_artifact = (
            '<conrad_artifact type="summary" title="Resumo de Eletromagnetismo">\n'
            "- Lei de Gauss\n- Lei de Faraday\n"
            "</conrad_artifact>"
        )
        clean_chat, artifact = CanvasParser.parse_message(raw_only_artifact)
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.type, "summary")
        self.assertEqual(clean_chat, "*(Conteúdo projetado no Quadro Negro ao lado 🎩)*")

    def test_resiliencia_mensagens_normais_sem_artifact(self):
        normal_msg = "Olá! Que ótimo ter você por aqui. Qual tópico de Física ou Programação vamos explorar hoje?"
        clean_chat, artifact = CanvasParser.parse_message(normal_msg)
        self.assertIsNone(artifact)
        self.assertEqual(clean_chat, normal_msg)

    def test_extracao_pensamento_cot(self):
        raw_with_thought = (
            "<think>O aluno está confundindo velocidade média com instantânea. Vou usar o exemplo do velocímetro.</think>\n"
            "Quando você olha para o velocímetro de um carro em uma curva, o que ele mede naquele exato instante?"
        )
        text_without_thought, thought = CanvasParser.parse_thought(raw_with_thought)
        self.assertEqual(
            thought,
            "O aluno está confundindo velocidade média com instantânea. Vou usar o exemplo do velocímetro.",
        )
        self.assertEqual(
            text_without_thought,
            "Quando você olha para o velocímetro de um carro em uma curva, o que ele mede naquele exato instante?",
        )


if __name__ == "__main__":
    unittest.main()
