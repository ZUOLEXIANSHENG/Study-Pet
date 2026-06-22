from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.core.settings import get_settings


class Base(DeclarativeBase):
    pass


class AppEvent(Base):
    __tablename__ = "app_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="demo")
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(64), default="api")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


engine = create_engine(
    get_settings().database_url,
    connect_args={"check_same_thread": False} if get_settings().database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
_initialized = False


def init_db() -> None:
    global _initialized
    Base.metadata.create_all(bind=engine)
    _initialized = True


def record_event(
    *,
    event_type: str,
    user_id: str = "demo",
    source: str = "api",
    payload: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
) -> AppEvent:
    if not _initialized:
        init_db()
    with SessionLocal() as session:
        event = AppEvent(
            user_id=user_id,
            event_type=event_type,
            source=source,
            payload_json=json.dumps(payload or {}, ensure_ascii=False, default=str),
            result_json=json.dumps(result or {}, ensure_ascii=False, default=str),
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return event


def list_events(user_id: str = "demo", limit: int = 50) -> list[dict[str, Any]]:
    if not _initialized:
        init_db()
    with SessionLocal() as session:
        statement = (
            select(AppEvent)
            .where(AppEvent.user_id == user_id)
            .order_by(AppEvent.created_at.desc())
            .limit(min(max(limit, 1), 200))
        )
        rows = session.execute(statement).scalars().all()
        return [_event_to_dict(row) for row in rows]


def _event_to_dict(event: AppEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "user_id": event.user_id,
        "event_type": event.event_type,
        "source": event.source,
        "payload": json.loads(event.payload_json or "{}"),
        "result": json.loads(event.result_json or "{}"),
        "created_at": event.created_at.isoformat(),
    }
