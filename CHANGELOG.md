# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.3.0] - 23/10/2026

### Adicionado
- **Modos Pedagógicos Especializados (`src/conrad_persona.py`, `src/conrad_core.py`, `app.py`):** Implementação do dicionário `PEDAGOGICAL_MODES` e método `set_pedagogical_mode()` com 4 abordagens didáticas selecionáveis em tempo real: *Socrático Puro*, *Simulado & Desafio (Banca)*, *Arquiteto de Software (Dev)* e *Intuitivo / Feynman (Iniciante)*.
- **Pensamento Pedagógico Visível Nativo (`app.py`):** Renderização acessível de Chain of Thought (CoT) com elementos `<details>` e `<summary>` sem deslocamento de layout (*layout shift* zero).
- **Suíte de Testes de Modos Pedagógicos (`tests/test_pedagogical_modes.py`):** Validação automatizada das diretrizes de todos os 4 modos e alternância dinâmica na sessão do `ConradEngine`.

## [2.2.0] - 23/10/2026

### Adicionado
- **Lançamento do Conrad Canvas e Interface Split-View (`app.py`, `src/conrad_canvas.py`):** Divisão da interface principal em duas colunas dinâmicas (`col_chat` à esquerda para o diálogo socrático limpo e `col_canvas` à direita para o "📐 Quadro Negro do Conrad").
- **Protocolo de Artifacts (`src/conrad_persona.py`, `src/conrad_canvas.py`):** Diretriz de sistema e parser (`CanvasParser` e `ConradArtifact`) para interceptar e projetar tags `<conrad_artifact type="math|code|mermaid|summary" title="...">` diretamente no Quadro Negro com suporte a MathJax, Syntax Highlighting e diagramas Mermaid nativos.
- **Pensamento Pedagógico Visível / CoT (`app.py`, `src/conrad_canvas.py`):** Componente expansível discreto (`🧠 Raciocínio Pedagógico do Conrad (Estratégia Socrática)`) no topo das respostas do assistente para dar transparência à mediação socrática.
- **Suíte de Testes do Canvas (`tests/test_canvas_artifacts.py`):** Validação automatizada da extração de artifacts matemáticos (Equação de Bernoulli), diagramas Mermaid, blocos de código, resumos e resiliência em mensagens puramente conversacionais.

## [2.1.0] - 23/10/2026

### Adicionado
- **Upgrade para Gemini 3.8 Flash & Seletor de Modelos Definitivos (`src/conrad_core.py`, `app.py`):** Adoção do modelo `gemini-3.8-flash` como padrão (`DEFAULT_MODEL_NAME`) e seletor dinâmico com a lista curada `DEFINITIVE_MODELS`.
- **Onboarding BYOK (Bring Your Own Key) & Validação em Tempo Real (`app.py`, `src/conrad_core.py`):** Inicialização resiliente sem chave (Zero Crash), campo de senha na sidebar com botão "Salvar e Validar Chave" (`validate_api_key()`) e tutorial expansível passo a passo do Google AI Studio.
- **Mensagem Pré-Programada da Cartola (`src/conrad_persona.py`):** Constante `MSG_CONRAD_SEM_API_KEY` (`get_missing_key_message()`) exibida graciosamente no chat quando nenhuma chave está configurada.
- **Diagramas Conceituais Mermaid & Utilitários de Estudo:** Diretriz de geração de mapas mentais em `mermaid`, contador de tokens na sidebar, botão "Nova Conversa" e exportação de resumo de estudos em Markdown (`.md`).

## [2.0.0] - 23/10/2026

### Adicionado
- **Camada de Persistência Relacional (`src/database.py`):** Modelagem ORM com SQLAlchemy (`StudentUser`, `ChatSessionDB`, `ChatMessageDB`) e banco SQLite/PostgreSQL (`conrad_data.db`).
- **Suporte a Streaming em Tempo Real (`src/conrad_core.py`):** Método `send_message_stream()` no `ConradEngine` para geração progressiva de respostas.
- **API Backend Comercial (`src/api.py`):** Serviço FastAPI com suporte a CORS, documentação automática OpenAPI (`/docs`), criação de sessões (`POST /api/sessions`) e streaming via Server-Sent Events (`POST /api/chat/stream`).
- **Aplicação Web Autônoma (`app.py`):** Frontend independente em Streamlit com Dark Mode, MathJax v3 e streaming interativo.
- **Infraestrutura de Containerização (`Dockerfile` e `docker-compose.yml`):** Empacotamento completo para deploy em nuvem.

