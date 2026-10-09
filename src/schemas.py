from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single chat message in history."""
    role: str = Field(..., description="Role of message sender: system, user, or assistant")
    content: str = Field(..., description="Text content of the message")


class ChatRequest(BaseModel):
    """Schema for incoming chat completion request."""
    message: str = Field(..., min_length=1, description="The user's latest query or prompt")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation context identifier")
    history: Optional[List[Message]] = Field(default_factory=list, description="Prior conversation message history")
    system_prompt: Optional[str] = Field(default=None, description="Optional custom system behavior override")


class ChatResponse(BaseModel):
    """Schema for successful chat completion response."""
    success: bool = Field(default=True, description="Request execution status")
    answer: str = Field(..., description="Assistant's generated answer")
    model: str = Field(..., description="Model used to generate response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation identifier")


class ErrorResponse(BaseModel):
    """Schema for API error responses."""
    success: bool = Field(default=False, description="Request execution status")
    error: str = Field(..., description="High-level error summary")
    details: Optional[str] = Field(default=None, description="Safe additional error diagnostic details")
