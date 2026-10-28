# 📋 Especificação Técnica de Engenharia — Plano 8: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 8 — Gems Pedagógicas Customizáveis, Upload Integrado e Refinamento de UX/UI  
**Etapa:** Fase 2 — Arquitetura e CRUD de Gems Pedagógicas Customizáveis (Estilo Gemini Gems)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico e Conceituação

### 1.1. Como Funciona o "Modo Pedagógico" Atual
No Conrad, o Modo Pedagógico funciona como uma lente diretiva injetada dinamicamente no **System Prompt** do Google Gemini. Cada modo contém um conjunto de regras heurísticas que orientam o modelo:
* **Socrático Puro:** Exige que a IA jamais entregue a resposta final e force o aluno a refletir através de perguntas únicas indutivas.
* **Simulado & Desafio:** Faz a IA agir como banca examinadora (concursos/vestibulares), gerando questões e avaliando a fundamentação.
* **Arquiteto de Software:** Foca em complexidade de tempo/espaço (Big-O), casos extremos de borda e boas práticas.
* **Intuitivo / Feynman:** Converte qualquer conceito denso em analogias ultrassimplificadas do cotidiano.

### 1.2. A Necessidade de Customização Escolar (Gems Pedagógicas)
Atualmente, esses 4 modos estão em uma lista estática de código (`PEDAGOGICAL_MODES`). No entanto, para comercialização em instituições de ensino:
* Um professor de literatura quer criar a Gem *"Treinador de Redação Nota 1000 ENEM"*;
* Um coordenador de curso técnico quer criar a Gem *"Inspetor de Bancos de Dados SQL"*;
* Um aluno quer criar a Gem *"Conversação em Inglês Jurídico"*.

Portanto, os Modos Pedagógicos devem ser evoluídos para **Gems Pedagógicas Dinâmicas com CRUD Completo** (Criar, Ler, Atualizar e Deletar) persistidas no banco SQLite.

---

## 2. Arquivos Afetados
* **Modificar:** `src/database.py` (Criar modelo `PedagogicalGemDB`, rotina de auto-seed das 4 Gems padrão e funções CRUD).
* **Modificar:** `src/conrad_persona.py` e `src/conrad_core.py` (Suporte à resolução dinâmica de diretrizes por `gem_id` ou injeção customizada).
* **Modificar:** `app.py` (Seletor reativo de Gems + painel expansível/modal para gerenciar, criar, editar e excluir Gems).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Modelo e Operações de Banco em `src/database.py`
1. Declarar a classe `PedagogicalGemDB`:
```python
class PedagogicalGemDB(Base):
    __tablename__ = "pedagogical_gems"
    id = Column(Integer, primary_key=True, index=True)
    gem_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    system_directive = Column(Text, nullable=False)
    is_builtin = Column(Integer, default=0)  # 1 para as 4 oficiais (protegidas), 0 para customizadas
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. Implementar a rotina de Seed das 4 Gems Oficiais (garante retrocompatibilidade total na inicialização):
```python
def seed_default_gems(db):
    """Garante a existência das 4 Gems nativas do Conrad."""
    from src.conrad_pedagogy import PEDAGOGICAL_MODES
    for key, data in PEDAGOGICAL_MODES.items():
        existing = db.query(PedagogicalGemDB).filter(PedagogicalGemDB.gem_id == key).first()
        if not existing:
            gem = PedagogicalGemDB(
                gem_id=key,
                name=data["nome"],
                description=data["descricao"],
                system_directive=data["diretriz"],
                is_builtin=1,
            )
            db.add(gem)
    db.commit()
```

3. Implementar as funções CRUD:
```python
def get_all_gems(db) -> list:
    """Retorna todas as Gems ordenando oficiais primeiro, depois por nome."""
    return db.query(PedagogicalGemDB).order_by(PedagogicalGemDB.is_builtin.desc(), PedagogicalGemDB.name.asc()).all()

def get_gem_by_id(db, gem_id: str) -> Optional[PedagogicalGemDB]:
    return db.query(PedagogicalGemDB).filter(PedagogicalGemDB.gem_id == gem_id).first()

