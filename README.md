# Pydah AI - Central GenAI Engine & Application Integration Guide

This repository contains the central **Pydah AI Engine (`pydah-ai`)**, providing unified GenAI orchestration, multi-assistant personas, tool selection, and secure tool execution across PydahSoft applications (Fee Management, Transport, Student Portal, HRMS, etc.).

---

## 1. System Architecture & Division of Responsibilities

```
                               ┌────────────────────────────────┐
                               │  CDN Chat UI / Host Application│
                               └───────────────┬────────────────┘
                                               │ ChatRequest + assistant_id + Bearer Token
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ pydah-ai (Central AI Backend)                                                           │
│  ├── src/api.py                 -> Receives chat requests from CDN UI                   │
│  ├── src/assistants/config.py   -> Defines assistants & their allowed tools             │
│  ├── src/tools/registry.py      -> Tool schemas & parameters for OpenRouter LLM         │
│  ├── src/tools/executor.py      -> Dispatches tool execution to target application APIs │
│  ├── src/services/llm_service.py-> Handles multi-turn tool calling loop with OpenRouter │
│  └── src/security/auth.py       -> Extracts user security token context                 │
└──────────────────────────────┬──────────────────────────────────────────────────────────┘
                               │ Dispatches: POST /execute-tool (tool_name, args, Bearer token)
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ Each Existing Application Backend (Fee, Transport, Student Portal, HRMS, etc.)           │
│  └── ai_integration/                                                                    │
│       ├── tools.py / tools.js        -> Wraps existing app services to fetch data        │
│       ├── permissions.py / perm.js   -> Verifies student/user access permissions        │
│       └── routes.py / routes.js      -> Exposes /execute-tool API endpoint for pydah-ai│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Core Principles:
- **`pydah-ai` Central Backend:** Understands the question, selects the right tool, dispatches the tool call to the application with the user's token, and generates the final natural language answer.
- **Application Backend:** Defines AI-facing tools in an `ai_integration/` folder, wraps existing application business logic/services, and enforces data access permissions.
- **CDN Chat UI:** Renders the chat interface, sends questions & `assistant_id`, and displays responses.

---

## 2. Central `pydah-ai` Structure & Responsibilities

```text
pydah-ai/
├── src/
│   ├── api.py                   # FastAPI chat endpoint & assistant API routes
│   ├── config.py                # Environment & model configuration loader
│   ├── llm_client.py            # OpenRouter HTTP API client (urllib)
│   ├── schemas.py               # Pydantic data schemas (ChatRequest, ChatResponse)
│   ├── assistants/              
│   │   ├── config.py            # Defines personas (student-assistant, fee-assistant, etc.)
│   │   └── resolver.py          # Resolves requested assistant_id and tool scope
│   ├── tools/                   
│   │   ├── registry.py          # Tool definitions & schemas for OpenRouter
│   │   ├── executor.py          # Enforces permissions & calls target application APIs
│   │   ├── generic_connector.py # Dispatches (tool_name, args) to app /execute-tool
│   │   └── handlers/            # Fallback & local dev tool handlers
│   ├── security/                
│   │   └── auth.py              # Extracts Bearer tokens & user context
│   └── services/                
│       └── llm_service.py       # OpenRouter tool-calling orchestration loop
├── requirements.txt             # Dependencies (FastAPI, Uvicorn, Pydantic, etc.)
├── server.py                    # REST API launcher
└── README.md                    # System guide & integration documentation
```

### Module Responsibilities inside `pydah-ai`:

| File Path | Responsibility |
| :--- | :--- |
| **`src/api.py`** | Receives `/api/v1/chat` requests from CDN chat UI. |
| **`src/assistants/config.py`** | Defines each assistant (`fee-assistant`, `student-assistant`, `transport-assistant`) and its permitted tool list. |
| **`src/tools/registry.py`** | Describes available tools and parameter schemas to the OpenRouter LLM. |
| **`src/tools/executor.py`** | Validates permission scope and calls the target application when a tool is selected. |
| **`src/services/llm_service.py`** | Coordinates OpenRouter model requests, executes tool loops, and generates final answers. |
| **`src/security/auth.py`** | Validates user identity and extracts delegated Bearer tokens. |

---

## 3. Integration Guide for Other Application Teams

To connect an existing application (Fee Management, Transport, Student Portal, HRMS, etc.) to the central AI system, **you do NOT need an LLM or separate AI engine inside your application**.

Simply add an `ai_integration/` folder inside your backend codebase.

### Application Folder Structure

```text
your-application/backend/
├── routes/
├── controllers/
├── services/
└── ai_integration/              <-- ADD THIS FOLDER IN YOUR APPLICATION BACKEND
    ├── tools.py / tools.js      # Wraps existing application services to retrieve data
    ├── permissions.py / perm.js # Verifies user context and record permissions
    └── routes.py / routes.js    # Exposes /execute-tool endpoint for pydah-ai
