from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.core.exceptions import NotFoundError
from app.core.interfaces import LLMRequest
from app.core.providers import (
    create_llm_provider,
    create_memory_provider,
    create_observability_service,
    create_session_store,
)
from app.core.security import hash_password
from app.db.database import get_db
from app.db.models import Assistant, ChatTurn, Device, User
from app.models.admin import (
    AdminOverview,
    AdminUserOut,
    AdminUserUpdate,
    ChatTurnOut,
    ProviderProbeRequest,
    ProviderProbeResponse,
)
from app.models.assistant import AssistantCreate, AssistantLLMUpdate, AssistantOut, AssistantPersonalityUpdate
from app.models.chat import ChatRequest, ChatResponse
from app.models.device import DeviceBindRequest, DeviceCreate, DeviceOut
from app.providers.personality_store import DbPersonalityStore
from app.services.chat_engine import ChatEngine
from app.services.device_service import DeviceService
from app.services.personality_service import PersonalityService
from app.services.prompt_builder import PromptBuilder

router = APIRouter()
device_service = DeviceService()
personality_service = PersonalityService()


def _is_global_admin(admin_key: str | None) -> bool:
    settings = get_settings()
    return bool(settings.admin_api_key and admin_key and admin_key == settings.admin_api_key)


def _require_global_admin(admin_key: str | None) -> None:
    if not _is_global_admin(admin_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Global admin key required")


def _build_chat_engine(db: AsyncSession) -> ChatEngine:
    return ChatEngine(
        llm_provider=create_llm_provider(),
        session_store=create_session_store(),
        prompt_builder=PromptBuilder(DbPersonalityStore(db), create_memory_provider()),
        device_service=device_service,
        observability=create_observability_service(),
    )


@router.get("/overview", response_model=AdminOverview)
async def overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> AdminOverview:
    global_admin = _is_global_admin(x_admin_key)
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    def scope(stmt, model):
        if global_admin:
            return stmt
        if model is User:
            return stmt.where(User.id == user.id)
        return stmt.where(model.user_id == user.id)

    users = (await db.execute(scope(select(func.count(User.id)), User))).scalar_one()
    assistants = (await db.execute(scope(select(func.count(Assistant.id)), Assistant))).scalar_one()
    devices = (await db.execute(scope(select(func.count(Device.id)), Device))).scalar_one()

    turns_stmt = select(func.count(ChatTurn.id)).where(ChatTurn.created_at >= since)
    err_stmt = select(func.count(ChatTurn.id)).where(ChatTurn.created_at >= since, ChatTurn.status != "ok")
    if not global_admin:
        turns_stmt = turns_stmt.where(ChatTurn.user_id == user.id)
        err_stmt = err_stmt.where(ChatTurn.user_id == user.id)
    turns_24h = (await db.execute(turns_stmt)).scalar_one()
    errors_24h = (await db.execute(err_stmt)).scalar_one()

    runtime = await create_observability_service().snapshot()
    return AdminOverview(
        users=int(users or 0),
        assistants=int(assistants or 0),
        devices=int(devices or 0),
        chat_turns_24h=int(turns_24h or 0),
        errors_24h=int(errors_24h or 0),
        runtime=runtime,
    )


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> list[AdminUserOut]:
    _require_global_admin(x_admin_key)
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    users = (await db.execute(select(User).order_by(User.created_at.desc()))).scalars().all()
    if not users:
        return []

    assistant_counts = {
        user_id: count
        for user_id, count in (
            await db.execute(select(Assistant.user_id, func.count(Assistant.id)).group_by(Assistant.user_id))
        ).all()
    }
    device_counts = {
        user_id: count
        for user_id, count in (
            await db.execute(select(Device.user_id, func.count(Device.id)).group_by(Device.user_id))
        ).all()
    }
    turn_counts_24h = {
        user_id: count
        for user_id, count in (
            await db.execute(
                select(ChatTurn.user_id, func.count(ChatTurn.id))
                .where(ChatTurn.created_at >= since)
                .group_by(ChatTurn.user_id)
            )
        ).all()
    }
    last_seen_by_user = {
        user_id: last_seen
        for user_id, last_seen in (
            await db.execute(select(Device.user_id, func.max(Device.last_seen)).group_by(Device.user_id))
        ).all()
    }

    return [
        AdminUserOut(
            id=item.id,
            email=item.email,
            plan=item.plan,
            assistants=int(assistant_counts.get(item.id, 0) or 0),
            devices=int(device_counts.get(item.id, 0) or 0),
            chat_turns_24h=int(turn_counts_24h.get(item.id, 0) or 0),
            created_at=item.created_at,
            last_seen=last_seen_by_user.get(item.id),
        )
        for item in users
    ]


@router.patch("/users/{user_id}", response_model=AdminUserOut)
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> AdminUserOut:
    _require_global_admin(x_admin_key)

    user_row = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.plan is not None:
        user_row.plan = payload.plan.strip()
    if payload.password is not None:
        user_row.hashed_password = hash_password(payload.password)

    await db.commit()
    await db.refresh(user_row)

    assistants = (
        await db.execute(select(func.count(Assistant.id)).where(Assistant.user_id == user_row.id))
    ).scalar_one()
    devices = (await db.execute(select(func.count(Device.id)).where(Device.user_id == user_row.id))).scalar_one()
    turns_24h = (
        await db.execute(
            select(func.count(ChatTurn.id)).where(
                ChatTurn.user_id == user_row.id,
                ChatTurn.created_at >= (datetime.now(timezone.utc) - timedelta(hours=24)),
            )
        )
    ).scalar_one()
    last_seen = (await db.execute(select(func.max(Device.last_seen)).where(Device.user_id == user_row.id))).scalar_one()

    return AdminUserOut(
        id=user_row.id,
        email=user_row.email,
        plan=user_row.plan,
        assistants=int(assistants or 0),
        devices=int(devices or 0),
        chat_turns_24h=int(turns_24h or 0),
        created_at=user_row.created_at,
        last_seen=last_seen,
    )


@router.post("/users/{user_id}/assistants", response_model=AssistantOut, status_code=status.HTTP_201_CREATED)
async def create_assistant_for_user(
    user_id: UUID,
    payload: AssistantCreate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> AssistantOut:
    _require_global_admin(x_admin_key)

    user_row = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    assistant = await personality_service.create_assistant(
        db,
        user_id=user_row.id,
        name=payload.name,
        personality=payload.personality,
        llm_backend=payload.llm_backend,
        llm_model=payload.llm_model,
        llm_overrides=payload.llm_overrides,
    )
    return AssistantOut.model_validate(assistant)


@router.post("/users/{user_id}/devices", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
async def create_device_for_user(
    user_id: UUID,
    payload: DeviceCreate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> DeviceOut:
    _require_global_admin(x_admin_key)

    user_row = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    device = await device_service.create_device(db, user_row.id, payload.name)
    return DeviceOut.model_validate(device)


@router.get("/chat-turns", response_model=list[ChatTurnOut])
async def list_chat_turns(
    limit: int = Query(default=50, ge=1, le=500),
    status_filter: str | None = Query(default=None, alias="status"),
    user_id: UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> list[ChatTurnOut]:
    global_admin = _is_global_admin(x_admin_key)

    stmt = select(ChatTurn).order_by(ChatTurn.created_at.desc()).limit(limit)
    if global_admin:
        if user_id is not None:
            stmt = stmt.where(ChatTurn.user_id == user_id)
    else:
        stmt = stmt.where(ChatTurn.user_id == user.id)

    if status_filter:
        stmt = stmt.where(ChatTurn.status == status_filter)

    result = await db.execute(stmt)
    turns = result.scalars().all()
    return [ChatTurnOut.model_validate(item) for item in turns]


@router.get("/assistants/llm", response_model=list[AssistantOut])
async def list_assistant_llm(
    user_id: UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> list[AssistantOut]:
    global_admin = _is_global_admin(x_admin_key)

    stmt = select(Assistant).order_by(Assistant.created_at.desc())
    if global_admin:
        if user_id is not None:
            stmt = stmt.where(Assistant.user_id == user_id)
    else:
        stmt = stmt.where(Assistant.user_id == user.id)

    result = await db.execute(stmt)
    assistants = result.scalars().all()
    return [AssistantOut.model_validate(item) for item in assistants]


@router.put("/assistants/{assistant_id}/llm", response_model=AssistantOut)
async def update_assistant_llm(
    assistant_id: UUID,
    payload: AssistantLLMUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> AssistantOut:
    if _is_global_admin(x_admin_key):
        assistant = (await db.execute(select(Assistant).where(Assistant.id == assistant_id))).scalar_one_or_none()
        if assistant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        assistant = await personality_service.update_llm_settings(
            db=db,
            user_id=assistant.user_id,
            assistant_id=assistant_id,
            llm_backend=payload.llm_backend,
            llm_model=payload.llm_model,
            llm_overrides=payload.llm_overrides,
        )
        return AssistantOut.model_validate(assistant)

    try:
        assistant = await personality_service.update_llm_settings(
            db=db,
            user_id=user.id,
            assistant_id=assistant_id,
            llm_backend=payload.llm_backend,
            llm_model=payload.llm_model,
            llm_overrides=payload.llm_overrides,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AssistantOut.model_validate(assistant)


@router.put("/assistants/{assistant_id}/personality", response_model=AssistantOut)
async def update_assistant_personality(
    assistant_id: UUID,
    payload: AssistantPersonalityUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> AssistantOut:
    if _is_global_admin(x_admin_key):
        assistant = (await db.execute(select(Assistant).where(Assistant.id == assistant_id))).scalar_one_or_none()
        if assistant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        assistant = await personality_service.update_personality(
            db=db,
            user_id=assistant.user_id,
            assistant_id=assistant_id,
            personality=payload.personality,
        )
        return AssistantOut.model_validate(assistant)

    try:
        assistant = await personality_service.update_personality(
            db=db,
            user_id=user.id,
            assistant_id=assistant_id,
            personality=payload.personality,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AssistantOut.model_validate(assistant)


@router.get("/devices", response_model=list[DeviceOut])
async def list_devices_admin(
    user_id: UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> list[DeviceOut]:
    global_admin = _is_global_admin(x_admin_key)

    stmt = select(Device).order_by(Device.created_at.desc())
    if global_admin:
        if user_id is not None:
            stmt = stmt.where(Device.user_id == user_id)
    else:
        stmt = stmt.where(Device.user_id == user.id)

    devices = (await db.execute(stmt)).scalars().all()
    return [DeviceOut.model_validate(item) for item in devices]


@router.put("/devices/{device_id}/assistant", response_model=DeviceOut)
async def bind_device_assistant_admin(
    device_id: UUID,
    payload: DeviceBindRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> DeviceOut:
    try:
        assistant_id = UUID(payload.assistant_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid assistant_id") from exc

    if _is_global_admin(x_admin_key):
        device = (await db.execute(select(Device).where(Device.id == device_id))).scalar_one_or_none()
        if device is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

        assistant = (await db.execute(select(Assistant).where(Assistant.id == assistant_id))).scalar_one_or_none()
        if assistant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        if assistant.user_id != device.user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assistant belongs to another user")

        device.assistant_id = assistant_id
        await db.commit()
        await db.refresh(device)
        return DeviceOut.model_validate(device)

    try:
        device = await device_service.bind_assistant(db, user.id, device_id, assistant_id)
    except (NotFoundError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DeviceOut.model_validate(device)


@router.get("/devices/{device_id}/session")
async def debug_device_session(
    device_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> dict:
    if _is_global_admin(x_admin_key):
        device = (await db.execute(select(Device).where(Device.id == device_id))).scalar_one_or_none()
        if device is None or device.assistant_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device or assistant not found")
        context = await create_session_store().get_context(str(device.assistant_id), str(device.user_id))
        return {
            "device_id": str(device.id),
            "assistant_id": str(device.assistant_id),
            "user_id": str(device.user_id),
            "messages": list(reversed(context)),
        }

    device = await device_service.get_device_with_assistant(db, device_id, user.id)
    context = await create_session_store().get_context(str(device.assistant_id), str(user.id))
    return {
        "device_id": str(device.id),
        "assistant_id": str(device.assistant_id),
        "messages": list(reversed(context)),
    }


@router.post("/providers/probe", response_model=ProviderProbeResponse)
async def provider_probe(
    payload: ProviderProbeRequest,
    _: User = Depends(get_current_user),
) -> ProviderProbeResponse:
    provider = create_llm_provider()
    response = await provider.complete(
        LLMRequest(
            messages=[{"role": "user", "content": payload.prompt}],
            model=payload.model,
            metadata={"llm_backend": payload.backend, "llm_model": payload.model, **payload.llm_overrides},
        )
    )
    return ProviderProbeResponse(
        backend=payload.backend,
        provider=response.provider,
        model=response.model,
        text=response.content,
        latency_ms=response.latency_ms,
        usage=response.usage,
    )


@router.post("/test-chat/{device_id}", response_model=ChatResponse)
async def test_chat(
    device_id: UUID,
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_admin_key: str | None = Header(default=None),
) -> ChatResponse:
    user_id = user.id
    if _is_global_admin(x_admin_key):
        device = (await db.execute(select(Device).where(Device.id == device_id))).scalar_one_or_none()
        if device is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        user_id = device.user_id

    try:
        text, session_id, provider, model, latency_ms = await _build_chat_engine(db).chat(
            db,
            user_id,
            device_id,
            payload.text,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ChatResponse(text=text, session_id=session_id, provider=provider, model=model, latency_ms=latency_ms)
