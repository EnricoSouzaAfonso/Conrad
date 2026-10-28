# 📋 Especificação Técnica de Engenharia — Plano 7: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 7 — Governança Documental, Sincronização de READMEs e Auditoria de Releases  
**Etapa:** Fase 2 — Protocolo Permanente de Governança Documental e Checklist de Release  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diretriz Estratégica: A Lei da Sincronização Documental

### 1.1. O Princípio Operacional
Um software com documentação desatualizada é, para todos os efeitos práticos, um software quebrado para o usuário final e para potenciais compradores institucionais.
A partir deste plano, fica instituída a **Lei de Governança Documental do Conrad**:
> **"Nenhuma nova funcionalidade, refatoração de código ou mudança de versão será considerada concluída sem que o `README(PT-BR).md`, o `README(ENG).md` e o `CHANGELOG.md` tenham sido atualizados em sincronia exata antes do commit."**

---

## 2. Arquivos Afetados
* **Modificar:** `tests/qa_visual_inspection.py` (Adicionar verificação programática que audita a versão do projeto contra o `CHANGELOG.md` e a integridade dos READMEs).
* **Modificar:** `CHANGELOG.md` (Registrar versão 3.3.1 — Automação de Governança Documental).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Verificador Automatizado de Documentação no `tests/qa_visual_inspection.py`
O Argon deve adicionar ao script de QA a etapa de auditoria de consistência documental:

```python
def check_documentation_sync():
    """Valida se as versões e os READMEs estão sincronizados com o código."""
    print("\n[Auditoria Documental] Verificando sincronização de versões e READMEs...")
    
    # 1. Captura versão da persona
    from src.conrad_persona import CONRAD_VERSION
    
    # 2. Verifica se a versão consta no CHANGELOG.md
    changelog_path = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")
    assert os.path.isfile(changelog_path), "Erro: CHANGELOG.md não encontrado!"
    with open(changelog_path, "r", encoding="utf-8") as f:
        changelog_content = f.read()
    assert f"[{CONRAD_VERSION}]" in changelog_content, (
        f"Falha de Governança: A versão {CONRAD_VERSION} declarada em src/conrad_persona.py "
        f"não está registrada no CHANGELOG.md!"
    )

    # 3. Verifica existência e integridade dos READMEs bilíngues
    readme_pt_path = os.path.join(os.path.dirname(__file__), "..", "README(PT-BR).md")
    readme_en_path = os.path.join(os.path.dirname(__file__), "..", "README(ENG).md")
    assert os.path.isfile(readme_pt_path), "Erro: README(PT-BR).md não encontrado!"
    assert os.path.isfile(readme_en_path), "Erro: README(ENG).md não encontrado!"

    with open(readme_pt_path, "r", encoding="utf-8") as f:
        pt_content = f.read()
    with open(readme_en_path, "r", encoding="utf-8") as f:
        en_content = f.read()

    # Valida presença das tecnologias vigentes em ambos
    for tech in ("gemini", "streamlit", "fastapi"):
        assert tech in pt_content.lower(), f"Falha no README(PT-BR): '{tech}' não mencionado!"
        assert tech in en_content.lower(), f"Falha no README(ENG): '{tech}' não mencionado!"

    print("✅ Governança Documental APROVADA: Versões, Changelog e READMEs 100% sincronizados!")
    return True
```

---

### 3.2. Checklist Obrigatório de Release para o Argon
A cada nova entrega ou release, o Argon deve incluir a seção de documentação no seu relatório de QA:

```markdown
### 📚 Checklist de Governança Documental
* [x] **Incremento SemVer:** `CONRAD_VERSION` em `src/conrad_persona.py` atualizado conforme o escopo da mudança.
* [x] **Changelog Registrado:** `CHANGELOG.md` documentou as adições e correções na versão correspondente.
* [x] **README(PT-BR).md Atualizado:** Guia de uso, tecnologias e funcionalidades conferidas em português.
* [x] **README(ENG).md Atualizado:** Versão em inglês espelhada sem defasagem de conteúdo.
* [x] **Auditoria de Código:** O que foi escrito na documentação foi testado empiricamente no sistema.
```

---

## 4. Critério de Validação (Definition of Done)
1. **Passagem na Auditoria:** O comando `python tests/qa_visual_inspection.py` roda e confirma a sincronia documental sem erros de assert.
2. **Commit & Push:** Commitar com a mensagem padronizada:  
   `ci(governance): automacao de auditoria documental e sincronizacao de releases`
