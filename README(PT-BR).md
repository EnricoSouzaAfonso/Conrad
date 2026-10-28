<p align="center">
  <img src="Conrad_Logo.jpg" alt="Logo do Conrad" width="700"/>
</p>

# Conrad - Assistente Pessoal de Aprendizado Socrático com IA

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Gemini-3.8%20Flash%20(1M%20Tokens)-purple.svg)](https://ai.google.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App%20Web-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend%20API-teal.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Container-blue.svg)](https://www.docker.com/)
[![Google Colab](https://img.shields.io/badge/Google%20Colab-notebook-orange.svg)](https://colab.research.google.com/github/EnricoSouzaAfonso/Conrad/blob/main/Conrad.ipynb)
[![License](https://img.shields.io/badge/License-CC--BY--NC--4.0-lightgrey.svg)](LICENSE)

**Conrad é um assistente pedagógico inteligente de alta performance, concebido para atuar como tutor socrático individualizado. Impulsionado pelo SDK moderno `google-genai` e pela família de modelos Google Gemini (com janela de contexto de até 1.048.576 tokens), o Conrad guia estudantes na construção ativa do conhecimento através de perguntas indutivas, lousa interativa e ciência da aprendizagem.**

---

## 📋 Índice
- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Arquitetura de Software](#arquitetura-de-software)
- [Como Executar o Conrad](#como-executar-o-conrad)
  - [Opção 1: Aplicação Web Local (Streamlit)](#opção-1-aplicação-web-local-streamlit)
  - [Opção 2: Container Docker](#opção-2-container-docker)
  - [Opção 3: Google Colab](#opção-3-google-colab)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Modos Pedagógicos](#modos-pedagógicos)
- [Histórico de Versões](#histórico-de-versões)
- [Contribuição](#contribuição)
- [Desenvolvido por](#desenvolvido-por)
- [Licença](#licença)

---

## 🎩 Sobre o Projeto

O **Conrad** nasceu da missão de transformar a inteligência artificial generativa em um verdadeiro parceiro cognitivo de estudos — e não em uma máquina de respostas prontas que atrofia o raciocínio do estudante. Representado por sua clássica cartola vitoriana (🎩), o Conrad combina rigor epistemológico, empatia e engenharia de interface de última geração.

Em sua arquitetura **v3.3**, o Conrad opera sobre quatro pilares científicos da educação:
1. **Taxonomia de Bloom Revisada:** Evolução estruturada do estudante desde a recordação e compreensão até a análise, avaliação e criação.
2. **Teoria da Carga Cognitiva (John Sweller):** Aplicação estrita da *Regra da Pergunta Única* (máximo de uma pergunta reflexiva por turno) e separação entre diálogo enxuto e demonstrações pesadas.
3. **Zona de Desenvolvimento Proximal e Scaffolding (Lev Vygotsky):** Andaimes graduais em 3 níveis (Pista Conceitual, Pista Estrutural e Exemplo Análogo Parcial) com retirada progressiva (*Fading*).
4. **Mentalidade de Crescimento (Carol Dweck):** Elogio focado no processo investigativo e tratamento de erros como oportunidades valiosas de neuroplasticidade.

---

## ✨ Funcionalidades Principais

- **🧠 Motor Cognitivo `google-genai` (1M Tokens):** Configurado por padrão com o `gemini-3.8-flash` e seletor integrado na interface para os modelos ativos (`gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.1-flash-lite` e `gemini-3.1-pro-preview`), incluindo *failover* transparente contra picos de demanda e *streaming* fluido a ~25fps (`40ms` throttle).
- **📐 Quadro Negro do Conrad (Collapsible Split-View Canvas):** Lousa lateral retrátil (`✖ Ocultar Lousa` / `📐 Abrir Lousa`) inspirada no *Claude Artifacts*. Recolhe-se para expandir o chat centralizado e abre-se automaticamente (*Auto-Reveal*) sempre que o Conrad projeta deduções algébricas em **LaTeX/MathJax v3**, diagramas em **Mermaid.js** (com validação e auto-reparo sintático) ou blocos de código.
- **💎 Gems Pedagógicas Customizáveis (CRUD Completo em SQLite):** Além das 4 Gems nativas protegidas (*Socrático Puro*, *Simulado & Desafio*, *Arquiteto de Software* e *Método Feynman*), estudantes e professores podem criar, editar e excluir suas próprias Gems especializadas para qualquer disciplina (ex: *Redação ENEM*, *Biologia*, *História*) diretamente na barra lateral.
- **💬 Floating Input Dock com Botão `➕` de Upload & Botão Flutuante Persistente da Lousa (`100dvh`):** Barra de perguntas flutuante no rodapé acompanhada do botão circular `➕` (`st.popover`) para anexar fotos de cadernos e PDFs com chip de pré-visualização, além do botão flutuante fixo no topo direito (`position: fixed`) que mantém o controle da lousa (`📐 Abrir Lousa` / `✖ Ocultar Lousa`) 100% acessível em qualquer nível de rolagem.
- **🔍 Cadeia de Pensamento Pedagógica (`<conrad_thought>`):** Acordeão expansível (*"🧠 Raciocínio Pedagógico do Conrad"*) que revela de forma transparente o diagnóstico do nível de Bloom e a estratégia socrática adotada em cada resposta.
- **📎 Visão Multimodal para Estudos:** Upload direto de fotos de cadernos, folhas de rascunho ou listas de exercícios em `.png`, `.jpg` e `.pdf` através do botão `➕` no Floating Dock para transcrição automática do enunciado no Quadro Negro e mediação passo a passo.
- **🧬 Memória Cognitiva Multidisciplinar Persistente (SQLite):** Registro contínuo e neutro dos pontos fortes, dificuldades em evolução e estilo de aprendizagem do estudante em banco de dados relacional local (`src/database.py`), com restauração rápida para o padrão multidisciplinar escolar.
- **📓 Caderno Digital Blindado & Micro-Termômetro de Retenção:** Compilação instantânea da sessão de estudos para download em **Markdown (`.md`)** e **PDF diagramado (`.pdf`)** (com proteção contra cliques concorrentes durante o streaming), acompanhada do Micro-Termômetro de Retenção Cognitiva com diagnóstico em *hover tooltip*.
- **🔑 Sistema BYOK (Bring Your Own Key) no Topo da Sidebar:** Entrada segura de chave da API Gemini posicionada ergonomicamente no topo da barra lateral, validação instantânea em milissegundos via `client.models.list()`, blindagem *Zero Crash* sem chave e tutorial integrado passo a passo.

---

## 🏗️ Arquitetura de Software

O projeto adota uma arquitetura modular desacoplada (*Clean Architecture*), permitindo que o mesmo núcleo cognitivo alimente a aplicação Web Streamlit, a API RESTful FastAPI e o notebook Google Colab:

```text
Conrad/
├── app.py                        # Aplicação Web Principal (Streamlit Split-View + Floating Dock)
├── Conrad.ipynb                  # Notebook Interativo para execução em nuvem no Google Colab
├── Dockerfile                    # Imagem de container para deploy reprodutível
├── docker-compose.yml            # Orquestração dos serviços Web (Streamlit) e API (FastAPI)
├── requirements.txt              # Dependências pinadas do ecossistema v3.x
├── src/
│   ├── conrad_core.py            # Motor GenAI (google-genai), Streaming, Multimodal e Validação BYOK
│   ├── conrad_persona.py         # Prompt Mestre v3.x, Persona Socrática e Blindagem MathJax
│   ├── conrad_pedagogy.py        # Governança Pedagógica (Bloom, Sweller, Vygotsky, Dweck e 4 Modos)
│   ├── conrad_canvas.py          # Parser de <conrad_artifact>, <conrad_thought> e reparo Mermaid
│   ├── conrad_analytics.py       # Termômetro heurístico de Retenção Cognitiva e Engajamento Ativo
│   ├── conrad_report.py          # Compilador do Caderno Digital para Markdown (.md) e PDF (fpdf2)
│   ├── database.py               # Persistência SQLAlchemy + SQLite (Perfil Cognitivo e Sessões)
│   ├── api.py                    # Backend RESTful FastAPI (/health, /chat, /sessions)
│   └── conrad_ui.py              # Interface interativa ipywidgets para Google Colab
└── tests/
    ├── qa_visual_inspection.py   # Suite de QA Ponta a Ponta + Inspeção Visual Headless + Governança
    ├── test_pedagogical_rigor.py # Auditoria automatizada de Bloom, Sweller, Dweck e Anti-Sycophancy
    ├── test_chaos_and_edge_cases.py # Bateria de Testes de Estresse, XSS, LaTeX e Resiliência HTTP
    ├── test_canvas_artifacts.py  # Testes unitários do parser do Quadro Negro e CoT
    ├── test_api_and_database.py  # Testes dos endpoints FastAPI, banco SQLite e validação BYOK
    └── test_persona_and_rules.py # Testes de integridade das regras invioláveis da persona
```

---

## 🚀 Como Executar o Conrad

### Opção 1: Aplicação Web Local (Streamlit)

1. **Clone o repositório e acesse a pasta do projeto:**
   ```bash
   git clone https://github.com/EnricoSouzaAfonso/Conrad.git
   cd Conrad
   ```

2. **Crie um ambiente virtual e instale as dependências:**
   ```bash
   python -m venv .venv
   # No Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # No Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Inicie a aplicação Web:**
   ```bash
   streamlit run app.py
   ```

4. **Configure sua API Key (BYOK):**
   - Abra `http://localhost:8501` no navegador.
   - Na barra lateral esquerda (**"🔑 Chave da API Gemini (BYOK)"**), insira sua chave gratuita obtida no [Google AI Studio](https://aistudio.google.com/app/apikey) e clique em **"Salvar e Validar Chave"** (ou defina `GOOGLE_API_KEY` em um arquivo `.env`).

---

### Opção 2: Container Docker

Para subir a aplicação Web (`porta 8501`) e o backend FastAPI (`porta 8000`) de forma isolada:

```bash
docker-compose up --build
```

- **Interface Web (Streamlit):** `http://localhost:8501`
- **Documentação Interativa da API (Swagger UI):** `http://localhost:8000/docs`

---

### Opção 3: Google Colab

Você também pode executar o Conrad diretamente na nuvem sem instalar nada localmente:

1. Clique no badge abaixo para abrir o notebook oficial no Google Colab:

   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnricoSouzaAfonso/Conrad/blob/main/Conrad.ipynb)

2. No menu lateral esquerdo do Colab, clique no ícone de **Chave (Secrets)** e adicione um segredo chamado `GOOGLE_API_KEY` com sua chave do [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Execute as células sequencialmente para instalar o pacote `google-genai` e carregar a interface interativa.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem Base:** [Python 3.11+](https://www.python.org/)
- **SDK de IA Generativa:** [Google GenAI SDK (`google-genai`)](https://ai.google.dev/) — Modelos `gemini-3.8-flash` (padrão, 1M tokens), `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.1-flash-lite` e `gemini-3.1-pro-preview`
- **Frontend Web:** [Streamlit](https://streamlit.io/) + CSS3 Moderno (`100dvh` Viewport, Floating Input Dock, Glassmorphism)
- **Renderização Científica & Diagramas:** [MathJax v3](https://www.mathjax.org/) (LaTeX/TeX) e [Mermaid.js v10](https://mermaid.js.org/)
- **Backend & Persistência:** [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/) e [SQLite](https://www.sqlite.org/)
- **Exportação Documental:** [FPDF2 (`fpdf2`)](https://py-pdf.github.io/fpdf2/) e [Markdown2](https://github.com/trentm/python-markdown2)
- **Containerização & Notebook:** [Docker](https://www.docker.com/) e [IPython Widgets (`ipywidgets`)](https://ipywidgets.readthedocs.io/en/stable/)

---

## 🎯 Modos Pedagógicos

Na barra lateral do Conrad, você pode alternar em tempo real entre **4 modos didáticos especializados**:

| Modo Pedagógico | Objetivo Didático | Comportamento do Conrad |
| :--- | :--- | :--- |
| **🎓 Socrático Puro (Padrão)** | Construção autônoma de conceitos do zero | Guia o estudante com perguntas indutivas, pistas graduais e jamais entrega o gabarito pronto. |
| **📝 Simulado & Desafio (Exame)** | Preparação rigorosa para provas e vestibulares | Propõe problemas desafiadores contextualizados, avalia justificativas passo a passo e exige rigor formal. |
| **💻 Arquiteto de Software (Code Review)** | Engenharia de software, algoritmos e depuração | Analisa complexidade Big-O ($O(n)$, $O(\log n)$), *clean code* e casos de borda sem reescrever o código inteiro pelo aluno. |
| **🔄 Método Feynman (Inversão)** | Consolidação profunda e detecção de pontos cegos | O Conrad assume o papel de um aprendiz curioso e pede que **você** explique o tema com suas palavras, questionando lacunas lógicas. |

---

## 📜 Histórico de Versões

Para consultar o registro detalhado de todas as versões, evoluções arquiteturais e correções do projeto seguindo o padrão *Keep a Changelog* e *SemVer*, acesse o arquivo [**CHANGELOG.md**](CHANGELOG.md).

---

## 🤝 Contribuição

Contribuições são muito bem-vindas! Para colaborar com a evolução do Conrad:

1. **Faça um Fork** do projeto.
2. **Crie uma Branch** para sua funcionalidade (`git checkout -b feat/MinhaInovacao`).
3. **Execute a suíte oficial de QA e Governança** (`python tests/qa_visual_inspection.py`).
4. **Faça o Commit** seguindo *Conventional Commits* (`git commit -m 'feat: adiciona MinhaInovacao'`).
5. **Envie o Push** (`git push origin feat/MinhaInovacao`) e abra um **Pull Request**.

---

## 👨‍💻 Desenvolvido por

Concebido e desenvolvido por **Enrico Souza Afonso** (iniciado em 17/05/2025 durante a Imersão Gemini da Alura e evoluído continuamente para a arquitetura Web & Cognitiva v3.3).

---

## 📄 Licença

Este projeto está licenciado sob a **Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0)**.

[![Licença CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc/4.0/)

Você pode consultar os termos completos desta licença no arquivo [LICENSE](LICENSE) ou em [creativecommons.org/licenses/by-nc/4.0](https://creativecommons.org/licenses/by-nc/4.0/).
