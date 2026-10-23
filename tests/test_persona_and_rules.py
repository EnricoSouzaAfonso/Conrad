import unittest
from unittest.mock import MagicMock, patch
from src.conrad_persona import (
    CONRAD_NAME,
    CONRAD_VERSION,
    CONRAD_ARCHETYPE,
    SYSTEM_INSTRUCTION_CONRAD,
    get_system_instruction,
)
from src.conrad_core import ConradEngine


class TestConradPersona(unittest.TestCase):
    def setUp(self):
        self.instruction = get_system_instruction()

    def test_metadados_persona(self):
        self.assertEqual(CONRAD_NAME, "Conrad")
        self.assertEqual(CONRAD_VERSION, "1.6.1")
        self.assertIn("Tutor Socrático", CONRAD_ARCHETYPE)
        self.assertEqual(self.instruction, SYSTEM_INSTRUCTION_CONRAD.strip())

    def test_regras_inviolaveis_presentes(self):
        self.assertIn("NUNCA proferir ofensas", self.instruction)
        self.assertIn("cartola vitoriana", self.instruction)

    def test_blindagem_mathjax_presente(self):
        self.assertIn("BUG DO MATHJAX", self.instruction)
        self.assertIn("PROIBIÇÃO DE CIFRÕES EM LINGUAGEM NATURAL", self.instruction)
        self.assertIn(r"\text{...}", self.instruction)

    def test_protocolo_3_passos_presente(self):
        self.assertIn("Passo 1 (Validação da Intenção)", self.instruction)
        self.assertIn("Passo 2 (Correção Suave e Firme)", self.instruction)
        self.assertIn("Passo 3 (Contextualização)", self.instruction)

    def test_encerramento_estrito_presente(self):
        self.assertIn("digite exatamente 'fim'", self.instruction)

    @patch("src.conrad_core.genai.Client")
    def test_integracao_core_default_system_instruction(self, mock_client_cls):
        engine = ConradEngine(api_key="TEST_KEY")
        self.assertEqual(engine.system_instruction, self.instruction)

    @patch("src.conrad_core.genai.Client")
    def test_pratico_mathjax_massa_energia_e_planck(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        mock_client.chats.create.return_value = mock_chat

        simulated_response = MagicMock()
        simulated_response.text = (
            "Antes de mergulharmos nas deduções, o que você já ouviu falar sobre a relação entre massa, energia e luz?\n\n"
            "Na Física Moderna, a equivalência massa-energia proposta por Einstein é expressa por:\n"
            "$$E = mc^2$$\n\n"
            "Já na Mecânica Quântica, a energia de um fóton é descrita pela equação de Planck:\n"
            "$$E = h\\nu$$\n\n"
            "Onde cada variável representa:\n"
            "- $E$: Energia total do sistema ou do fóton (em Joules);\n"
            "- $m$: Massa de repouso do corpo (em quilogramas);\n"
            "- $c$: Velocidade da luz no vácuo ($c \\approx 3 \\times 10^8\\text{ m/s}$);\n"
            "- $h$: Constante de Planck;\n"
            "- $\\nu$: Frequência da radiação eletromagnética (em Hertz)."
        )
        mock_chat.send_message.return_value = simulated_response

        engine = ConradEngine(api_key="TEST_KEY")
        resposta = engine.send_message("Explique a equivalência massa-energia e a equação de Planck")

        self.assertIn("$$E = mc^2$$", resposta)
        self.assertIn(r"$$E = h\nu$$", resposta)
        for var in ("$E$", "$m$", "$c$", "$h$", r"$\nu$"):
            self.assertIn(var, resposta)


if __name__ == "__main__":
    unittest.main()
