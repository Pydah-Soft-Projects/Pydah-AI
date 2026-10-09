from typing import List, Dict
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import Config, ConfigError
from src.llm_client import LLMClient, LLMError
from src.schemas import ChatRequest, ChatResponse, ErrorResponse
from src.console import DEFAULT_SYSTEM_PROMPT

app = FastAPI(
    title="AI Core Service API",
    description="Centralized AI engine API providing unified LLM integrations.",
    version="1.0.0"
)

# Enable CORS for frontend clients (React/Next.js/Dashboard apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_llm_client() -> LLMClient:
    """Initialize configuration and LLM client lazily for requests."""
    config = Config.load()
    return LLMClient(config)


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
        "service": "ai-core-service-api"
    }


@app.post(
    "/api/v1/chat",
    tags=["Chat Completions"],
    summary="Generate Chat Response",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or configuration"},
        401: {"model": ErrorResponse, "description": "Authentication failure"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error or LLM failure"},
    }
)
def chat_completion(request: ChatRequest):
    """
    Accept user question and conversation context, process via OpenRouter LLM, 
    and return normalized assistant response.
    """
    try:
        config = Config.load()
        client = LLMClient(config)

        # 1. System Prompt
        system_text = request.system_prompt or DEFAULT_SYSTEM_PROMPT
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_text}]

        # 2. Add client-supplied history
        if request.history:
            for item in request.history:
                if item.role in ("user", "assistant", "system"):
                    messages.append({"role": item.role, "content": item.content})

        # 3. Append latest user query
        messages.append({"role": "user", "content": request.message})

        # 4. History size truncation
        system_msg = messages[0]
        conversation = messages[1:]
        if len(conversation) > config.max_history_messages:
            conversation = conversation[-config.max_history_messages:]
        final_messages = [system_msg] + conversation

        # 5. Call LLM Client
        answer = client.generate_response(final_messages)

        return ChatResponse(
            success=True,
            answer=answer,
            model=config.model,
            conversation_id=request.conversation_id
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