## [1.6.2-dev] - 23/10/2026

### Adicionado
- **Ativo Vetorial da Cartola (`src/assets/conrad_avatar.py`):** Isolamento da constante `CONRAD_AVATAR_SVG` com o ícone vetorial otimizado do Conrad (🎩).
- **Módulo de Interface Interativa (`src/conrad_ui.py`):** Implementação da classe `ConradChatUI` com injeção dinâmica de MathJax v3 (`tex-svg.js`), mapeamento dinâmico de extensões/MIME via Pygments, botões interativos de Copiar e Baixar blocos de código, suporte a `Enter`/`Shift+Enter` e encerramento estrito por `"fim"`.

### Alterado
- **Simplificação Drástica da Célula 4 (`Conrad.ipynb`):** Redução da Célula 4 para inicialização enxuta (`ui = ConradChatUI(engine=engine); ui.render()`).

## [1.6.1-dev] - 22/10/2026

### Adicionado
- **Módulo de Persona (`src/conrad_persona.py`):** Extração e consolidação das System Instructions (`SYSTEM_INSTRUCTION_CONRAD`), metadados de identidade e diretrizes pedagógicas socráticas e construtivistas.
- **Blindagem Rigorosa de Renderização LaTeX / MathJax:** Regras estritas contra o bug de palavras coladas em modo inline (`$...$`), determinando equações em bloco (`$$...$$`), variáveis isoladas inline, uso de `\text{...}` e discriminação obrigatória de variáveis.
- **Protocolo Não-Hostil de Precisão Factual (3 Passos):** Validação da intenção, correção suave baseada em consenso científico e contextualização histórica.
- **Testes Automatizados (`tests/test_persona_and_rules.py`):** Suíte de validação das regras invioláveis, blindagem MathJax, protocolo de 3 passos e encerramento estrito.

### Alterado
- **Desacoplamento da Célula 4 (`Conrad.ipynb`) e `ConradEngine` (`src/conrad_core.py`):** Substituição do bloco monolítico de 540 linhas de System Instructions pela importação direta de `src.conrad_persona`.

## [1.6.0-dev] - 22/10/2026

### Adicionado
- **Módulo Core Desacoplado (`src/conrad_core.py`):** Criação da classe `ConradEngine` para encapsular o cliente da API Gemini, gerenciamento de sessão de chat, contagem de tokens e tratamento de bloqueios de segurança (`safety_settings`).
- **Autenticação Híbrida:** Suporte flexível tanto para Google Colab Secrets (`userdata`) quanto para variáveis de ambiente locais (`GEMINI_API_KEY` / `GOOGLE_API_KEY`).
- **Padronização de Dependências (`requirements.txt`):** Adição do arquivo de dependências para permitir execução e testes em ambiente local ou servidor.

### Alterado
- **Migração para o Novo SDK Oficial (`google-genai` v1.x):** Substituição integral do pacote legado `google-generativeai` pelo novo SDK `google-genai`, utilizando `genai.Client`, `client.chats.create` e `types.GenerateContentConfig` com o modelo `gemini-2.5-flash`.
- **Refatoração do Notebook (`Conrad.ipynb`):** Atualização das células de instalação, configuração, listagem de modelos e integração com o `ConradEngine`.

## [1.5.1] - 10/09/2025

### Corrigido
- Corrigido um bug crítico causado pela descontinuação do modelo de linguagem `gemini-2.5-flash-preview-04-17-thinking`. O modelo padrão do Conrad foi atualizado para a versão estável `models/gemini-2.5-flash` para garantir a continuidade do serviço.

## [1.5.0] - 28/06/2025

### Adicionado
- **Interface de Chat Reconstruída com `ipywidgets`:** A UI foi completamente refeita para ser mais robusta, interativa e nativa do ambiente Jupyter/Colab, com melhor controle de layout e componentes como área de texto auto-redimensionável.
- **Blocos de Código Interativos:** As respostas com código agora possuem:
    - **Syntax Highlighting** aprimorado e indicação visual da linguagem.
    - Botões para **Copiar** e **Baixar** o código diretamente.
