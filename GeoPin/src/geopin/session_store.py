from __future__ import annotations

import secrets
from pathlib import Path

from .models import SessionData


class SessionStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, session: SessionData) -> str:
        session_id = secrets.token_urlsafe(8)
        path = self.root / f"{session_id}.json"
        path.write_text(session.model_dump_json(indent=2), encoding="utf-8")
        return session_id

    def read(self, session_id: str) -> SessionData:
        path = self.root / f"{session_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Unknown session_id: {session_id}")
        return SessionData.model_validate_json(path.read_text(encoding="utf-8"))
