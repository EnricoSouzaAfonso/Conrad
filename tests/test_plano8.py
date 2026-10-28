"""
Suite de Testes Automatizados — Plano 8
Validação de Perfil Neutro, CRUD de Gems Pedagógicas, Injeção Dinâmica e Blindagem de Concorrência.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    import pytest
except ImportError:
    class _PytestStub:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestStub()
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


class TestPlano8Suite(unittest.TestCase):
    """Espelho unittest para execução automática em 'python -m unittest discover tests'."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = TestingSession()
        seed_default_gems(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_perfil_multidisciplinar_e_reset(self):
        test_perfil_cognitivo_multidisciplinar(self.db)
        self.db.query(type(get_or_create_profile(self.db))).first().strengths = "Tópico Customizado"
        self.db.commit()
        reset_prof = reset_profile_to_default(self.db)
        self.assertEqual(reset_prof.strengths, DEFAULT_STRENGTHS)

    def test_migracao_perfil_antigo_algebra(self):
        test_migracao_perfil_antigo(self.db)

    def test_crud_completo_gems_pedagogicas(self):
        test_crud_gems_pedagogicas(self.db)

    def test_injecao_system_prompt_gem_customizada(self):
        test_injecao_dinamica_gem_system_prompt()

    def test_blindagem_concorrencia_e_upload_dock_no_app(self):
        app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            app_src = f.read()
        self.assertIn("is_generating", app_src)
        self.assertIn("pointer-events: none !important;", app_src)
        self.assertIn("disabled=is_busy", app_src)
        self.assertIn("canvas_toggle_fixed_btn", app_src)
        self.assertIn('with st.popover("➕"', app_src)

    def test_modelos_ativos_e_sem_mascaramento(self):
        core_path = os.path.join(os.path.dirname(__file__), "..", "src", "conrad_core.py")
        with open(core_path, "r", encoding="utf-8") as f:
            core_src = f.read()
        # Não pode conter modelo extinto
        self.assertNotIn("gemini-2.5-flash-lite", core_src)
        # Não pode conter mapa de mascaramento/desvio de modelo
        self.assertNotIn("RUNTIME_MODEL_MAP", core_src)
        # Deve conter os modelos ativos suportados
        self.assertIn("gemini-3.8-flash", core_src)
        self.assertIn("gemini-3.5-flash", core_src)


if __name__ == "__main__":
    unittest.main()
