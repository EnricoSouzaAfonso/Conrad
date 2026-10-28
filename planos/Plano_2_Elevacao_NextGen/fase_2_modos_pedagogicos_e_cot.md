# 📋 Especificação Técnica de Engenharia — Plano 2: Fase 2
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 2 — Elevação Next-Gen & Arquitetura Comercial de Alto Nível  
**Etapa:** Fase 2 — Modos Pedagógicos Especializados e Pensamento Socrático Visível (CoT)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Objetivo do Plano
Permitir que o estudante ou professor selecione dinamicamente a **abordagem didática** do Conrad de acordo com o seu objetivo de estudo, implementando 4 modos pedagógicos especializados:
1. **Modo Socrático Puro (Padrão):** Foco estrito em perguntas indutivas, andaimes cognitivos e descoberta guiada.
2. **Modo Simulado & Desafio:** O Conrad atua como examinador de bancas acadêmicas (ENEM, vestibulares, certificações), gerando problemas desafiadores e avaliando as respostas do aluno com rubricas formativas.
3. **Modo Arquiteto de Software:** Foco rigoroso em boas práticas de engenharia de software, complexidade algorítmica (Big-O), testes de casos de borda (*edge cases*) e refatoração.
4. **Modo Didático Intuitivo (Método Feynman):** Foco em analogias simples do cotidiano, eliminando jargões excessivos para quem está começando do zero.

Além disso, implementar a visualização expansível e acessível do **Raciocínio Pedagógico (Chain of Thought - CoT)** utilizando elementos nativos `<details>` e `<summary>`, revelando a estratégia de ensino adotada pelo assistente em cada turno.

---

## 2. Arquivos Afetados
* **Modificar:** `src/conrad_persona.py` (Adicionar diretrizes dos 4 modos pedagógicos e função geradora de prompt dinâmico baseada no modo ativo).
* **Modificar:** `src/conrad_core.py` (Adicionar suporte ao parâmetro `pedagogical_mode` e método `set_pedagogical_mode(mode: str)`).
* **Modificar:** `app.py` (Inserir seletor de Modo Pedagógico no menu lateral com ícones e descrições, e renderizar o CoT expansível acima de cada resposta).
* **Criar:** `tests/test_pedagogical_modes.py` (Bateria de testes unitários garantindo que cada modo altera o tom e o comportamento do prompt).
* **Modificar:** `CHANGELOG.md` (Registrar a versão 2.3.0 — Modos Pedagógicos e CoT Visível).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Diretrizes dos Modos Pedagógicos em `src/conrad_persona.py`
Adicionar a modelagem dos modos e a função geradora de instruções:

```python
"""
Definições dos Modos Pedagógicos do Conrad.
"""
PEDAGOGICAL_MODES = {
    "socratico": {
        "nome": "Socrático Puro (Padrão 🎓)",
        "descricao": "Perguntas indutivas, pistas graduais e construção autônoma de conceitos.",
        "diretriz": """
[MODO ATIVO: SOCRÁTICO PURO]
- NUNCA forneça a resposta final ou o código completo de imediato.
- Devolva perguntas indutivas que ativem o raciocínio prévio do aluno.
- Quando o aluno errar, investigue a premissa do erro em vez de apenas corrigi-lo.
"""
    },
    "simulado": {
        "nome": "Simulado & Desafio (Banca 📝)",
        "descricao": "Conrad gera questões estilo vestibular/concurso e avalia seu raciocínio.",
        "diretriz": """
[MODO ATIVO: SIMULADO & DESAFIO]
- Atue como examinador rigoroso, porém encorajador.
- Gere questões contextualizadas de múltipla escolha ou discursivas sobre o tema solicitado.
- Aguarde a resposta do estudante antes de revelar o gabarito.
- Forneça uma correção formativa detalhando os pontos fortes da resposta e onde houve falha de fundamentação.
"""
    },
    "engenharia": {
        "nome": "Arquiteto de Software (Dev 💻)",
        "descricao": "Engenharia de software, complexidade algorítmica, edge cases e clean code.",
        "diretriz": """
[MODO ATIVO: ARQUITETO DE SOFTWARE]
- Foque em boas práticas, arquitetura limpa e escalabilidade.
- Pergunte sobre complexidade de tempo e espaço (Big-O notation).
- Provoque ativamente a reflexão sobre casos extremos (nulos, arrays vazios, concorrência, exceções).
"""
    },
    "feynman": {
        "nome": "Intuitivo / Feynman (Iniciante 💡)",
        "descricao": "Explicações simples com analogias práticas do cotidiano, sem jargões difíceis.",
        "diretriz": """
[MODO ATIVO: MÉTODO FEYNMAN]
- Explique o conceito como se estivesse conversando com uma pessoa curiosa de 12 anos.
- Use analogias do dia a dia (carros, receitas, esportes, brinquedos).
- Elimine termos excessivamente técnicos; se usar um jargão, defina-o imediatamente em linguagem simples.
"""
    }
}

def get_system_instruction(mode: str = "socratico") -> str:
    """Retorna o prompt do sistema customizado com o modo pedagógico escolhido."""
    mode_info = PEDAGOGICAL_MODES.get(mode, PEDAGOGICAL_MODES["socratico"])
    return f"{SYSTEM_INSTRUCTION_CONRAD}\n\n{mode_info['diretriz']}".strip()
```

