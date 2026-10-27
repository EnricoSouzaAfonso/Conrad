# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [3.3.0] - 27/10/2026

### Documentação
- **Atualização Integral dos READMEs Oficiais em Português e Inglês (`README(PT-BR).md`, `README(ENG).md`):** Reescrita completa e espelhada da documentação oficial da arquitetura v3.3, preservando o layout clássico (logo centralizado, badges tecnológicos e sumário navegável) e documentando o SDK `google-genai` (`gemini-3.8-flash` 1M tokens), aplicação Web Streamlit, API FastAPI, containerização Docker, Quadro Negro Retrátil com *Auto-Reveal*, 4 Modos Pedagógicos científicos, Sistema BYOK, Caderno Digital em PDF/Markdown e Floating Input Dock.

## [3.2.1] - 27/10/2026

### Corrigido
- **Extinção da Scrollbar Rígida na Coluna do Quadro Negro (`app.py`):** Substituição do `overflow-y: auto` permanente na coluna direita (`div[data-testid="stColumn"]:last-child`) por `height: auto !important; overflow: visible !important;`, delegando a rolagem exclusivamente ao card interno (`div[data-testid="stVerticalBlockBorderWrapper"]`) com `max-height: calc(100dvh - 160px)` e barra invisível por padrão (`scrollbar-color: transparent transparent`), revelada sutilmente apenas em `:hover` (`#444444 transparent`).

## [3.2.0] - 27/10/2026

### Adicionado
- **Quadro Negro Retrátil (Collapsible Canvas Drawer) e Expansão Dinâmica do Chat (`app.py`):** Implementação do estado reativo `st.session_state.canvas_collapsed`, botão de alternância (`✖ Ocultar Lousa` / `📐 Abrir Lousa`) no cabeçalho do chat, expansão centralizada (`max-width: 820px`) com reposicionamento automático do Floating Input Dock quando a lousa está recolhida e abertura automática (*Auto-Reveal*) estilo Claude Artifacts ao receber novos artefatos matemáticos, de código ou diagramas.

## [3.1.1] - 27/10/2026

### Adicionado
- **Floating Input Dock Estilo Gemini/Claude/Grok (`app.py`):** Ancoragem da barra de perguntas (`div[data-testid="stChatInput"]`) fora do fluxo descendente com `position: fixed; bottom: 24px; border-radius: 28px; backdrop-filter: blur(16px)` e destaque dourado (`#C59B27`) no foco, garantindo que o campo de digitação jamais se desloque ou suma da tela durante respostas longas.
- **Botão Flutuante Scroll-to-Bottom (`#jump-to-bottom-btn`) e Espaçador de Segurança (`app.py`):** Adição do botão circular `↓` com rolagem suave (`scrollTo({ top: chatCol.scrollHeight, behavior: 'smooth' })`) e âncora `.chat-bottom-spacer` (`height: 120px`) para impedir que o Floating Dock cubra a última linha das mensagens.

## [3.1.0] - 27/10/2026

### Corrigido
- **Extinção da Barra Dupla de Rolagem e Unificação de Viewport 100dvh (`app.py`):** Remoção dos contêineres de scroll aninhados (`.chat-scroll-area`) e travamento estrutural de `html, body, [data-testid="stAppViewContainer"]` e `[data-testid="stMainBlockContainer"]` em `100dvh` (`overflow: hidden`), concentrando a rolagem exclusivamente nas trilhas independentes `div[data-testid="stColumn"]:first-child` e `div[data-testid="stColumn"]:last-child` com `scrollbar-gutter: stable`, `scrollbar-width: thin` e `scrollbar-color`.

## [3.0.1] - 27/10/2026

### Adicionado
- **Suíte Automatizada de Avaliação Heurística e Rigor Pedagógico (`tests/test_pedagogical_rigor.py`, `tests/qa_visual_inspection.py`):** Validação automatizada da conformidade epistemológica do Conrad v3.0 (Recusa Construtiva / Não-Passividade, Regra da Pergunta Única de Sweller, Proibição de Elogio à Inteligência Inata de Dweck, Anti-Sycophancy e Blindagem LaTeX), integrada como Passo 5/5 no protocolo obrigatório de QA.

## [3.0.0] - 27/10/2026

### Adicionado
- **Engenharia do Prompt Mestre v3.0 (`src/conrad_persona.py`):** Reescritura integral de `SYSTEM_INSTRUCTION_CONRAD` (v3.0.0) estruturada em 8 eixos científicos: Regra de Ouro da Não-Passividade (Recusa Construtiva), Gestão de Carga Cognitiva e Regra da Pergunta Única (Sweller), Scaffolding Dinâmico, Fading e Retrieval Practice (Vygotsky/Roediger), Linguagem de Mentalidade de Crescimento (Carol Dweck), Anti-Sycophancy e Protocolo de 3 Passos, Blindagem MathJax, Protocolo do Quadro Negro e Regras Invioláveis.

## [3.0.0-dev] - 27/10/2026

