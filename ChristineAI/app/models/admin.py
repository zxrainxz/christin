from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AdminOverview(BaseModel):
    users: int
    assistants: int
    devices: int
    chat_turns_24h: int
    errors_24h: int
    runtime: dict


class ProviderProbeRequest(BaseModel):
    backend: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=128)
    prompt: str = Field(min_length=1, max_length=2000)
    llm_overrides: dict = Field(default_factory=dict)


class ProviderProbeResponse(BaseModel):
    backend: str
    provider: str
    model: str
    text: str
    latency_ms: int | None
    usage: dict


class ChatTurnOut(BaseModel):
    id: UUID
    user_id: UUID
    assistant_id: UUID | None
    device_id: UUID | None
    request_text: str
    response_text: str | None
    provider: str
    model: str
    status: str
    latency_ms: int | None
    error: str | None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    meta: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserOut(BaseModel):
    id: UUID
    email: EmailStr
    plan: str
    assistants: int
    devices: int
    chat_turns_24h: int
    created_at: datetime
    last_seen: datetime | None


class AdminUserUpdate(BaseModel):
    plan: str | None = Field(default=None, min_length=1, max_length=32)
    password: str | None = Field(default=None, min_length=8, max_length=128)
