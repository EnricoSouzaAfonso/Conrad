# 📋 Especificação Técnica de Auditoria — Plano 9: Fase 3
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 9 — Dossiê de Auditoria Forense e Revisão Técnica para o Argon  
**Etapa:** Fase 3 — Revisão de Banco de Dados, Testes Unitários e Governança Documental  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Emissor:** Arquiteto Líder  

---

## 1. Contexto & Diagnóstico

### 1.1. Depreciações no Banco de Dados (`src/database.py`)
No Python 3.12+, `datetime.utcnow()` foi formalmente marcado como depreciado pelo Python Software Foundation, gerando avisos de `DeprecationWarning` a cada operação de criação de sessão, mensagem ou perfil cognitivo.

### 1.2. Fragilidade em Asserções de Teste (`tests/test_plano8.py`)
A asserção anterior do Plano 8 apenas procurava pela string `"chat-sticky-header"` dentro do arquivo `app.py`. Isso permitiu que uma tag HTML vazia e inoperante passasse no teste sem validar se o botão estava de fato acessível na interface. Além disso, não havia teste impedindo a regressão do seqüestro de modelos (`RUNTIME_MODEL_MAP`) ou o uso de modelos extintos.

---

## 2. Modificações Exatas Realizadas

Argon, revise as seguintes modificações aplicadas:

### 2.1. Higienização de `datetime` no `src/database.py`
* Importado `from datetime import datetime, timezone`.
* Criada função utilitária `_utcnow`:
```python
def _utcnow():
    return datetime.now(timezone.utc)
```
* Substituídas todas as ocorrências de `default=datetime.utcnow` por `default=_utcnow`.
* Substituídas todas as atribuições `profile.updated_at = datetime.utcnow()` por `profile.updated_at = _utcnow()`.

### 2.2. Fortalecimento da Suíte de Testes (`tests/test_plano8.py`)
1. Atualizado o teste do botão fixo no app:
```python
def test_blindagem_concorrencia_e_upload_dock_no_app(self):
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        app_src = f.read()
    self.assertIn("is_generating", app_src)
    self.assertIn("pointer-events: none !important;", app_src)
    self.assertIn("disabled=is_busy", app_src)
    self.assertIn("canvas_toggle_fixed_btn", app_src)
    self.assertIn('with st.popover("➕"', app_src)
```

2. Adicionado teste explícito contra regressão de mascaramento de modelos:
```python
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
```

### 2.3. Governança e Documentação Bilíngue
* **`src/conrad_persona.py`:** Atualizado `CONRAD_VERSION = "3.4.1"`.
* **`CHANGELOG.md`:** Registrada a versão `[3.4.1] - 28/10/2026` com todas as correções forenses.
* **`README(PT-BR).md` & `README(ENG).md`:** Atualizados os blocos de Tecnologias e Funcionalidades para remover qualquer menção ao extinto `gemini-2.5-flash-lite` e refletir o catálogo oficial de 2026.

---

## 3. Checklist de Revisão e Execução para o Argon
- [ ] Executar a suíte completa de testes:
  ```powershell
  python -m unittest discover -s tests -v
  ```
  *(Verificar que os 63 testes rodam com 100% de sucesso).*
- [ ] Executar o protocolo visual de QA:
  ```powershell
  python tests/qa_visual_inspection.py
  ```
  *(Verificar que todos os 5 passos passam e novas evidências são salvas em `tests/screenshots/`).*
- [ ] Confirmar que os arquivos estão perfeitamente sincronizados entre a raiz, `repo/` e `Conrad/`.
