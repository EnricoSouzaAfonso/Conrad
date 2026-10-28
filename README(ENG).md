<p align="center">
  <img src="Conrad_Logo.jpg" alt="Conrad's Logo" width="700"/>
</p>

# Conrad - Personal Socratic AI Learning Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Gemini-3.8%20Flash%20(1M%20Tokens)-purple.svg)](https://ai.google.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend%20API-teal.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Container-blue.svg)](https://www.docker.com/)
[![Google Colab](https://img.shields.io/badge/Google%20Colab-notebook-orange.svg)](https://colab.research.google.com/github/EnricoSouzaAfonso/Conrad/blob/main/Conrad.ipynb)
[![License](https://img.shields.io/badge/License-CC--BY--NC--4.0-lightgrey.svg)](LICENSE)

**Conrad is a high-performance intelligent pedagogical assistant designed to act as an individualized Socratic tutor. Powered by the modern `google-genai` SDK and the Google Gemini model family (with up to a 1,048,576-token context window), Conrad guides students in actively building knowledge through inductive questioning, an interactive blackboard, and evidence-based learning science.**

---

## 📋 Table of Contents
- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Software Architecture](#software-architecture)
- [How to Run Conrad](#how-to-run-conrad)
  - [Option 1: Local Web Application (Streamlit)](#option-1-local-web-application-streamlit)
  - [Option 2: Docker Container](#option-2-docker-container)
  - [Option 3: Google Colab](#option-3-google-colab)
- [Technologies Used](#technologies-used)
- [Pedagogical Modes](#pedagogical-modes)
- [Version History](#version-history)
- [Contributing](#contributing)
- [Developed by](#developed-by)
- [License](#license)

---

## 🎩 About the Project

**Conrad** was created with the mission of transforming generative artificial intelligence into a true cognitive study partner—rather than an answer-giving machine that bypasses critical thinking. Represented by his signature Victorian top hat (🎩), Conrad combines epistemological rigor, empathy, and next-generation UI engineering.

In its **v3.3** architecture, Conrad operates on four scientific pillars of education:
1. **Revised Bloom's Taxonomy:** Structured progression guiding learners from remembering and understanding up to analyzing, evaluating, and creating.
2. **Cognitive Load Theory (John Sweller):** Strict enforcement of the *Single-Question Rule* (at most one reflective question per turn) and separation between concise chat dialogue and heavy visual derivations.
3. **Zone of Proximal Development & Scaffolding (Lev Vygotsky):** Graduated 3-tier scaffolding (Conceptual Hint, Structural Hint, and Partial Analogous Example) with progressive *Fading*.
4. **Growth Mindset (Carol Dweck):** Process-oriented praise and reframing errors as valuable opportunities for neuroplasticity and deeper mastery.

---

## ✨ Key Features

- **🧠 `google-genai` Cognitive Engine (1M Tokens):** Configured by default with `gemini-3.8-flash` alongside an integrated sidebar selector for active models (`gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.1-flash-lite`, and `gemini-3.1-pro-preview`), featuring transparent failover against demand spikes and smooth ~25fps streaming (`40ms` throttle).
- **📐 Conrad's Blackboard (Collapsible Split-View Canvas):** A retractable side panel (`✖ Ocultar Lousa` / `📐 Abrir Lousa`) inspired by *Claude Artifacts*. Collapses to expand the centered chat and automatically opens (*Auto-Reveal*) whenever Conrad projects algebraic derivations in **LaTeX/MathJax v3**, conceptual diagrams in **Mermaid.js** (with syntax validation and auto-repair), or formatted code blocks.
- **💎 Customizable Pedagogical Gems (Full SQLite CRUD):** In addition to the 4 protected built-in Gems (*Pure Socratic*, *Exam & Challenge*, *Software Architect*, and *Feynman Method*), students and teachers can create, edit, and delete their own specialized Gems for any subject (e.g., *Essay Writing*, *Molecular Biology*, *World History*) directly in the sidebar.
- **💬 Floating Input Dock with `➕` Upload Button & Persistent Floating Blackboard Button (`100dvh`):** A pill-shaped floating prompt bar paired with a circular `➕` attachment popover (`st.popover`) and floating file preview chip, plus a persistent fixed top-right button (`position: fixed`) that keeps the Blackboard toggle (`📐 Abrir Lousa` / `✖ Ocultar Lousa`) 100% accessible regardless of chat scroll position.
- **🔍 Pedagogical Chain-of-Thought (`<conrad_thought>`):** An expandable accordion (*"🧠 Raciocínio Pedagógico do Conrad"*) that transparently reveals the student's diagnosed Bloom level and the Socratic strategy chosen for each response.
- **📎 Multimodal Study Vision:** Direct upload of notebook photos, scratchpad sheets, or problem sets in `.png`, `.jpg`, and `.pdf` via the `➕` button in the Floating Dock for automatic problem transcription onto the Blackboard and step-by-step guidance.
- **🧬 Persistent Multidisciplinary Cognitive Memory (SQLite):** Continuous, subject-neutral tracking of the student's strengths, evolving difficulties, and learning style in a local relational database (`src/database.py`), with one-click reset to school-wide multidisciplinary defaults.
- **📓 Concurrency-Safe Digital Notebook & Micro-Retention Thermometer:** Instant compilation of the study session for download as **Markdown (`.md`)** and **typeset PDF (`.pdf`)** (with concurrency lock while AI streaming is active), paired with a compact 6px Cognitive Retention Thermometer featuring a rich hover tooltip.
- **🔑 Top-of-Sidebar BYOK (Bring Your Own Key) System:** Ergonomically positioned Gemini API key input at the very top of the sidebar, millisecond canonical validation via `client.models.list()`, *Zero Crash* protection when no key is configured, and an integrated step-by-step onboarding guide.

---

## 🏗️ Software Architecture

The project follows a decoupled modular architecture (*Clean Architecture*), allowing the same cognitive core to power the Streamlit Web App, the FastAPI RESTful backend, and the Google Colab notebook:

```text
Conrad/
├── app.py                        # Main Web Application (Streamlit Split-View + Floating Dock)
├── Conrad.ipynb                  # Interactive Notebook for cloud execution on Google Colab
├── Dockerfile                    # Container image for reproducible deployment
├── docker-compose.yml            # Orchestration for Web (Streamlit) and API (FastAPI) services
├── requirements.txt              # Pinned dependencies for the v3.x ecosystem
├── src/
│   ├── conrad_core.py            # GenAI Engine (google-genai), Streaming, Multimodal & BYOK Validation
│   ├── conrad_persona.py         # Master Prompt v3.x, Socratic Persona & MathJax Shielding
│   ├── conrad_pedagogy.py        # Pedagogical Governance (Bloom, Sweller, Vygotsky, Dweck & 4 Modes)
│   ├── conrad_canvas.py          # Parser for <conrad_artifact>, <conrad_thought> & Mermaid auto-repair
│   ├── conrad_analytics.py       # Heuristic Cognitive Retention & Active Engagement Thermometer
│   ├── conrad_report.py          # Digital Notebook Compiler for Markdown (.md) and PDF (fpdf2)
│   ├── database.py               # SQLAlchemy + SQLite Persistence (Cognitive Profile & Sessions)
│   ├── api.py                    # FastAPI RESTful Backend (/health, /chat, /sessions)
│   └── conrad_ui.py              # Interactive ipywidgets interface for Google Colab
└── tests/
    ├── qa_visual_inspection.py   # End-to-End QA Suite + Headless Visual Inspection + Doc Governance
    ├── test_pedagogical_rigor.py # Automated audit for Bloom, Sweller, Dweck & Anti-Sycophancy
    ├── test_chaos_and_edge_cases.py # Stress Testing Battery, XSS, LaTeX & HTTP Resilience
    ├── test_canvas_artifacts.py  # Unit tests for the Blackboard parser and CoT extraction
    ├── test_api_and_database.py  # Tests for FastAPI endpoints, SQLite DB & BYOK validation
    └── test_persona_and_rules.py # Integrity tests for the persona's inviolable rules
```

---

## 🚀 How to Run Conrad

### Option 1: Local Web Application (Streamlit)

1. **Clone the repository and navigate into the project folder:**
   ```bash
   git clone https://github.com/EnricoSouzaAfonso/Conrad.git
   cd Conrad
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   # On Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Launch the Web Application:**
   ```bash
   streamlit run app.py
   ```

4. **Configure your API Key (BYOK):**
   - Open `http://localhost:8501` in your browser.
   - In the left sidebar (**"🔑 Chave da API Gemini (BYOK)"**), paste your free key from [Google AI Studio](https://aistudio.google.com/app/apikey) and click **"Salvar e Validar Chave"** (or set `GOOGLE_API_KEY` in a `.env` file).

---

### Option 2: Docker Container

To spin up both the Web Application (`port 8501`) and the FastAPI backend (`port 8000`) in isolated containers:

```bash
docker-compose up --build
```

- **Web Interface (Streamlit):** `http://localhost:8501`
- **Interactive API Documentation (Swagger UI):** `http://localhost:8000/docs`

---

### Option 3: Google Colab

You can also run Conrad directly in the cloud with zero local setup:

1. Click the badge below to open the official notebook in Google Colab:

   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnricoSouzaAfonso/Conrad/blob/main/Conrad.ipynb)

2. In the left sidebar of Google Colab, click the **Key (Secrets)** icon and add a secret named `GOOGLE_API_KEY` with your key from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Run the cells sequentially to install `google-genai` and launch the interactive interface.

---

## 🛠️ Technologies Used

- **Core Language:** [Python 3.11+](https://www.python.org/)
- **Generative AI SDK:** [Google GenAI SDK (`google-genai`)](https://ai.google.dev/) — Models `gemini-3.8-flash` (default, 1M tokens), `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.1-flash-lite`, and `gemini-3.1-pro-preview`
- **Web Frontend:** [Streamlit](https://streamlit.io/) + Modern CSS3 (`100dvh` Viewport, Floating Input Dock, Glassmorphism)
- **Scientific Rendering & Diagrams:** [MathJax v3](https://www.mathjax.org/) (LaTeX/TeX) and [Mermaid.js v10](https://mermaid.js.org/)
- **Backend & Persistence:** [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), and [SQLite](https://www.sqlite.org/)
- **Document Export:** [FPDF2 (`fpdf2`)](https://py-pdf.github.io/fpdf2/) and [Markdown2](https://github.com/trentm/python-markdown2)
- **Containerization & Notebook:** [Docker](https://www.docker.com/) and [IPython Widgets (`ipywidgets`)](https://ipywidgets.readthedocs.io/en/stable/)

---

## 🎯 Pedagogical Modes

In Conrad's sidebar, you can switch in real time between **4 specialized teaching modes**:

| Pedagogical Mode | Didactic Goal | Conrad's Behavior |
| :--- | :--- | :--- |
| **🎓 Pure Socratic (Default)** | Autonomous concept building from first principles | Guides the student with inductive questions and graduated hints without ever handing out ready-made answers. |
| **📝 Exam & Challenge Mode** | Rigorous preparation for exams and competitions | Presents contextualized challenge problems, evaluates step-by-step justifications, and demands formal rigor. |
| **💻 Software Architect (Code Review)** | Software engineering, algorithms, and debugging | Analyzes Big-O complexity ($O(n)$, $O(\log n)$), clean code, and edge cases without rewriting the entire program for the student. |
| **🔄 Feynman Method (Role Reversal)** | Deep consolidation and blind-spot detection | Conrad takes on the role of a curious apprentice and asks **you** to explain the topic in your own words, probing logical gaps. |

---

## 📜 Version History

For a detailed log of all releases, architectural milestones, and bug fixes following *Keep a Changelog* and *Semantic Versioning*, see [**CHANGELOG.md**](CHANGELOG.md).

---

## 🤝 Contributing

Contributions are warmly welcomed! To help improve Conrad:

1. **Fork** the project.
2. **Create a Feature Branch** (`git checkout -b feat/MyInnovation`).
3. **Run the official QA & Governance suite** (`python tests/qa_visual_inspection.py`).
4. **Commit your changes** following *Conventional Commits* (`git commit -m 'feat: add MyInnovation'`).
5. **Push to the branch** (`git push origin feat/MyInnovation`) and open a **Pull Request**.

---

## 👨‍💻 Developed by

Conceived and developed by **Enrico Souza Afonso** (originally created on May 17, 2025, during the Alura Gemini Immersion and continuously evolved into the v3.3 Web & Cognitive architecture).

---

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0)** license.

[![License: CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc/4.0/)

You can read the full license terms in the [LICENSE](LICENSE) file or at [creativecommons.org/licenses/by-nc/4.0](https://creativecommons.org/licenses/by-nc/4.0/).
