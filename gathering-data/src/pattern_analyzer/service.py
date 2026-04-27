"""Business logic for TUI flow and persistence."""

from __future__ import annotations

from datetime import datetime, timezone

from pattern_analyzer.analysis import build_report
from pattern_analyzer.models import SessionState, normalize_players, validate_round_pairs
from pattern_analyzer.rounds import is_monster_round, next_round, next_player_round, round_label
from pattern_analyzer.storage import SessionStore


class SessionService:
    """Service layer to keep CLI simple."""

    def __init__(self, store: SessionStore) -> None:
        self.store = store

    def create_session(self, players: list[str]) -> SessionState:
        normalized = normalize_players(players)
        session = SessionState(players=normalized)
        session.phase, session.round_no = next_player_round(1, 1)
        self.store.save(session)
        return session

    def load_session(self, session_id: str) -> SessionState:
        return self.store.load(session_id)

    def save_round_pairs(self, session: SessionState, pairs: list[str]) -> SessionState:
        valid_pairs = validate_round_pairs(session.players, pairs)
        label = round_label(session.phase, session.round_no)
        now = datetime.now(timezone.utc).isoformat()
        for p1, p2 in valid_pairs:
            session.matches.append(
                {
                    "round_label": label,
                    "phase": session.phase,
                    "round_no": session.round_no,
                    "player1": p1,
                    "player2": p2,
                    "recorded_at": now,
                }
            )
        phase, rnd = next_round(session.phase, session.round_no)
        phase, rnd = next_player_round(phase, rnd)
        session.phase = phase
        session.round_no = rnd
        self.store.save(session)
        return session

    def skip_monsters_until_player_round(self, session: SessionState) -> SessionState:
        if is_monster_round(session.phase, session.round_no):
            session.phase, session.round_no = next_player_round(session.phase, session.round_no)
            self.store.save(session)
        return session

    def finish_session(self, session: SessionState) -> SessionState:
        session.is_finished = True
        session.ended_at = datetime.now(timezone.utc).isoformat()
        session.report = build_report(session)
        self.store.save(session)
        return session

