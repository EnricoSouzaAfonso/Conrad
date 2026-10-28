# 📋 Especificação Técnica de Engenharia — Plano 8: Fase 5
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 8 — Gems Pedagógicas Customizáveis, Upload Integrado e Refinamento de UX/UI  
**Etapa:** Fase 5 — Blindagem de Concorrência nos Downloads, Suite de QA e Governança Documental  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. Cliques Concorrentes nos Botões de Download Durante Geração da IA
* **Sintoma Relatado pelo Usuário:** Enquanto o Conrad está processando o streaming da resposta ou pensando, os botões *"Baixar resumo"* e *"Baixar caderno"* escurecem visualmente, mas o navegador ainda aceita o clique do usuário. Quando a resposta termina ou durante o streaming, esse clique enfileirado dispara um recarregamento concorrente indesejado da página no Streamlit.
* **Causa Raiz:**
  1. A propriedade `disabled` não estava sendo vinculada a uma flag reativa de controle de ciclo de vida (`is_generating`).
  2. No Streamlit, a camada de eventos HTML continua ouvindo cliques se a classe CSS do botão não tiver `pointer-events: none !important`.

### 1.2. Governança e Validação Contínua
* Conforme instituído no **Plano 7 (Governança Documental)**, nenhuma versão sobe para release sem suite de testes automatizados completa e sem a sincronização dos READMEs bilíngues (`README(PT-BR).md` e `README.md`) e do `CHANGELOG.md`.

---

## 2. Arquivos Afetados
* **Modificar:** `app.py` (Implementar a flag `is_generating`, o atributo `disabled` nos download buttons e a trava CSS via `pointer-events: none`).
* **Criar:** `tests/test_plano8.py` (Suite completa de testes automatizados cobrindo Perfil Neutro, CRUD de Gems, Injeção de Prompt e Prevenção de Concorrência).
* **Modificar:** `CHANGELOG.md`, `README(PT-BR).md` e `README.md` (Atualizar para a versão v3.4.0 documentando o CRUD de Gems e Upload Integrado).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Blindagem de Estado e CSS no `app.py`
1. Inicializar o estado reativo:
```python
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
```

2. Adicionar regra de CSS para bloquear cliques físicos no nível do ponteiro do mouse durante geração:
```css
/* Bloqueio absoluto de clique físico nos botões de download durante geração */
.generating-active button[kind="primary"],
.generating-active [data-testid="stDownloadButton"] button {
    pointer-events: none !important;
    opacity: 0.40 !important;
    cursor: not-allowed !important;
}
```

3. No fluxo de envio da mensagem:
```python
if prompt:
    st.session_state.is_generating = True
    try:
        # Execução do streaming ou multimodal...
        ...
    finally:
        st.session_state.is_generating = False
```

4. Nos botões de download no rodapé da lousa:
```python
is_busy = st.session_state.get("is_generating", False)

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.download_button(
        "📥 Baixar Resumo (.md)",
        data=md_data,
        file_name="caderno_conrad.md",
        mime="text/markdown",
        use_container_width=True,
        disabled=is_busy,
    )
with col_d2:
    st.download_button(
        "📄 Baixar Caderno (.pdf)",
        data=pdf_data,
        file_name="caderno_conrad.pdf",
        mime="application/pdf",
        use_container_width=True,
        disabled=is_busy,
    )
```

---

### 3.2. Suite de Testes de Engenharia (`tests/test_plano8.py`)
Criar o arquivo de testes automatizados com cobertura rigorosa:

```python
"""
Suite de Testes Automatizados — Plano 8
Validação de Perfil Neutro, CRUD de Gems Pedagógicas, Injeção Dinâmica e Blindagem de Concorrência.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import (
    Base,
    get_or_create_profile,
    reset_profile_to_default,
    seed_default_gems,
    get_all_gems,
    create_custom_gem,
    update_custom_gem,
    delete_custom_gem,
    DEFAULT_STRENGTHS,
    DEFAULT_DIFFICULTIES,
)
from src.conrad_persona import get_system_instruction

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()
    seed_default_gems(db)
    yield db
    db.close()

def test_perfil_cognitivo_multidisciplinar(test_db):
    profile = get_or_create_profile(test_db)
    # Garante que não possui viés hardcoded de álgebra
    assert "álgebra" not in profile.strengths.lower()
    assert "equações" not in profile.difficulties.lower()
    assert profile.strengths == DEFAULT_STRENGTHS

def test_migracao_perfil_antigo(test_db):
    # Simula perfil antigo com texto de álgebra
    profile = get_or_create_profile(test_db)
    profile.strengths = "Introdução à álgebra"
    profile.difficulties = "Identificação de variáveis em equações"
    test_db.commit()

    # Reexecuta get_or_create_profile: deve sanitizar para padrão multidisciplinar
    migrated = get_or_create_profile(test_db)
    assert migrated.strengths == DEFAULT_STRENGTHS
    assert migrated.difficulties == DEFAULT_DIFFICULTIES

def test_crud_gems_pedagogicas(test_db):
    gems = get_all_gems(test_db)
    assert len(gems) >= 4
    builtin_keys = [g.gem_id for g in gems if g.is_builtin == 1]
    assert "socratico" in builtin_keys
    assert "simulado" in builtin_keys

    # Criação de Gem customizada
    nova_gem = create_custom_gem(
        test_db,
        name="Redação ENEM ✍️",
        description="Foco nas 5 competências do ENEM",
        system_directive="[MODO ATIVO: REDAÇÃO ENEM] Avalie tema, tese e proposta de intervenção.",
    )
    assert nova_gem.is_builtin == 0
    assert "redacao" in nova_gem.gem_id

    # Atualização
    updated = update_custom_gem(
        test_db,
        gem_id=nova_gem.gem_id,
        name="Redação Nota 1000",
        description="Critérios oficiais",
        system_directive="Diretriz atualizada",
    )
    assert updated.name == "Redação Nota 1000"

    # Proteção de built-in: não pode deletar
    assert delete_custom_gem(test_db, "socratico") is False

    # Deleção da customizada
    assert delete_custom_gem(test_db, nova_gem.gem_id) is True

def test_injecao_dinamica_gem_system_prompt():
    custom_directive = "[MODO ATIVO: BIOLOGIA MOLECULAR] Explique DNA e RNA com precisão bioquímica."
    prompt = get_system_instruction(custom_directive=custom_directive)
    assert "[MODO ATIVO: BIOLOGIA MOLECULAR]" in prompt
    assert "Conrad" in prompt
```

---

### 3.3. Governança Documental (READMEs e CHANGELOG)
1. Atualizar `CHANGELOG.md` com a entrada `[3.4.0] — Gems Pedagógicas Customizáveis, Upload Integrado e Refinamento de UX/UI`.
2. Sincronizar `README(PT-BR).md` e `README.md` refletindo os novos recursos de Gems, novo layout de upload e perfil multidisciplinar para escolas.

---

## 4. Critérios de Aceite & Validação
* [ ] Os botões de download ficam inoperantes e sem resposta ao clique (`disabled=True` e `pointer-events: none`) durante qualquer geração do Conrad.
* [ ] A suite `tests/test_plano8.py` roda e passa com 100% de sucesso.
* [ ] A documentação bilíngue é devidamente atualizada refletindo a versão 3.4.0.
