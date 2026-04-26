"""Tests for guided TUI stop-at-ii-4 behavior."""

from mcgg.cli import (
    _get_guided_history_records,
    _get_next_predicted_sequence,
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

    # ii-1, ii-2, ii-4
    session.current_phase, session.current_round = 2, 1
    session.add_round(dina, RoundType.USER)
    session.current_phase, session.current_round = 2, 2
    session.add_round(alice, RoundType.USER)
    session.current_phase, session.current_round = 2, 4
    session.add_round(bob, RoundType.USER)

    # Chain data required for ii-5 and ii-6 predictions.
    session.set_chain_relation(2, 2, "Bob", "Charlie")   # ii-5 predicted Charlie
    session.set_chain_relation(2, 3, "Charlie", "Dina")  # ii-6 predicted Dina
    return session


def test_guided_flow_end_marker_only_ii4():
    assert _is_guided_flow_end(RoundNumber.P2_R4)
    assert not _is_guided_flow_end(RoundNumber.P2_R5)
    assert not _is_guided_flow_end(RoundNumber.P1_R4)


def test_guided_history_records_include_expected_rounds():
    session = _build_session_for_guided_summary()
    history = _get_guided_history_records(session)

    assert history == [
        ("i-2", "Alice"),
        ("i-3", "Bob"),
        ("i-4", "Charlie"),
        ("ii-1", "Dina"),
        ("ii-2", "Alice"),
        ("ii-4", "Bob"),
    ]


def test_next_predicted_sequence_uses_engine_rules():
    session = _build_session_for_guided_summary()
    session.current_phase = 2
    session.current_round = 5

    predictions = _get_next_predicted_sequence(session)

    assert predictions == [("ii-5", "Charlie"), ("ii-6", "Dina")]
