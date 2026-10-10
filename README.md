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

---

## 📋 Checklist for Application Developers: What Your Application Backend Must Handle

When connecting your application backend (Student Portal, Fee, Transport, HRMS) to `pydah-ai`, make sure your backend handles the following 6 requirements:

### 1. Expose the `/execute-tool` Route
- Register a `POST` route at `/execute-tool` (or `/api/v1/execute-tool` or `/ai_integration/execute-tool`).
- `pydah-ai` sends a `POST` request to this endpoint whenever the LLM requests data from your application.

### 2. Handle Flexible Authentication Extraction
- Extract the user's Bearer token flexibly. `pydah-ai` sends the token in:
  - Header: `Authorization: Bearer <token>`
  - Header: `x-access-token` / `x-user-token`
  - Body: `req.body.token` or `req.body.user_context.delegated_access_token`
- Verify the token using your application's existing JWT / Session authentication middleware.

### 3. Support Tool Name Aliases & String Normalization
- The LLM might generate tool function names with slight variations (e.g. `get_my_student_profile`, `get_student_profile`, `get_profile`, `fetch_student_profile`).
- Map these function name variations to your tool execution handler (e.g. normalize string case and hyphens).

### 4. Authenticate & Scope Record Permissions (Record Security)
- Decode the student/user ID from the verified Bearer token.
- Ensure students can **only access their own data** (record-level permission check).
- Never allow unauthenticated queries or arbitrary student IDs without permission verification.

### 5. Reuse Existing Application Services
- Do **NOT** rewrite database queries or calculation logic.
- Call your existing controllers/services (e.g. `StudentService.getProfile(studentId)` or `FeeService.getPendingDues(studentId)`).

### 6. Return Clean JSON Data
- Return structured JSON (e.g. `{ "full_name": "...", "roll_number": "...", "attendance": 87.5 }`).
- If no record is found, return a clear JSON response `{ "error": "No records found" }` with HTTP 200 or 404 instead of returning HTML error pages.

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

---

## 3. Integration Guide for Other Application Teams

To connect an existing application to the central AI system, add an `ai_integration/` folder inside your backend codebase:

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

### Implementation Code Examples for Application Teams

#### Node.js Express Example (`ai_integration/routes.js` & `tools.js`):

```javascript
// ai_integration/routes.js
const express = require('express');
const router = express.Router();
const { authenticateUser } = require('../middleware/auth');
const tools = require('./tools');

router.post('/execute-tool', authenticateUser, async (req, res) => {
  const toolName = (req.body.tool_name || req.body.function_name || '').toLowerCase();
  const args = req.body.arguments || {};
  const userContext = { userId: req.user.id, role: req.user.role };

  try {
    // Map tool aliases to tools handler
    const handler = tools[toolName] || tools.resolveAlias(toolName);
    if (typeof handler === 'function') {
      const data = await handler(userContext, args);
      return res.json(data);
    }
    return res.status(404).json({ error: `Tool '${toolName}' not found in application` });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
});

module.exports = router;
```

#### Python FastAPI Example (`ai_integration/routes.py` & `tools.py`):

```python
# ai_integration/routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from security import get_authenticated_user
from ai_integration import tools

router = APIRouter(tags=["AI Integration"])

@router.post("/execute-tool")
async def execute_tool(payload: dict, current_user=Depends(get_authenticated_user)):
    tool_name = payload.get("tool_name", "").lower()
    args = payload.get("arguments", {})
    user_context = {"user_id": current_user.id, "role": current_user.role}

    handler = getattr(tools, tool_name, None) or tools.resolve_alias(tool_name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    result = await handler(user_context=user_context, **args)
    return result
```

---

## 4. Environment Variables Configuration

In `pydah-ai/.env`, configure the base service URLs for your application backends:

```env
# Server Configuration
PORT=8000
REQUEST_TIMEOUT_SECONDS=30
MAX_HISTORY_MESSAGES=10

# Application Backend Service Base URLs (Where /execute-tool is dispatched)
STUDENT_SERVICE_URL=http://localhost:3001
FEE_SERVICE_URL=http://localhost:3002
TRANSPORT_SERVICE_URL=http://localhost:3003
```