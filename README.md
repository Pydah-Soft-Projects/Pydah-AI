# Pydah AI - Core LLM Console Service

This repository provides the core, modular AI integration layer for PydahSoft applications. 
The current phase implements a direct console-based interactive client powered by OpenRouter LLMs.

---

## 1. Project Architecture & Components

The application is structured into generic, reusable modules:

```text
pydah-ai/
├── docs/
│   └── Pydah_AI_Backend_Detailed_Plan.docx
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration loading & validation
│   ├── llm_client.py     # OpenRouter API communication adapter
│   └── console.py        # Terminal interface & message context management
├── tests/
│   ├── __init__.py
│   ├── test_config.py    # Unit tests for configuration logic
│   ├── test_llm_client.py# Unit tests for LLM client request/error handling
│   └── test_console.py   # Unit tests for conversation history truncation
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusion rules
├── requirements.txt      # Project dependencies
├── main.py               # Application entry point
└── README.md             # Setup and usage guide
```

---

## 2. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_actual_openrouter_api_key
   OPENROUTER_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
   REQUEST_TIMEOUT_SECONDS=30
   MAX_HISTORY_MESSAGES=10
   ```

---

## 3. Setup Instructions

### Create and Activate Virtual Environment

**On Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Running the Console Application

Start the interactive session:

```bash
python main.py
```

### Example Console Session:

```text
============================================================
 Welcome to Pydah AI Assistant Console
 Configured Model: google/gemini-2.0-flash-lite-preview-02-05:free
 Type 'exit' or 'quit' to close the session.
============================================================

User > What is artificial intelligence?
Pydah AI > Artificial intelligence (AI) refers to the simulation of human intelligence in machines...

User > My name is Durga.
Pydah AI > Nice to meet you, Durga! How can I assist you today?

User > What is my name?
Pydah AI > Your name is Durga.

User > exit
Exiting Pydah AI Console. Goodbye!
```

---

## 5. Running Automated Tests

Run the unit test suite without needing external API calls:

```bash
python -m unittest discover -s tests
```