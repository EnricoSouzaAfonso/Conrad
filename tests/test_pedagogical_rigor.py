"""
Suíte de Testes de Rigor Pedagógico e Avaliação Heurística do Conrad v3.0.
Verifica Anti-Passividade, Sweller, Growth Mindset e Anti-Sycophancy.
"""
import unittest
import re
from src.conrad_persona import get_system_instruction, CONRAD_VERSION
from src.conrad_pedagogy import GROWTH_MINDSET_RULES, BLOOM_LEVELS, SWELLER_LOAD_RULES


class TestPedagogicalRigor(unittest.TestCase):
    def setUp(self):
        self.instruction = get_system_instruction("socratico")

    def test_versao_3_ativa(self):
        self.assertTrue(CONRAD_VERSION.startswith("3."), "A versão da persona deve pertencer à série 3.x")

    def test_regra_nao_passividade_presente(self):
        self.assertIn("REGRA DE OURO DA NÃO-PASSIVIDADE", self.instruction)
        self.assertIn("NUNCA forneça o gabarito final", self.instruction)

    def test_regra_pergunta_unica_sweller(self):
        self.assertIn("REGRA DA PERGUNTA ÚNICA", self.instruction)
        self.assertIn("EXATAMENTE UMA pergunta reflexiva", self.instruction)

    def test_proibicao_elogio_inteligencia_inata(self):
        self.assertIn("PROIBIÇÃO DE ELOGIOS À INTELIGÊNCIA INATA", self.instruction)
        self.assertIn('NUNCA diga frases como "Você é muito inteligente!"', self.instruction)
        self.assertIn("ELOGIO AO PROCESSO", self.instruction)

    def test_anti_sycophancy_presente(self):
        self.assertIn("ANTI-SYCOPHANCY", self.instruction)
        self.assertIn("Nunca concorde com um erro conceitual do aluno", self.instruction)

    def test_blindagem_latex_mantida(self):
        self.assertIn("TOLERÂNCIA ZERO A CIFRÕES EM PALAVRAS DA LÍNGUA PORTUGUESA", self.instruction)
        self.assertIn(r"\text{...}", self.instruction)

    def test_framework_bloom_e_sweller_estruturados(self):
        self.assertEqual(len(BLOOM_LEVELS), 6)
        self.assertEqual(BLOOM_LEVELS[1]["nome"], "Lembrar")
        self.assertEqual(BLOOM_LEVELS[6]["nome"], "Criar")
        self.assertGreaterEqual(len(GROWTH_MINDSET_RULES), 4)
        self.assertGreaterEqual(len(SWELLER_LOAD_RULES), 3)

    def test_heuristica_analise_resposta_mock(self):
        """Simula a validação de uma resposta hipotética do Conrad."""
        resposta_valida = (
            "Excelente reflexão! Note que quando derivamos em relação a x, a constante se anula. "
            "Qual regra de potenciação você utilizaria para o termo restante?"
        )
        # 1. Verifica se não há elogio inato proibido
        self.assertFalse(
            re.search(r"\b(você é um gênio|você é inteligente|muito esperto)\b", resposta_valida, re.I)
        )
        # 2. Verifica se há exatamente uma pergunta reflexiva
        interrogacoes = resposta_valida.count("?")
        self.assertEqual(interrogacoes, 1, "A resposta deve conter exatamente uma pergunta indutiva.")


if __name__ == "__main__":
    unittest.main()
