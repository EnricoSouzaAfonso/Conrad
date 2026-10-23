import unittest
from unittest.mock import patch
from src.conrad_persona import (
    PEDAGOGICAL_MODES,
    SYSTEM_INSTRUCTION_CONRAD,
    get_system_instruction,
)
from src.conrad_core import ConradEngine


class TestPedagogicalModes(unittest.TestCase):
    def test_quatro_modos_pedagogicos_definidos(self):
        expected_modes = {"socratico", "simulado", "engenharia", "feynman"}
        self.assertEqual(set(PEDAGOGICAL_MODES.keys()), expected_modes)
        for key, mode_data in PEDAGOGICAL_MODES.items():
            self.assertIn("nome", mode_data)
            self.assertIn("descricao", mode_data)
            self.assertIn("diretriz", mode_data)
            self.assertTrue(len(mode_data["diretriz"].strip()) > 20)

    def test_geracao_instrucao_dinamica_por_modo(self):
        inst_socratico = get_system_instruction("socratico")
        self.assertIn("[MODO ATIVO: SOCRÁTICO PURO]", inst_socratico)
        self.assertIn(SYSTEM_INSTRUCTION_CONRAD.strip(), inst_socratico)

        inst_simulado = get_system_instruction("simulado")
        self.assertIn("[MODO ATIVO: SIMULADO & DESAFIO]", inst_simulado)
        self.assertIn("examinador rigoroso", inst_simulado)

        inst_engenharia = get_system_instruction("engenharia")
        self.assertIn("[MODO ATIVO: ARQUITETO DE SOFTWARE]", inst_engenharia)
        self.assertIn("Big-O notation", inst_engenharia)

        inst_feynman = get_system_instruction("feynman")
        self.assertIn("[MODO ATIVO: MÉTODO FEYNMAN]", inst_feynman)
        self.assertIn("12 anos", inst_feynman)

    def test_fallback_modo_invalido_para_socratico(self):
        inst_default = get_system_instruction("modo_inexistente")
        self.assertIn("[MODO ATIVO: SOCRÁTICO PURO]", inst_default)

    @patch("src.conrad_core.genai.Client")
    def test_alternancia_modo_no_engine_em_tempo_real(self, mock_client_cls):
        engine = ConradEngine(api_key="TEST_KEY")
        self.assertEqual(engine.pedagogical_mode, "socratico")
        self.assertIn("[MODO ATIVO: SOCRÁTICO PURO]", engine.system_instruction)

        for mode_key in ("simulado", "engenharia", "feynman", "socratico"):
            engine.set_pedagogical_mode(mode_key)
            self.assertEqual(engine.pedagogical_mode, mode_key)
            self.assertIn(PEDAGOGICAL_MODES[mode_key]["diretriz"].strip(), engine.system_instruction)


if __name__ == "__main__":
    unittest.main()
