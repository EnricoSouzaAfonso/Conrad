# 📋 Especificação Técnica de Engenharia — Plano 8: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 8 — Gems Pedagógicas Customizáveis, Upload Integrado e Refinamento de UX/UI  
**Etapa:** Fase 1 — Neutralização Multidisciplinar do Perfil Cognitivo Inicial  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. O Viés Algébrico Hardcoded no Banco de Dados
* **Sintoma Relatado pelo Usuário:** Toda vez que um novo aluno abre o Conrad ou o banco SQLite é inicializado em uma escola, o perfil cognitivo já vem pré-preenchido com tópicos de álgebra (*"Introdução à álgebra"*, *"Identificação de variáveis em equações"*). O Conrad, portanto, já inicia a conversa assumindo viés matemático restrito, o que quebra a proposta do produto para escolas de ensino fundamental, médio e superior multidisciplinar (onde os alunos estudam História, Biologia, Redação, Filosofia, etc.).
* **Causa Raiz:** Em `src/database.py`, na função `get_or_create_profile`, os valores de fallback criados no primeiro acesso foram escritos estaticamente:
  ```python
  profile = StudentCognitiveProfile(
      student_id=student_id,
      strengths="Introdução à álgebra",
      difficulties="Identificação de variáveis em equações",
      learning_style="Analogias do cotidiano",
      pedagogical_notes="Aluno motivado; responde bem quando estimulado com exemplos do dia a dia.",
  )
  ```

---

## 2. Arquivos Afetados
* **Modificar:** `src/database.py` (Substituir defaults matemáticos por defaults neutros e multidisciplinares; adicionar rotina de sanitização automática para migrar bancos existentes que contenham o texto antigo).
* **Modificar:** `app.py` (Garantir que os placeholders dos inputs reflitam o caráter genérico e adicionar botão para "Resetar Perfil para Padrão Neutro").

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Atualização do `src/database.py`
1. Definir constantes para os valores padrão de um perfil neutro escolar:
   ```python
   DEFAULT_STRENGTHS = "Curioso e aberto a novos conhecimentos"
   DEFAULT_DIFFICULTIES = "Diagnóstico conceitual em andamento"
   DEFAULT_LEARNING_STYLE = "Adaptativo (Analogias e exemplos práticos)"
   DEFAULT_PEDAGOGICAL_NOTES = "Estudante iniciando jornada multidisciplinar. Adapte a linguagem ao ritmo e aos interesses do aluno."
   ```

2. Atualizar a função `get_or_create_profile`:
   ```python
   def get_or_create_profile(db, student_id: Optional[int] = None) -> StudentCognitiveProfile:
       """Busca ou inicializa o perfil cognitivo neutro e multidisciplinar do estudante."""
       query = db.query(StudentCognitiveProfile)
       if student_id is not None:
           profile = query.filter(StudentCognitiveProfile.student_id == student_id).first()
       else:
           profile = query.first()

       if not profile:
           profile = StudentCognitiveProfile(
               student_id=student_id,
               strengths=DEFAULT_STRENGTHS,
               difficulties=DEFAULT_DIFFICULTIES,
               learning_style=DEFAULT_LEARNING_STYLE,
               pedagogical_notes=DEFAULT_PEDAGOGICAL_NOTES,
           )
           db.add(profile)
           db.commit()
           db.refresh(profile)
       else:
           # Migração transparente: se o banco local ainda possuir o mock antigo de álgebra, atualiza suavemente
           if "Introdução à álgebra" in (profile.strengths or ""):
               profile.strengths = DEFAULT_STRENGTHS
               if "Identificação de variáveis" in (profile.difficulties or ""):
                   profile.difficulties = DEFAULT_DIFFICULTIES
               if "Aluno motivado" in (profile.pedagogical_notes or ""):
                   profile.pedagogical_notes = DEFAULT_PEDAGOGICAL_NOTES
               db.commit()
               db.refresh(profile)
       return profile
   ```

3. Adicionar função de reset em `src/database.py`:
   ```python
   def reset_profile_to_default(db, student_id: Optional[int] = None) -> StudentCognitiveProfile:
       """Restaura o perfil cognitivo para os padrões neutros e multidisciplinares."""
       profile = get_or_create_profile(db, student_id=student_id)
       profile.strengths = DEFAULT_STRENGTHS
       profile.difficulties = DEFAULT_DIFFICULTIES
       profile.learning_style = DEFAULT_LEARNING_STYLE
       profile.pedagogical_notes = DEFAULT_PEDAGOGICAL_NOTES
       db.commit()
       db.refresh(profile)
       return profile
   ```

---

### 3.2. Atualização da Interface no `app.py`
No bloco expander do Perfil Cognitivo:
1. Exibir os novos valores padrão neutros.
2. Adicionar botão secundário de redefinição rápida:
   ```python
   col_save_prof, col_reset_prof = st.columns([0.65, 0.35])
   with col_save_prof:
       if st.button("💾 Atualizar Perfil", use_container_width=True):
           _save_cognitive_profile(new_strengths, new_difficulties, new_style, cognitive_profile["pedagogical_notes"])
           st.success("Perfil atualizado!")
           st.rerun()
   with col_reset_prof:
       if st.button("🔄 Resetar", use_container_width=True, help="Restaurar perfil inicial neutro"):
           db = SessionLocal()
           try:
               reset_profile_to_default(db)
           finally:
               db.close()
           st.info("Perfil restaurado para padrão multidisciplinar!")
           st.rerun()
   ```

---

## 4. Critérios de Aceite & Validação
* [ ] Ao inicializar uma base SQLite zerada, o perfil cognitivo NÃO contém nenhuma menção a "álgebra" ou "variáveis".
* [ ] Em bancos existentes com "Introdução à álgebra", a rotina de auto-migração substitui transparentemente pelos defaults neutros.
* [ ] Ao clicar em "Resetar", os campos voltam imediatamente para o padrão multidisciplinar.
