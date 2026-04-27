"""JSON persistence for gathering sessions."""

from __future__ import annotations

from pathlib import Path
from dataclasses import asdict
from datetime import datetime, timezone
import json

from pattern_analyzer.models import SessionState


class SessionStore:
    """Store sessions as JSON files."""

    def __init__(self, data_dir: Path | None = None) -> None:
        base = data_dir or (Path(__file__).resolve().parents[2] / "data")
        self.base_dir = base
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def session_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def save(self, session: SessionState) -> Path:
        session.touch()
        path = self.session_path(session.id)
        path.write_text(json.dumps(asdict(session), indent=2), encoding="utf-8")
        return path

    def load(self, session_id: str) -> SessionState:
        path = self.session_path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"Sesi '{session_id}' tidak ditemukan.")
        raw = json.loads(path.read_text(encoding="utf-8"))
        return SessionState(**raw)

    def list_sessions(self) -> list[dict]:
        items: list[dict] = []
        for path in sorted(self.sessions_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append(
                {
                    "id": data["id"],
                    "updated_at": data.get("updated_at"),
                    "is_finished": data.get("is_finished", False),
                    "phase": data.get("phase"),
                    "round_no": data.get("round_no"),
                }
            )
        return items

    def latest_session_id(self) -> str | None:
        sessions = self.list_sessions()
        if not sessions:
            return None
        sessions.sort(
            key=lambda item: datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            if item["updated_at"]
            else datetime.min.replace(tzinfo=timezone.utc)
        )
        return sessions[-1]["id"]