def create_custom_gem(db, name: str, description: str, system_directive: str) -> PedagogicalGemDB:
    import re
    # Gera um slug seguro
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", name.lower()).strip("_")[:40]
    gem_id = f"custom_{slug}_{int(datetime.utcnow().timestamp())}"
    gem = PedagogicalGemDB(
        gem_id=gem_id,
        name=name.strip(),
        description=description.strip(),
        system_directive=system_directive.strip(),
        is_builtin=0,
    )
    db.add(gem)
    db.commit()
    db.refresh(gem)
    return gem

def update_custom_gem(db, gem_id: str, name: str, description: str, system_directive: str) -> Optional[PedagogicalGemDB]:
    gem = get_gem_by_id(db, gem_id)
    if not gem or gem.is_builtin == 1:
        return None  # Não permite alterar built-ins
    gem.name = name.strip()
    gem.description = description.strip()
    gem.system_directive = system_directive.strip()
    db.commit()
    db.refresh(gem)
    return gem

def delete_custom_gem(db, gem_id: str) -> bool:
    gem = get_gem_by_id(db, gem_id)
    if not gem or gem.is_builtin == 1:
        return False  # Built-ins são blindadas contra exclusão
    db.delete(gem)
    db.commit()
    return True
```

---

### 3.2. Integração no `src/conrad_persona.py` e `src/conrad_core.py`
Atualizar `get_system_instruction` para aceitar a diretriz da Gem ativa vinda do banco:
```python
def get_system_instruction(mode: str = "socratico", custom_directive: Optional[str] = None) -> str:
    """Monta o system prompt mestre aplicando a diretriz da Gem ativa."""
    if custom_directive:
        directive_text = custom_directive.strip()
    else:
        from src.conrad_pedagogy import PEDAGOGICAL_MODES
        mode_info = PEDAGOGICAL_MODES.get(mode, PEDAGOGICAL_MODES.get("socratico", {}))
        directive_text = mode_info.get("diretriz", "").strip()

    return f"{SYSTEM_INSTRUCTION_CONRAD.strip()}\n\n{directive_text}".strip()
```

Em `ConradEngine`:
```python
def set_gem(self, gem_id: str, directive: str):
    """Atualiza a Gem ativa e regenera a sessão do chat com o novo System Instruction."""
    self.pedagogical_mode = gem_id
    self.custom_gem_directive = directive
    if self.client and self.api_key:
        self._init_chat()
```

---

### 3.3. Interface de Gestão de Gems no `app.py`
Na sidebar, no bloco de **Modo Pedagógico / Gems**:
1. O `st.selectbox` carrega dinamicamente a lista de Gems do banco:
   ```python
   db = SessionLocal()
   all_gems = get_all_gems(db)
   db.close()
   gem_options = {g.gem_id: g for g in all_gems}
   ```
2. Adicionar expansor **"💎 Gerenciar Gems Pedagógicas (Criar / Editar)"**:
   * Aba 1: **Criar Nova Gem**:
     - Input Nome (ex: "Redação ENEM ✍️")
     - Input Descrição (ex: "Guia estruturado com os 5 critérios")
     - Text Area com as Diretrizes da IA (instruções de como o Conrad deve se comportar)
     - Botão `✨ Criar Gem Pedagógica`
   * Aba 2: **Minhas Gems Customizadas**:
     - Lista das Gems criadas com badges, botão para editar e botão de lixeira `🗑️` com confirmação.

---

## 4. Critérios de Aceite & Validação
* [ ] As 4 Gems oficiais vêm ativas e protegidas contra exclusão acidental.
* [ ] O usuário consegue criar uma Gem nova (ex: *"Prof. de Filosofia"*), salvá-la e vê-la imediatamente no selectbox.
* [ ] Ao selecionar a nova Gem, o Conrad incorpora rigorosamente a nova instrução durante o chat.
* [ ] Gems customizadas podem ser editadas ou excluídas sem quebrar o banco de dados.
