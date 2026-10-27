"""
Suíte de Testes de Estresse, Caos e Casos Extremos (Chaos & Edge-Case Testing).
Valida a blindagem Zero-Crash do Projeto Conrad frente a entradas extremas (20k+ chars,
prompts vazios, emojis, bytes nulos, códigos corrompidos), falhas de API (429 Quota, Timeout)
e integridade do Quadro Negro (LaTeX complexo, Mermaid corrompido, tags truncadas e XSS).
"""
import unittest
from unittest.mock import MagicMock, patch

from src.conrad_core import ConradEngine, MSG_EMPTY_PROMPT, MAX_SAFE_PROMPT_CHARS
from src.conrad_canvas import CanvasParser, ConradArtifact
from src.conrad_report import ConradNotebookCompiler
from src.conrad_analytics import CognitiveRetentionTracker
from src.conrad_persona import get_missing_key_message


class TestChaosAndEdgeCases(unittest.TestCase):
    # ==========================================================================
    # 1. ENTRADAS EXTREMAS (Vazias, 20.000+ chars, Emojis, Bytes Nulos, Código Corrompido)
    # ==========================================================================
    @patch("src.conrad_core.genai.Client")
    def test_prompts_vazios_e_espacos_zero_crash(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        mock_client.chats.create.return_value = mock_chat

        engine = ConradEngine(api_key="AIzaSyValidKey123")
        for empty_input in ("", "   ", "\n\t\r  ", None, "\x00\x07"):
            reply = engine.send_message(empty_input)
            self.assertEqual(reply, MSG_EMPTY_PROMPT)

            stream_reply = "".join(engine.send_message_stream(empty_input))
            self.assertEqual(stream_reply, MSG_EMPTY_PROMPT)

        # Nenhuma chamada desnecessária deve ter sido disparada para a API com payload vazio
        mock_chat.send_message.assert_not_called()
        mock_chat.send_message_stream.assert_not_called()

    @patch("src.conrad_core.genai.Client")
    def test_prompt_25000_caracteres_emojis_e_truncamento_seguro(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        mock_resp = MagicMock(text="Análise socrática concluída com sucesso! 🎩")
        mock_chat.send_message.return_value = mock_resp
        mock_client.chats.create.return_value = mock_chat

        engine = ConradEngine(api_key="AIzaSyValidKey123")

        # 1. Texto extremo de 25.000 caracteres com múltiplos emojis e bytes de controle
        emoji_stream = "🎩🚀🧠📐🔥🔬🌌💡" * 500
        long_prompt_25k = ("Explique esta dedução: " + ("A" * 21000) + "\x00\x07" + emoji_stream)
        self.assertGreater(len(long_prompt_25k), 25000)

        res_25k = engine.send_message(long_prompt_25k)
        self.assertIn("Análise socrática concluída", res_25k)
        sent_arg = mock_chat.send_message.call_args[0][0]
        self.assertNotIn("\x00", sent_arg)
        self.assertIn("🎩🚀🧠", sent_arg)

        # 2. Texto colossal de 45.000 caracteres (acima de MAX_SAFE_PROMPT_CHARS = 32000)
        colossal_45k = "INICIO_CONTEXTO " + ("Z" * 45000) + " FIM_CONTEXTO"
        engine.send_message(colossal_45k)
        truncated_arg = mock_chat.send_message.call_args[0][0]
        self.assertLessEqual(len(truncated_arg), MAX_SAFE_PROMPT_CHARS)
        self.assertIn("INICIO_CONTEXTO", truncated_arg)
        self.assertIn("FIM_CONTEXTO", truncated_arg)
        self.assertIn("truncado automaticamente", truncated_arg)

    def test_codigo_sintaxe_corrompida_e_20k_chars_no_pdf_e_analytics(self):
        corrupted_code = (
            "def funcao_quebrada(x, y=\n"
            "    if x ====> 10 and (y + :\n"
            '        print("String nunca fechada \x00\x01\x07 <script>alert(1)</script></div>\n'
            "    return [[[}}}}\n"
        )
        unbreakable_22k = "X" * 22000 + " 🎩🚀🧠"

        chaos_messages = [
            {"role": "user", "content": unbreakable_22k},
            {"role": "assistant", "content": "Vamos depurar esse trecho passo a passo!"},
            None,  # Item nulo infiltrado na lista
            {"role": "user", "content": None},  # Conteúdo nulo
        ]
        chaos_artifacts = [
            ConradArtifact("code", "Código Corrompido <script> & </div>", corrupted_code),
            {"type": "math", "title": "Fórmula em Dict", "content": "$$E = mc^2$$"},
            None,
        ]

        # Analytics não pode quebrar com None ou strings gigantes
        stats = CognitiveRetentionTracker.evaluate_session(chaos_messages)
        self.assertIn("score", stats)
        self.assertGreaterEqual(stats["score"], 60)

        # Exportação Markdown e PDF não podem quebrar com bytes de controle, tags XML ou 22k chars
        md_out = ConradNotebookCompiler.to_markdown("Caos & <script>\x00", chaos_messages, chaos_artifacts)
        self.assertIn("Código Corrompido", md_out)

        pdf_bytes = ConradNotebookCompiler.to_pdf_bytes("Caos & <script>\x00", chaos_messages, chaos_artifacts)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 500)

    # ==========================================================================
    # 2. RESILIÊNCIA DA API E CHAVE (Timeout, 429 Sem Cota, Sem Chave — Zero Crash)
    # ==========================================================================
    @patch("src.conrad_core.genai.Client")
    def test_resiliencia_erro_429_chave_sem_cota_zero_crash(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        quota_exc = Exception("429 RESOURCE_EXHAUSTED: Quota exceeded for quota metric 'GenerateContent'")
        mock_chat.send_message.side_effect = quota_exc
        mock_chat.send_message_stream.side_effect = quota_exc
        mock_client.chats.create.return_value = mock_chat

        engine = ConradEngine(api_key="AIzaSyQuotaExhaustedKey")

        # send_message síncrono
        msg_sync = engine.send_message("Me explique cálculo diferencial")
        self.assertIn("429", msg_sync)
        self.assertIn("Limite de Requisições Atingido", msg_sync)

        # send_message_stream
        msg_stream = "".join(engine.send_message_stream("Me explique cálculo diferencial"))
        self.assertIn("429", msg_stream)
        self.assertIn("Limite de Requisições Atingido", msg_stream)

        # send_message_multimodal
        msg_multi = engine.send_message_multimodal("Analise esta foto", b"fake_img", "image/png")
        self.assertIn("429", msg_multi)

    @patch("src.conrad_core.genai.Client")
    def test_resiliencia_timeout_e_rede_zero_crash(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_chat = MagicMock()
        timeout_exc = TimeoutError("504 DEADLINE_EXCEEDED: Request timed out after 15000ms")
        mock_chat.send_message.side_effect = timeout_exc
        mock_chat.send_message_stream.side_effect = timeout_exc
        mock_client.chats.create.return_value = mock_chat

        engine = ConradEngine(api_key="AIzaSyValidKey")

        msg_sync = engine.send_message("O que é entropia?")
        self.assertIn("Timeout", msg_sync)

        msg_stream = "".join(engine.send_message_stream("O que é entropia?"))
        self.assertIn("Timeout", msg_stream)

        msg_multi = engine.send_message_multimodal("Foto de termodinâmica", b"bytes", "image/png")
        self.assertIn("Timeout", msg_multi)

    def test_multimodal_sem_api_key_zero_crash(self):
        with patch.object(ConradEngine, "_resolve_api_key", return_value=None):
            engine = ConradEngine(api_key="")
            res = engine.send_message_multimodal("Foto sem chave", b"123", "image/png")
            self.assertEqual(res, get_missing_key_message())

    # ==========================================================================
    # 3. INTEGRIDADE DA UI & CANVAS (LaTeX Complexo, Mermaid Corrompido, Tags Truncadas)
    # ==========================================================================
    def test_latex_complexo_matrizes_e_delimitadores_desbalanceados(self):
        # Fórmulas complexas com matrizes, integrais triplas, \left( sem \right) e $$ ímpar
        complex_math_raw = (
            '<conrad_artifact title="Tensor & Integral Tripla" type="math">\n'
            r"$$\iiint_V \left( \nabla \cdot \mathbf{F} \, dV = \oiint_S \mathbf{F} \cdot \mathbf{n} \, dS$$" "\n"
            r"\[\mathbf{A} = \begin{pmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{pmatrix}\]" "\n"
            "$$f(x) = x^2\n"  # $$ não fechado propositalmente
            "</conrad_artifact>"
        )
        clean_chat, artifact = CanvasParser.parse_message(complex_math_raw)
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.type, "math")
        self.assertEqual(artifact.title, "Tensor & Integral Tripla")
        # Verifica que número de $$ agora é par
        self.assertEqual(artifact.content.count("$$") % 2, 0)
        # Verifica que \left recebeu \right. correspondente
        self.assertIn(r"\right.", artifact.content)
        self.assertIn(r"\begin{pmatrix}", artifact.content)

    def test_mermaid_com_erro_de_sintaxe_auto_reparo(self):
        # Diagrama Mermaid sem cabeçalho graph/flowchart e com colchetes/parênteses não fechados
        corrupted_mermaid = (
            "```mermaid\n"
            "A[Início do Algoritmo --> B( Validação de Dados\n"
            "B --> C{Dados Válidos?\n"
            "C --> D[Processamento Concluído]\n"
            "```"
        )
        repaired, is_clean, warn = CanvasParser.validate_and_repair_mermaid(corrupted_mermaid)
        self.assertFalse(is_clean)
        self.assertIsNotNone(warn)
        self.assertTrue(repaired.startswith("flowchart TD"))
        self.assertIn("A[Início do Algoritmo] --> B( Validação de Dados)", repaired)
        self.assertIn("B --> C{Dados Válidos?}", repaired)

    def test_artifact_e_thought_truncados_sem_tag_de_fechamento(self):
        # Simula corte de streaming no meio do <think> e no meio do <conrad_artifact>
        truncated_thought_msg = "<think>Raciocínio cortado pela metade sem tag final"
        clean_t, thought = CanvasParser.parse_thought(truncated_thought_msg)
        self.assertEqual(clean_t, "")
        self.assertIn("Raciocínio cortado", thought)

        truncated_artifact_msg = (
            "Observe a dedução no Quadro Negro:\n"
            '<conrad_artifact type="math" title="Equação Truncada">\n'
            "$$\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$"
        )
        clean_chat, art = CanvasParser.parse_message(truncated_artifact_msg)
        self.assertEqual(clean_chat, "Observe a dedução no Quadro Negro:")
        self.assertIsNotNone(art)
        self.assertEqual(art.type, "math")
        self.assertEqual(art.title, "Equação Truncada")
        self.assertIn("\\frac{\\sqrt{\\pi}}{2}", art.content)


if __name__ == "__main__":
    unittest.main()