```

---

### File Responsibilities in Your Application:

#### 1. `tools.py` (or `tools.js`)
Wraps your existing application services. Reuse your existing data access functions rather than recreating calculation logic.

**Python Example (`tools.py`):**
```python
# ai_integration/tools.py
from services.fee_service import FeeService

async def get_my_pending_dues(user_context: dict, academic_year: str = None):
    # Retrieve student identity from trusted user context
    student_id = user_context["user_id"]
    
    # Call existing fee calculation service
    return await FeeService.get_pending_dues(
        student_id=student_id,
        academic_year=academic_year
    )
```

**Node.js Example (`tools.js`):**
```javascript
// ai_integration/tools.js
const FeeService = require('../services/FeeService');

async function get_my_pending_dues(userContext, args) {
  const studentId = userContext.userId;
  const academicYear = args.academic_year;

  // Call existing application service
  return await FeeService.getPendingDues(studentId, academicYear);
}

module.exports = { get_my_pending_dues };
```

---

#### 2. `permissions.py` (or `permissions.js`)
Enforces record-level security so users can access only their authorized data.

```python
# ai_integration/permissions.py
def check_student_access(user_context: dict, target_student_id: str):
    if user_context["role"] == "student" and user_context["user_id"] != target_student_id:
        raise PermissionError("Access denied: You can only query your own student records.")
```

---

#### 3. `routes.py` (or `routes.js`)
Exposes a single `/execute-tool` endpoint for `pydah-ai` to dispatch tool calls.

**Node.js Express Example (`routes.js`):**
```javascript
// ai_integration/routes.js
const express = require('express');
const router = express.Router();
const { authenticateUser } = require('../middleware/auth');
const tools = require('./tools');

router.post('/execute-tool', authenticateUser, async (req, res) => {
  const { tool_name, arguments: args } = req.body;
  const userContext = { userId: req.user.id, role: req.user.role };

  try {
    if (typeof tools[tool_name] === 'function') {
      const data = await tools[tool_name](userContext, args);
      return res.json(data);
    }
    return res.status(404).json({ error: `Tool ${tool_name} not supported` });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
});

module.exports = router;
```

**Python FastAPI Example (`routes.py`):**
```python
# ai_integration/routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from security import get_authenticated_user
from ai_integration import tools

router = APIRouter(tags=["AI Integration"])

@router.post("/execute-tool")
async def execute_tool(payload: dict, current_user=Depends(get_authenticated_user)):
    tool_name = payload.get("tool_name")
    args = payload.get("arguments", {})
    user_context = {"user_id": current_user.id, "role": current_user.role}

    handler = getattr(tools, tool_name, None)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    result = await handler(user_context=user_context, **args)
    return result
```

---

## 4. Environment Variables Configuration

In `pydah-ai/.env`, configure the base service URLs for your application backends:

```env
# OpenRouter Config
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free

# Application Backend Service URLs (Where /execute-tool is dispatched)
STUDENT_SERVICE_URL=http://localhost:3001
FEE_SERVICE_URL=http://localhost:3002
TRANSPORT_SERVICE_URL=http://localhost:3003
```

---

## 5. Running & Verifying `pydah-ai`

### Start the Server:
```bash
python server.py
```

### Test Assistant API via Curl:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_VALID_AUTH_TOKEN" \
  -d '{
    "message": "What is my attendance percentage?",
    "assistant_id": "student-assistant"
  }'
```