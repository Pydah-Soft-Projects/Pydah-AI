from typing import List, Dict
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import Config, ConfigError
from src.llm_client import LLMClient, LLMError
from src.schemas import ChatRequest, ChatResponse, ErrorResponse
from src.security.auth import get_user_context
from src.services.llm_service import run_assistant_chat
from src.assistants.config import ASSISTANTS_CONFIG

app = FastAPI(
    title="Pydah AI Core Engine API",
    description="Centralized multi-assistant AI engine with tool-calling capabilities.",
    version="1.1.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Check API Health Status",
    response_model=Dict[str, str]
)
def health_check():
    """Health check endpoint to verify backend service status."""
    return {
        "status": "healthy",
        "service": "pydah-ai-core-engine"
    }


@app.get(
    "/api/v1/assistants",
    tags=["Assistants"],
    summary="List Registered Assistants",
)
def list_assistants():
    """Returns available assistant personas and descriptions."""
    return {
        "assistants": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "allowed_tools": a.allowed_tools
            }
            for a in ASSISTANTS_CONFIG.values()
        ]
    }


@app.post(
    "/api/v1/chat",
    tags=["Chat Completions"],
    summary="Generate Assistant Response with Tool Calling",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or configuration"},
        401: {"model": ErrorResponse, "description": "Authentication failure"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error or LLM failure"},
    }
)
def chat_completion(chat_req: ChatRequest, request: Request):
    """
    Accept user question, assistant_id, and conversation context.
    Extracts security token context, executes permitted tool calls, and returns answer.
    """
    try:
        config = Config.load()
        client = LLMClient(config)
        user_context = get_user_context(request=request, payload=chat_req)

        answer, executed_tools, assistant_id = run_assistant_chat(
            payload=chat_req,
            user_context=user_context,
            config=config,
            client=client
        )

        return ChatResponse(
            success=True,
            answer=answer,
            model=config.model,
            assistant_id=assistant_id,
            conversation_id=chat_req.conversation_id,
            executed_tools=executed_tools
        )

    except ConfigError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error="Configuration Error",
                details=str(e)
            ).model_dump()
        )

    except LLMError as e:
        err_msg = str(e)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if "Authentication failed" in err_msg or "HTTP 401" in err_msg:
            status_code = status.HTTP_401_UNAUTHORIZED
        elif "Rate limit" in err_msg or "HTTP 429" in err_msg:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        elif "Bad request" in err_msg:
            status_code = status.HTTP_400_BAD_REQUEST

        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                success=False,
                error="LLM Provider Error",
                details=err_msg
            ).model_dump()
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error="Internal Server Error",
                details=str(e)
            ).model_dump()
        )