### Adicionado
- **Framework Pedagógico Baseado em Evidências (`src/conrad_pedagogy.py`):** Criação do módulo científico de governança pedagógica contendo os 6 níveis da Taxonomia de Bloom Revisada (`BLOOM_LEVELS`), heurísticas de Mentalidade de Crescimento (`GROWTH_MINDSET_RULES`), diretrizes de Carga Cognitiva de Sweller (`SWELLER_LOAD_RULES`), andaimes de Vygotsky (`VYGOTSKY_ZPD_RULES`) e modos especializados (`PEDAGOGICAL_MODES`).

## [2.6.2] - 23/10/2026

### Adicionado
- **Protocolo Operacional Anti-Vibe Coding Cego (`tests/qa_visual_inspection.py`):** Script de inspeção visual automatizada ponta a ponta que executa toda a suíte unitária, valida a chave de API real/falsa sem falso-positivo, verifica a integridade DOM do Quadro Negro e Layout Sticky, sobe o servidor Streamlit em modo headless e captura evidências visuais e logs de auditoria em `tests/screenshots/`.

## [2.6.1] - 23/10/2026

### Corrigido
- **Encapsulamento Estrito do Quadro Negro (`app.py`, `src/conrad_canvas.py`):** Substituição das tags HTML abertas `<div class="canvas-container">` por contêineres nativos `st.container(border=True)` estilizados via `div[data-testid="stVerticalBlockBorderWrapper"]`, garantindo que fórmulas MathJax/KaTeX, diagramas Mermaid e blocos de código renderizem 100% dentro da moldura da lousa.
- **Área de Perguntas Fixa no Rodapé e Scroll Independente (`app.py`):** Aplicação das diretrizes de estabilidade de layout (`max-height: calc(100dvh - 220px)`, `overflow-y: auto`, `scrollbar-gutter: stable`, `overscroll-behavior: contain`) no contêiner de mensagens e fixação de `.stChatInput` com `position: sticky; bottom: 0; backdrop-filter: blur(12px)`.

## [2.6.0] - 23/10/2026

### Corrigido
- **Validação Canônica da API Key com Zero Falso-Positivo (`src/conrad_core.py`, `tests/test_api_and_database.py`):** Refatoração de `validate_api_key()` para consultar `client.models.list()` em vez de disparar gerações de conteúdo, validando credenciais reais em milissegundos sem gastar tokens e rejeitando exclusivamente erros reais de autenticação (`API_KEY_INVALID`, `PERMISSION_DENIED`, `UNAUTHENTICATED`).
- **Otimização de Latência e Buffer de Streaming (`app.py`, `src/conrad_core.py`):** Implementação de throttling temporal (`RENDER_THROTTLE_SECONDS = 0.04` / ~25fps) durante o streaming no `app.py` e execução única do parser do Canvas ao final da resposta, eliminando gargalos de reconstrução de DOM a cada caractere.

## [2.5.0] - 23/10/2026

### Adicionado
- **Compilador do Caderno Digital de Estudos (`src/conrad_report.py`, `app.py`):** Implementação da classe `ConradNotebookCompiler` com geração de material estruturado contendo todos os artifacts do Quadro Negro, síntese do diálogo e Flashcards de revisão, exportável em Markdown (`caderno_conrad.md`) e PDF diagramado via ReportLab (`caderno_conrad.pdf`).
- **Termômetro de Retenção Cognitiva (`src/conrad_analytics.py`, `app.py`):** Módulo `CognitiveRetentionTracker` que avalia em tempo real o índice de autonomia e retenção cognitiva do aluno (*Iniciando*, *Em Construção*, *Boa Compreensão* e *Excelente Autonomia*), exibindo barra de progresso e diagnóstico formativo no menu lateral.
- **Folha de Estilo de Impressão (`app.py`):** Regras CSS `@media print` para impressão limpa da sessão de estudos (`Ctrl+P`).
- **Suíte de Testes do Caderno e Analytics (`tests/test_caderno_and_analytics.py`):** Validação automatizada da geração de Markdown/PDF e cálculo das faixas do Termômetro de Retenção.

## [2.4.0] - 23/10/2026

### Adicionado
- **Memória Pedagógica Persistente (`src/database.py`, `src/conrad_core.py`, `app.py`):** Nova tabela ORM `StudentCognitiveProfile` e funções `get_or_create_profile()` / `update_profile()` para salvar pontos fortes, temas em evolução, estilo de aprendizado e notas pedagógicas em `conrad_data.db`, com injeção automática no contexto (`build_context_with_memory()`).
- **Tutoria Multimodal Nativa para Fotos & PDFs (`src/conrad_core.py`, `app.py`):** Método `send_message_multimodal()` utilizando `types.Part.from_bytes()` do SDK `google-genai` e widget `st.file_uploader` para envio de fotos de caderno (`PNG`/`JPG`) e listas de exercícios em `PDF`, transcrevendo enunciados diretamente para o Quadro Negro.
- **Suíte de Testes Multimodais e de Memória (`tests/test_multimodal_and_memory.py`):** Validação automatizada de persistência do perfil cognitivo e envio de mídias binárias (imagens e PDFs) com extração no Canvas.

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
