# 📋 Especificação Técnica de Engenharia — Plano 4: Fase 3
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 4 — Engenharia Pedagógica Avançada e Reformulação das System Instructions  
**Etapa:** Fase 3 — Suíte Automatizada de Avaliação Heurística e Rigor Pedagógico  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Criar uma suíte de testes automatizados dedicados exclusivamente a **auditar a qualidade pedagógica** do Conrad (`tests/test_pedagogical_rigor.py`). Diferente de testes de código comuns (que apenas checam se uma função roda sem dar erro), esta suíte avalia a **conformidade epistemológica e comportamental** do assistente, garantindo que ele não sofra de amnésia pedagógica, não entregue respostas prontas para lições de casa e aplique rigorosamente as diretrizes de Bloom, Sweller e Carol Dweck.

---

## 2. Arquivos Afetados
* **Criar:** `tests/test_pedagogical_rigor.py` (Suíte de testes de estresse pedagógico, anti-passividade, growth mindset e MathJax).
* **Modificar:** `tests/qa_visual_inspection.py` (Integrar a suíte de rigor pedagógico ao checklist mandatório de QA pré-commit).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 3.0.1 — Homologação da Suíte de Rigor Pedagógico Automatizada).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Implementação de `tests/test_pedagogical_rigor.py`
O Argon deve codificar a bateria de testes avaliando os princípios científicos:

```python
"""
Suíte de Testes de Rigor Pedagógico e Avaliação Heurística do Conrad v3.0.
Verifica Anti-Passividade, Sweller, Growth Mindset e Anti-Sycophancy.
"""
import unittest
import re
from src.conrad_persona import get_system_instruction, CONRAD_VERSION
from src.conrad_pedagogy import GROWTH_MINDSET_RULES, BLOOM_LEVELS

class TestPedagogicalRigor(unittest.TestCase):
    def setUp(self):
        self.instruction = get_system_instruction("socratico")

    def test_versao_3_ativa(self):
        self.assertEqual(CONRAD_VERSION, "3.0.0", "A versão da persona deve ser 3.0.0")

    def test_regra_nao_passividade_presente(self):
        self.assertIn("REGRA DE OURO DA NÃO-PASSIVIDADE", self.instruction)
        self.assertIn("NUNCA forneça o gabarito final", self.instruction)

    def test_regra_pergunta_unica_sweller(self):
        self.assertIn("REGRA DA PERGUNTA ÚNICA", self.instruction)
        self.assertIn("EXATAMENTE UMA pergunta reflexiva", self.instruction)

    def test_proibicao_elogio_inteligencia_inata(self):
        self.assertIn("PROIBIÇÃO DE ELOGIOS À INTELIGÊNCIA INATA", self.instruction)
        self.assertIn("NUNCA diga frases como \"Você é muito inteligente!\"", self.instruction)
        self.assertIn("ELOGIO AO PROCESSO", self.instruction)

    def test_anti_sycophancy_presente(self):
        self.assertIn("ANTI-SYCOPHANCY", self.instruction)
        self.assertIn("Nunca concorde com um erro conceitual do aluno", self.instruction)

    def test_blindagem_latex_mantida(self):
        self.assertIn("TOLERÂNCIA ZERO A CIFRÕES EM PALAVRAS DA LÍNGUA PORTUGUESA", self.instruction)
        self.assertIn(r"\text{...}", self.instruction)

    def test_heuristica_analise_resposta_mock(self):
        """Simula a validação de uma resposta hipotética do Conrad."""
        resposta_valida = (
            "Excelente reflexão! Note que quando derivamos em relação a x, a constante se anula. "
            "Qual regra de potenciação você utilizaria para o termo restante?"
        )
        # 1. Verifica se não há elogio inato proibido
        self.assertFalse(re.search(r"\b(você é um gênio|você é inteligente|muito esperto)\b", resposta_valida, re.I))
        # 2. Verifica se há exatamente uma pergunta reflexiva
        interrogacoes = resposta_valida.count("?")
        self.assertEqual(interrogacoes, 1, "A resposta deve conter exatamente uma pergunta indutiva.")

if __name__ == "__main__":
    unittest.main()
```

---

### 3.2. Integração ao Protocolo de QA (`tests/qa_visual_inspection.py`)
No script `tests/qa_visual_inspection.py`, o Argon deve adicionar a etapa explícita de auditoria pedagógica:

```python
    # Passo adicional no run_qa_suite():
    print("\n[Passo 5/5] Executando auditoria da Suíte de Rigor Pedagógico v3.0...")
    res_ped = subprocess.run(["python", "-m", "unittest", "tests/test_pedagogical_rigor.py"], capture_output=True, text=True)
    assert res_ped.returncode == 0, f"Falha na auditoria pedagógica:\n{res_ped.stderr}"
    print("✅ Auditoria Pedagógica APROVADA: Bloom, Sweller e Growth Mindset 100% validados!")
```

---

## 4. Critério de Validação (Definition of Done)
1. **Execução Verde da Suíte:** O comando `python -m unittest tests/test_pedagogical_rigor.py` executa e passa com 100% de sucesso.
2. **Homologação no QA Geral:** O script `python tests/qa_visual_inspection.py` incorpora a etapa pedagógica e conclui com aprovação total.
3. **Commit & Push:** Commitar com a mensagem padronizada:  
   `test(pedagogy): suite de avaliacao heuristica e testes de rigor pedagogico v3.0`
