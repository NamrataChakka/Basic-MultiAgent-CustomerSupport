from typing import Dict, Any, List
from pydantic import BaseModel


class SessionState(BaseModel):
    session_id: str
    history: List[Dict[str, str]] = []
    context: Dict[str, Any] = {}
    last_agent: str | None = None
    updated_at: str | None = None
