# Pydah AI - Core LLM Console & API Service

This repository provides the core, modular AI integration layer for PydahSoft applications. 
It supports both an interactive console terminal client and a high-performance FastAPI REST API service.

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
│   ├── console.py        # Terminal interface & message context management
│   ├── schemas.py        # Pydantic request & response schemas
│   └── api.py            # FastAPI service application & routes
├── tests/
│   ├── __init__.py
│   ├── test_config.py    # Unit tests for configuration logic
│   ├── test_llm_client.py# Unit tests for LLM client request/error handling
│   ├── test_console.py   # Unit tests for conversation history truncation
│   └── test_api.py       # Unit tests for REST API endpoints
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusion rules
├── requirements.txt      # Project dependencies
├── main.py               # Console application entry point
├── server.py             # REST API server entry point
└── README.md             # Setup and usage guide
```

---

## 2. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your OpenRouter API key and desired model:
   ```env
   OPENROUTER_API_KEY=your_actual_openrouter_api_key
   OPENROUTER_MODEL=nvidia/nemotron-3.5-lightning:free
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
   REQUEST_TIMEOUT_SECONDS=30
   MAX_HISTORY_MESSAGES=10
   ```

---

## 3. Setup Instructions

### Virtual Environment Setup

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

## 4. Running the Application

### Option A: Interactive Console Interface

Start the terminal console session:

```bash
python main.py
```

### Option B: FastAPI REST API Server

Start the API service server:

```bash
python server.py
```

The server will launch at `http://localhost:8000`.

* **Health Endpoint:** `GET http://localhost:8000/health`
* **Chat Endpoint:** `POST http://localhost:8000/api/v1/chat`
* **Interactive Swagger UI Documentation:** `http://localhost:8000/docs`

---

## 5. REST API Usage Examples

### Health Check Request

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-core-service-api"
}
```

### Chat Completion Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is artificial intelligence?",
       "conversation_id": "session-101"
     }'
```

**Successful Response (200 OK):**
```json
{
  "success": true,
  "answer": "Artificial intelligence (AI) is the intelligence of machines or software...",
  "model": "nvidia/nemotron-3.5-lightning:free",
  "conversation_id": "session-101"
}
```

### Chat Request with Multi-turn Context History

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is my name?",
       "history": [
         {"role": "user", "content": "My name is Durga."},
         {"role": "assistant", "content": "Nice to meet you, Durga!"}
       ]
     }'
```

**Response:**
```json
{
  "success": true,
  "answer": "Your name is Durga.",
  "model": "nvidia/nemotron-3.5-lightning:free",
  "conversation_id": null
}
```

---

## 6. Running Automated Tests

Run all unit tests (for configuration, LLM client, console app, and FastAPI endpoints):

```bash
python -m unittest discover -s tests
```