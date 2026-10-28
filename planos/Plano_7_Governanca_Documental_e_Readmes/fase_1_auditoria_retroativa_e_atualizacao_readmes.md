# 📋 Especificação Técnica de Engenharia — Plano 7: Fase 1
**Projeto:** Conrad — Assistente Cognitivo e Pedagógico  
**Ciclo:** Plano 7 — Governança Documental, Sincronização de READMEs e Auditoria de Releases  
**Etapa:** Fase 1 — Auditoria Retroativa de Recursos e Atualização Integral dos READMEs (PT-BR e ENG)  
**Destinatário:** Argon (Desenvolvedor de Software)  
**Revisor:** Arquiteto Líder  

---

## 1. Diagnóstico do Problema & Causa Raiz

### 1.1. O Descompasso Documental (READMEs Parados na v1.5.1)
* **Situação Atual:** O projeto evoluiu intensamente nos últimos ciclos (novo SDK `google-genai`, motor padrão `gemini-3.8-flash` com 1M tokens, aplicação web autônoma com Streamlit, backend FastAPI, sistema BYOK com onboarding, Quadro Negro Split-View com MathJax e Mermaid, 4 Modos Pedagógicos, Caderno Digital em PDF/MD e Floating Input Dock).
* **O Problema:** Os arquivos [`README(PT-BR).md`](file:///c:/Users/enric/Downloads/ProjetoConrad/repo/README(PT-BR).md) e [`README(ENG).md`](file:///c:/Users/enric/Downloads/ProjetoConrad/repo/README(ENG).md) ainda descrevem o Conrad de setembro de 2025: mencionam apenas o Google Colab com `ipywidgets`, citam o modelo antigo `gemini-2.5-flash` e possuem links antigos do repositório (`ImersaoGemini_Alura_Conrad` em vez de `Conrad`).
* **Objetivo Desta Fase:** O Argon deve auditar o código real em execução e reescrever integralmente ambos os READMEs, preservando rigorosamente o estilo visual clássico criado por Enrico (banner centralizado, badges de tecnologia, sumário com emojis e seções claras), mas apresentando o produto no seu estado da arte contemporâneo.

---

## 2. Arquivos Afetados
* **Modificar:** `README(PT-BR).md` (Reescrita completa em Português com arquitetura v3.x, guia de execução Web App + Colab e funcionalidades modernas).
* **Modificar:** `README(ENG).md` (Reescrita completa em Inglês espelhando fielmente a versão em português).
* **Modificar:** `CHANGELOG.md` (Registrar versão 3.3.0 — Atualização Integral da Documentação Oficial).

---

## 3. Instruções Técnicas Passo a Passo

### 3.1. Auditoria e Matriz de Funcionalidades a Documentar
O Argon deve conferir se todas as seguintes inovações estão descritas em ambos os READMEs:
1. **Modelos e Inteligência:** Motor `google-genai` com `gemini-3.8-flash` (1M tokens) e seletor de modelos estáveis (Gemini 2.5 Pro/Flash).
2. **Duplo Ambiente de Execução:**
   * **Aplicação Web Autônoma:** Execução local com `streamlit run app.py` ou via container Docker (`docker-compose up`).
   * **Notebook Google Colab:** Execução no Colab com `Conrad.ipynb` (com o link do badge corrigido para `EnricoSouzaAfonso/Conrad`).
3. **Quadro Negro do Conrad (Canvas / Split-View):** Lousa lateral reativa com deduções em LaTeX/MathJax e diagramas conceituais em Mermaid.js.
4. **Modos Pedagógicos Especializados:** Socrático Puro, Simulado & Desafio, Arquiteto de Software e Método Feynman.
5. **Sistema BYOK (Bring Your Own Key):** Input de chave com validação em tempo real e tutorial passo a passo integrado.
6. **Caderno Digital & Métricas:** Exportação de resumo de estudos em Markdown (`.md`) e PDF diagramado, acompanhado do Termômetro de Retenção Cognitiva.
7. **Floating Input Dock:** Barra de perguntas flutuante estilo Gemini/Claude no rodapé, com scrollbar única e botão de retorno rápido (`↓`).

---

### 3.2. Estrutura Padrão Obrigatória para os READMEs
O Argon deve manter a identidade visual estabelecida por Enrico:

```markdown
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

**Conrad é um assistente pedagógico inteligente de alta performance, concebido para atuar como tutor socrático individualizado...**

---

## 📋 Índice
- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Arquitetura de Software](#arquitetura-de-software)
- [Como Executar o Conrad](#como-executar-o-conrad)
  - [Opção 1: Aplicação Web Local (Streamlit)](#opcao-1-aplicacao-web-local-streamlit)
  - [Opção 2: Container Docker](#opcao-2-container-docker)
  - [Opção 3: Google Colab](#opcao-3-google-colab)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Modos Pedagógicos](#modos-pedagógicos)
- [Desenvolvido por](#desenvolvido-por)
- [Licença](#licença)
```

---

## 4. Critério de Validação (Definition of Done)
1. **Auditoria de Fatos (Zero Mentiras):** Cada funcionalidade descrita no `README(PT-BR).md` e `README(ENG).md` DEVE corresponder a código real, funcional e testado no repositório.
2. **Espelhamento Bilíngue Perfeito:** Nenhuma seção ou instrução presente na versão em português pode faltar na versão em inglês.
3. **Links e Badges Válidos:** O badge do Google Colab deve apontar para o repositório correto (`EnricoSouzaAfonso/Conrad`).
4. **Commit & Push:** Commitar com a mensagem:  
   `docs: atualizacao integral dos READMEs em portugues e ingles para v3.3`
