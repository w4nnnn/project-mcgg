"""Tests for guided TUI stop-at-ii-2 behavior."""

from mcgg.cli import (
    _get_opponent_sequence_until_ii4,
    _predict_ii4_for_summary,
    _is_guided_flow_end,
)
from mcgg.models import Player, RoundType, RoundNumber, Session


def _build_session_for_guided_summary() -> Session:
    session = Session()
    players = [
        Player(name="Kamu", position=1, is_local_player=True),
        Player(name="Alice", position=2),
        Player(name="Bob", position=3),
        Player(name="Charlie", position=4),
        Player(name="Dina", position=5),
    ]
    for player in players:
        session.add_player(player)

    alice = session.get_player_by_name("Alice")
    bob = session.get_player_by_name("Bob")
    charlie = session.get_player_by_name("Charlie")
    dina = session.get_player_by_name("Dina")
    assert alice and bob and charlie and dina

    # i-2, i-3, i-4
    session.current_phase, session.current_round = 1, 2
    session.add_round(alice, RoundType.USER)
    session.current_phase, session.current_round = 1, 3
    session.add_round(bob, RoundType.USER)
    session.current_phase, session.current_round = 1, 4
    session.add_round(charlie, RoundType.USER)

    # ii-1, ii-2
    session.current_phase, session.current_round = 2, 1
    session.add_round(dina, RoundType.USER)
    session.current_phase, session.current_round = 2, 2
    session.add_round(alice, RoundType.USER)

    # Chain data required for ii-4 prediction:
    # ii-2 opponent is Alice, and at i-4 Alice faced Bob.
    session.set_chain_relation(1, 4, "Alice", "Bob")
    return session


def test_guided_flow_end_marker_only_ii2():
    assert _is_guided_flow_end(RoundNumber.P2_R2)
    assert not _is_guided_flow_end(RoundNumber.P2_R4)
    assert not _is_guided_flow_end(RoundNumber.P1_R4)


def test_opponent_sequence_until_ii4_includes_predicted_ii4():
    session = _build_session_for_guided_summary()
    history = _get_opponent_sequence_until_ii4(session)

    assert history == [
        ("i-2", "Alice"),
        ("i-3", "Bob"),
        ("i-4", "Charlie"),
        ("ii-1", "Dina"),
        ("ii-2", "Alice"),
        ("ii-4 (predict)", "Bob"),
    ]


def test_predict_ii4_for_summary_uses_engine_rule():
    session = _build_session_for_guided_summary()
    session.current_phase = 2
    session.current_round = 3

    predicted = _predict_ii4_for_summary(session)

    assert predicted == "Bob"