---

### 3.2. Atualização do `src/conrad_core.py`
Permitir a troca de modo sem reiniciar a conexão do cliente:

```python
    def set_pedagogical_mode(self, mode: str):
        """Atualiza o modo pedagógico e reinicia a sessão de chat com a nova instrução."""
        if mode in PEDAGOGICAL_MODES:
            self.system_instruction = get_system_instruction(mode)
            if self.client and self.api_key:
                self._init_chat()
```

---

### 3.3. Pensamento Pedagógico Visível (CoT) e Seletor no `app.py`
No `app.py`, o Argon deve:
1. Inserir o seletor no sidebar:
   ```python
   modo_selecionado = st.sidebar.selectbox(
       "🎯 Modo Pedagógico",
       options=list(PEDAGOGICAL_MODES.keys()),
       format_func=lambda k: PEDAGOGICAL_MODES[k]["nome"],
       help="Altere o estilo de tutoria do Conrad conforme seu objetivo de estudo."
   )
   if st.session_state.get("current_mode") != modo_selecionado:
       st.session_state.current_mode = modo_selecionado
       st.session_state.engine.set_pedagogical_mode(modo_selecionado)
       st.sidebar.caption(f"ℹ️ {PEDAGOGICAL_MODES[modo_selecionado]['descricao']}")
   ```
2. Renderizar o bloco expansível de CoT com acessibilidade nativa acima das respostas:
   ```python
   st.markdown("""
   <details style="background: #252525; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #C59B27;">
     <summary style="cursor: pointer; font-size: 12px; font-weight: 600; color: #ddd;">
       🧠 Raciocínio Pedagógico do Conrad
     </summary>
     <div style="font-size: 11px; color: #bbb; margin-top: 6px; line-height: 1.4;">
       Estratégia ativada: Diagnóstico socrático prévio. As pistas foram calibradas para provocar reflexão autônoma sem entregar a conclusão pronta.
     </div>
   </details>
   """, unsafe_allow_html=True)
   ```

---

## 4. Critério de Validação (Definition of Done)
1. **Alternância de Modos em Tempo Real:** A troca no selectbox altera a persona do Conrad imediatamente na próxima mensagem.
2. **Comportamento Socrático vs. Simulado:**
   - No modo *Socrático*, perguntar *"Como resolvo a integral de x * e^x?"* faz o Conrad perguntar qual método de integração o aluno lembra (integração por partes).
   - No modo *Simulado*, o Conrad gera uma questão contextualizada e solicita que o aluno tente resolver o primeiro passo.
3. **CoT Acessível:** O componente `<details>` abre e fecha suavemente sem causar deslocamento de layout (*layout shift* zero).
4. **Testes Unitários:** A suíte `tests/test_pedagogical_modes.py` valida com sucesso a geração de instruções para todos os 4 modos.
5. **Git Commit & Push:** Commitar com a mensagem:  
   `feat(modes): suporte a 4 modos pedagogicos e CoT socratico visivel`
