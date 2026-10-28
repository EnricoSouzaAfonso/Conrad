# 📋 Especificação Técnica de Engenharia — Plano 2: Fase 3
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 2 — Elevação Next-Gen & Arquitetura Comercial de Alto Nível  
**Etapa:** Fase 3 — Memória Pedagógica Persistente e Upload Multimodal de Exercícios (Fotos & PDFs)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Dotar o Conrad de duas das capacidades mais solicitadas por estudantes e instituições de ensino:
1. **Memória Pedagógica Persistente (Perfil Cognitivo):** Armazenar de forma estruturada no banco de dados (`src/database.py`) o mapa de habilidades do aluno — seus pontos fortes, temas de maior dificuldade e estilo preferido de explicação —, permitindo que o Conrad retome o aprendizado exatamente de onde parou em sessões passadas.
2. **Tutoria Multimodal Nativa (Fotos de Caderno & PDFs de Listas):** Aproveitar a arquitetura multimodal do **Gemini 3.8 Flash** para permitir o upload direto de imagens (fotos de listas de exercícios, gráficos ou anotações à mão) e arquivos PDF de apostilas. O Conrad transcreve o enunciado para o Quadro Negro (Canvas) e guia o estudante passo a passo na resolução do problema prático fotografado.

---

## 2. Arquivos Afetados
* **Modificar:** `src/database.py` (Adicionar a tabela `StudentCognitiveProfile` para armazenar facilidades, dificuldades e notas de tutoria por estudante).
* **Modificar:** `src/conrad_core.py` (Implementar `send_message_multimodal()` com suporte a `types.Part.from_bytes()` e injeção do perfil de memória no contexto do chat).
* **Modificar:** `app.py` (Adicionar `st.file_uploader` para imagens PNG/JPG e documentos PDF, com preview instantâneo na coluna do chat e extração no Canvas).
* **Criar:** `tests/test_multimodal_and_memory.py` (Testes unitários de persistência e serialização de arquivos binários para a API).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 2.4.0 — Perfil Cognitivo e Suporte Multimodal).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Expansão da Camada de Banco de Dados (`src/database.py`)
Adicionar o modelo de perfil cognitivo:

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class StudentCognitiveProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=True)
    strengths = Column(Text, default="")         # Ex: "Geometria plana, Lógica Booleana"
    difficulties = Column(Text, default="")      # Ex: "Regra da Cadeia em Derivadas, Recursão"
    learning_style = Column(String(50), default="Visual e Prático")  # Visual, Intuitivo, Formal
    pedagogical_notes = Column(Text, default="") # Observações cumulativas do tutor
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_or_create_profile(db, student_id: Optional[int] = None) -> StudentCognitiveProfile:
    """Busca ou inicializa o perfil cognitivo do estudante."""
    profile = db.query(StudentCognitiveProfile).first()
    if not profile:
        profile = StudentCognitiveProfile(
            strengths="Introdução à álgebra",
            difficulties="Identificação de variáveis em equações",
            learning_style="Analogias do cotidiano",
            pedagogical_notes="Aluno motivado; responde bem quando estimulado com exemplos do dia a dia."
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
```

---

### 3.2. Suporte Multimodal no `src/conrad_core.py`
Implementar o envio de mídias usando os tipos nativos do SDK `google-genai`:

```python
from google.genai import types

class ConradEngine:
    ...
    def send_message_multimodal(
        self,
        prompt: str,
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None
    ) -> str:
        """Envia prompt acompanhado de mídia binária (imagem ou PDF)."""
        if not self.chat:
            raise RuntimeError("Sessão de chat não inicializada.")

        contents = []
        if media_bytes and mime_type:
            part = types.Part.from_bytes(data=media_bytes, mime_type=mime_type)
            contents.append(part)

        contents.append(prompt or "Por favor, analise este material e me guie no entendimento do exercício.")

        try:
            response = self.chat.send_message(contents)
            return response.text if response.text else "(Sem resposta textual da API)"
        except Exception as e:
            raise RuntimeError(f"Erro ao processar conteúdo multimodal: {str(e)}")

    def build_context_with_memory(self, memory_notes: str) -> str:
        """Gera injeção de contexto com o histórico pedagógico do aluno."""
        return f"[HISTÓRICO PEDAGÓGICO DO ESTUDANTE]: {memory_notes}\n"
```

---

### 3.3. Interface de Upload e Visualização no `app.py`
No `app.py`, o Argon deve:
1. Inserir o widget de upload no rodapé da coluna do chat:
   ```python
   uploaded_file = st.file_uploader(
       "📎 Anexar foto do caderno, lista ou PDF de estudos:",
       type=["png", "jpg", "jpeg", "pdf"],
       key="study_media_uploader"
   )
   ```
2. Ao enviar uma mensagem com arquivo anexado:
   - Exibir miniatura da imagem no histórico de chat (`st.image(uploaded_file, width=220)`).
   - Chamar `engine.send_message_multimodal(...)`.
   - Instruir o Conrad a transcrever o problema fotografado para o Quadro Negro (Canvas) e começar com uma pergunta indutiva sobre a primeira linha do enunciado.
3. Exibir no menu lateral uma caixa retrátil:
   `"🧠 Seu Perfil de Aprendizado (O que o Conrad já aprendeu sobre você)"` mostrando seus pontos fortes e temas em evolução.

---

## 4. Critério de Validação (Definition of Done)
1. **Upload e Leitura de Foto de Caderno:**
   - Enviar uma foto contendo uma equação escrita à mão (ex: `2x + 5 = 15`).
   - O Conrad deve transcrever a equação com sucesso para o Canvas e perguntar: *"Para isolarmos a incógnita x, o que você acha que devemos fazer com o número 5 primeiro?"*.
2. **Upload de Documento PDF:**
   - Enviar um PDF de 1 página contendo um enunciado de física.
   - O Conrad deve ler o texto do PDF, extrair os dados informados e perguntar quais grandezas o aluno identifica no problema.
3. **Persistência de Perfil Cognitivo:**
   - As anotações do perfil são salvas no banco SQLite `conrad_data.db`.
   - Ao reiniciar o app, o Conrad cumprimenta o estudante reconhecendo o assunto trabalhado anteriormente.
4. **Testes Unitários:** A suíte `tests/test_multimodal_and_memory.py` roda e passa sem erros de tipo na API do Gemini.
5. **Git Commit & Push:** Commitar com a mensagem padronizada:  
   `feat(multimodal): suporte a fotos/PDFs de exercicios e perfil cognitivo do aluno`
