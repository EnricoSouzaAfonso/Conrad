# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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
