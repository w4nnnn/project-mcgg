"""JSON persistence for simplified gathering-data sessions."""

from __future__ import annotations

from pathlib import Path
import json


class SessionStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        base = data_dir or (Path(__file__).resolve().parents[2] / "data")
        self.base_dir = Path(base)
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def session_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def save(self, payload: dict) -> Path:
        path = self.session_path(payload["id"])
        data = {
            "id": payload["id"],
            "players": payload.get("players", []),
            "matches": payload.get("matches", []),
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self, session_id: str) -> dict:
        path = self.session_path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"Sesi '{session_id}' tidak ditemukan.")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_sessions(self) -> list[str]:
        return sorted([p.stem for p in self.sessions_dir.glob("*.json")])

    def delete(self, session_id: str) -> None:
        path = self.session_path(session_id)
        if path.exists():
            path.unlink()
