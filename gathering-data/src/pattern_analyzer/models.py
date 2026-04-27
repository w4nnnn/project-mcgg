"""Domain models and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class SessionState:
    """Session persisted to JSON."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    players: list[str] = field(default_factory=list)
    phase: int = 1
    round_no: int = 2
    matches: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: str | None = None
    is_finished: bool = False
    report: dict[str, Any] | None = None

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()


def parse_pair(pair_text: str) -> tuple[str, str]:
    """Parse A:C style pair."""
    if ":" not in pair_text:
        raise ValueError(f"Format pair tidak valid: '{pair_text}'. Gunakan 'A:B'.")
    left, right = pair_text.split(":", 1)
    p1 = left.strip()
    p2 = right.strip()
    if not p1 or not p2:
        raise ValueError(f"Pair tidak lengkap: '{pair_text}'.")
    if p1.lower() == p2.lower():
        raise ValueError(f"Pair tidak boleh pemain yang sama: '{pair_text}'.")
    return p1, p2


def normalize_players(players: list[str]) -> list[str]:
    """Trim and validate unique players."""
    normalized = [p.strip() for p in players if p.strip()]
    if len(normalized) != 8:
        raise ValueError("Jumlah pemain harus tepat 8 nama unik.")

    seen: set[str] = set()
    for p in normalized:
        key = p.lower()
        if key in seen:
            raise ValueError(f"Nama pemain duplikat: {p}")
        seen.add(key)
    return normalized


def validate_round_pairs(players: list[str], raw_pairs: list[str]) -> list[tuple[str, str]]:
    """Validate 4 pairs include all 8 players exactly once."""
    if len(raw_pairs) != 4:
        raise ValueError("Setiap ronde player harus berisi tepat 4 pairing.")

    normalized_players = {p.lower(): p for p in players}
    used: set[str] = set()
    pairs: list[tuple[str, str]] = []

    for raw in raw_pairs:
        p1, p2 = parse_pair(raw)
        k1 = p1.lower()
        k2 = p2.lower()
        if k1 not in normalized_players or k2 not in normalized_players:
            raise ValueError(f"Nama pemain tidak terdaftar di sesi: '{raw}'")
        if k1 in used or k2 in used:
            raise ValueError(f"Pemain tidak boleh muncul lebih dari sekali: '{raw}'")
        used.add(k1)
        used.add(k2)
        pairs.append((normalized_players[k1], normalized_players[k2]))

    if len(used) != 8:
        raise ValueError("Tidak semua pemain tercatat di ronde ini.")
    return pairs

