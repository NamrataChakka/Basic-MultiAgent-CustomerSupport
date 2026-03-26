import json
from datetime import datetime
from app.services.redis_client import redis_client
from typing import Dict, Any, List
from pydantic import BaseModel


class SessionState(BaseModel):
    session_id: str
    history: List[Dict[str, str]] = []
    context: Dict[str, Any] = {}
    last_agent: str | None = None
    updated_at: str | None = None


# Persist session info for 24 hours
SESSION_TTL_SECONDS = 60 * 60 * 24  # 24 hours


def _session_key(session_id: str) -> str:
    return f"session:{session_id}"


def get_session(session_id: str) -> SessionState:
    raw = redis_client.get(_session_key(session_id))

    if raw is None:
        return SessionState(session_id=session_id)

    data = json.loads(raw)
    return SessionState(**data)


def save_session(state: SessionState) -> None:
    state.updated_at = datetime.now().isoformat()

    redis_client.setex(
        _session_key(state.session_id),
        SESSION_TTL_SECONDS,
        json.dumps(state.model_dump())
    )