- **Contador de Tokens de Contexto:** Um contador visível na UI que ajuda o usuário (e o Conrad) a gerenciar o tamanho da conversa e evitar a perda de contexto.
- **Novas Estratégias Pedagógicas (IA):** Conrad agora pode usar "Verificação por Parafraseamento" e sugerir pequenos "Desafios" para um aprendizado mais ativo.

### Alterado
- **Refinamento da Filosofia de Ensino (IA):** O objetivo principal foi aprofundado para focar em uma abordagem "construtivista e socrática", guiando o usuário na construção do conhecimento em vez de apenas entregar respostas.
- **Personalização e Empatia Aprimoradas (IA):** Conrad agora se lembra das preferências de estilo de explicação do usuário (ex: analogias) dentro de uma mesma sessão e é mais proativo ao oferecer ajuda quando detecta frustração.
- **Refatoração Completa da Lógica da Interface:** O código foi reestruturado para suportar `ipywidgets`, com uma renderização de HTML/CSS mais sofisticada, incluindo um avatar SVG para o Conrad e barras de rolagem customizadas.

## [1.4.0] - 30/05/2025

### Adicionado
- **Nova Interface de Usuário (Colab HTML):** Experiência de chat aprimorada com textarea, botão de envio e interatividade via callbacks, substituindo o input de console.
- **Gerenciamento Seguro de API Key:** Utilização de Colab Secrets para configuração da chave da API Gemini, com tratamento de erro robusto.
- **Utilitário de Seleção de Modelo:** Nova célula para listar e facilitar a escolha de diferentes modelos Gemini para o Conrad.
- **Avanços na IA (System Instruction):**
    - Melhoria na clareza das respostas (uso de Markdown).
    - Maior foco no usuário como condutor do aprendizado.
    - Instruções detalhadas para lidar com "code-switching" (múltiplos idiomas no prompt).
    - Capacidade de sugerir pausas e injetar curiosidades pertinentes.

### Alterado
- **Modernização da API e Lógica de Chat:**
    - Migração para a API `genai.GenerativeModel` (mais recente) para sessões de chat.
    - Lógica de interação e encerramento completamente refeita para suportar a nova interface HTML e a API atualizada.
- **Refinamentos no `System Instruction`:** Ajustes nas diretrizes multilíngues e de encerramento.

## [1.3.0] - 29/05/2025

### Adicionado
- **Suporte Multilíngue Dinâmico:** Conrad agora adapta saudações e respostas ao idioma do usuário, permitindo também a solicitação explícita de mudança de idioma.
- **Interface com Instruções Bilíngues:** Mensagens fixas do console (encerrar, resumo) exibidas em PT-BR e Inglês.

### Alterado
- **Lógica de Interação:** Saudação inicial, comando de encerramento e exibição de mensagens adaptadas para o novo suporte multilíngue.

## [1.2.0] - 24/05/2025

### Adicionado
- **Habilidades de Comunicação Avançadas:** Incluindo linguagem inclusiva, reconhecimento de frustração, melhor gestão de tópicos, tratamento de perguntas complexas e incentivo à autonomia do usuário.
- **Modo "Curiosidade Rápida":** Capacidade de compartilhar fatos interessantes.

### Alterado
- **Estrutura Interna e Feedback:** Melhor organização das instruções do `system_instruction` e refinamento no processo de lidar com feedback do usuário.

## [1.1.0] - 23/05/2025

### Adicionado
- **Interação e Pedagogia Aprimoradas:** Saudação padrão, sugestão de tópicos, novas estratégias de ensino (celebração de marcos, perguntas de sondagem), melhorias na gestão da conversa e maior clareza nas limitações do assistente.
- **Expansão de Tipos de Solicitação:** Suporte a brainstorming, comparações, explicações passo a passo, definições rápidas, role-playing e criação de estruturas.

### Alterado
- **Persona e Diretrizes:** Refinamento na expressão de empatia, adaptação de tom e política de uso de recursos externos.

## [1.0.0] - 18/05/2025

### Adicionado
- **Lançamento Inicial do Conrad:** Assistente educativo pessoal com personalidade base, 10 estratégias de ensino fundamentais e interface de chat interativa via console.
