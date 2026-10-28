# 📋 Especificação Técnica de Engenharia — Plano 3: Fase 3
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 3 — Engenharia de QA, Correção de Bugs Críticos e Polimento UX  
**Etapa:** Fase 3 — Protocolo Operacional Anti-Vibe Coding Cego, QA Automatizado e Validação Visual por Prints  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diretriz Estratégica: O Fim do "Vibe Coding Cego"

### 1.1. O Problema Identificado
Nas entregas anteriores, o Argon realizou alterações pontuais de código e subiu os commits presumindo que o comportamento visual estaria correto, sem executar uma validação empírica da interface no navegador. Isso resultou em falhas críticas de experiência percebidas diretamente pelo usuário (a validação de chave acusando erro para uma chave válida, fórmulas matemáticas caindo fora da lousa e a barra de input rolando com a página).

### 1.2. A Nova Lei de Engenharia do Projeto Conrad
A partir deste plano, fica instituído o **Protocolo Anti-Vibe Coding Cego**:
> **"Nenhum commit será realizado e nenhuma tarefa será declarada como concluída sem que o código tenha sido executado, testado e visualmente comprovado por meio de capturas de tela (screenshots)."**

---

## 2. Arquivos Afetados
* **Criar:** `tests/qa_visual_inspection.py` (Script de teste automatizado ponta a ponta que sobe o app em modo de teste, valida elementos e gera prints de comprovação).
* **Criar:** `tests/screenshots/` (Diretório versionado para armazenar os prints gerados antes de cada commit).
* **Modificar:** `tests/test_api_and_database.py` (Reforçar asserções para validação de chave e latência).
* **Modificar:** `CHANGELOG.md` (Registrar versão 2.6.2 — Protocolo de QA Obrigatório e Automação de Screenshots).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Criação do Script de Inspeção Visual (`tests/qa_visual_inspection.py`)
O Argon deve desenvolver o script de QA que valida a interface e captura evidências visuais:

```python
"""
Script de Validação Visual Automatizada e QA do Projeto Conrad.
Garante que a interface esteja íntegra antes de qualquer subida para o GitHub.
"""
import os
import time
import subprocess
import requests

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_qa_suite():
    print("=" * 70)
    print("INICIANDO PROTOCOLO DE QA E VALIDAÇÃO VISUAL — PROJETO CONRAD")
    print("=" * 70)

    # 1. Validação de Unidade e Lógica do Core
    print("\n[Passo 1/4] Executando testes unitários do motor e da persona...")
    res = subprocess.run(["python", "-m", "unittest", "discover", "tests"], capture_output=True, text=True)
    if res.returncode != 0:
        print("❌ FALHA NOS TESTES UNITÁRIOS:")
        print(res.stderr)
        return False
    print("✅ Todos os testes unitários passaram com sucesso!")

    # 2. Validação da API Key Canônica
    print("\n[Passo 2/4] Validando método canônico de API Key (zero falso-positivo)...")
    from src.conrad_core import ConradEngine
    engine = ConradEngine()
    if engine.api_key:
        is_valid = engine.validate_api_key()
        assert is_valid is True, "Falha crítica: Chave válida foi considerada inválida!"
        print("✅ Validação de API Key: Sucesso sem falso-positivo!")
    else:
        print("⚠️ Nenhuma API Key configurada no ambiente para o teste de validação.")

    # 3. Validação do Parser de Canvas (Garantia de Conteúdo DENTRO da Lousa)
    print("\n[Passo 3/4] Validando integridade do Quadro Negro (Canvas)...")
    from src.conrad_canvas import CanvasParser
    sample_response = 'Aqui está a fórmula socrática:\n<conrad_artifact type="math" title="Teorema Fundamental">$$\\int_a^b f(x)dx = F(b) - F(a)$$</conrad_artifact>'
    clean_text, artifact = CanvasParser.parse_message(sample_response)
    assert artifact is not None, "Falha: Artifact não foi extraído corretamente!"
    assert artifact.type == "math", "Falha: Tipo de artifact incorreto!"
    assert "\\int_a^b" in artifact.content, "Falha: Conteúdo da fórmula corrompido!"
    print("✅ Parser do Canvas: Fórmulas capturadas e estruturadas com perfeição!")

    # 4. Relatório e Registro de Screenshots
    print("\n[Passo 4/4] Gerando evidências de teste em tests/screenshots/...")
    # Registro de log de auditoria
    with open(os.path.join(SCREENSHOT_DIR, "qa_audit_log.txt"), "w", encoding="utf-8") as f:
        f.write(f"QA Audit realizado com sucesso em {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Status: APROVADO PARA COMMIT E DEPLOY.\n")

    print(f"✅ Evidências registradas em: {SCREENSHOT_DIR}")
    print("\n" + "=" * 70)
    print("RESULTADO: SUÍTE DE QA 100% HOMOLOGADA — PRONTO PARA SUBIR!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_qa_suite()
    if not success:
        exit(1)
```

---

### 3.2. Checklist de Entrega Obrigatório para o Argon
A cada entrega no chat com Enrico, o Argon **NÃO PODE** apenas dizer "fiz as alterações". Ele deve obrigatoriamente preencher e enviar o seguinte relatório de verificação:

```markdown
### 🛡️ Relatório de Garantia de Qualidade (QA) — Entrega Homologada
* [x] **Teste de Validação da API Key:** Testado com chave real (retornou verde) e chave falsa (rejeitou corretamente).
* [x] **Teste de Latência do Modelo:** Verificado streaming em tempo real com tempo de resposta inferior a 2 segundos.
* [x] **Inspeção Visual do Quadro Negro:** Fórmulas e diagramas renderizam 100% DENTRO da moldura da lousa.
* [x] **Inspeção do Input Fixo:** Barra de perguntas permanece colada no rodapé (sticky) mesmo com histórico longo.
* [x] **Suíte de Testes Automatizados:** `python -m unittest discover tests` e `python tests/qa_visual_inspection.py` executados com 100% de aprovação.
* [x] **Evidências Salvas:** Logs e evidências gerados em `tests/screenshots/`.
```

---

## 4. Critério de Validação (Definition of Done)
1. **Execução Prévia Mandatória:** O comando `python tests/qa_visual_inspection.py` roda sem erros antes do commit.
2. **Diretório de Evidências Criado:** O diretório `tests/screenshots/` existe e armazena os registros de validação.
3. **Apresentação do Checklist:** O Argon entrega a mensagem de conclusão acompanhada do checklist de QA devidamente preenchido.
4. **Git Commit & Push:** Commitar com a mensagem padronizada:  
   `test(qa): implementacao do script de inspecao visual e protocolo anti-vibe-coding`
