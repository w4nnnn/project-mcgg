from pattern_analyzer.models import (
    build_round_matches,
    normalize_players,
    round_key,
    suggest_next_round,
    upsert_round_matches,
)


def test_normalize_players_accepts_2_to_8_unique_names():
    assert normalize_players(["A", "B"]) == ["A", "B"]
    assert normalize_players(["A", "B", "C", "D", "E", "F", "G", "H"]) == ["A", "B", "C", "D", "E", "F", "G", "H"]


def test_normalize_players_rejects_duplicates_and_too_few():
    try:
        normalize_players(["A", "a"])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "duplikat" in str(exc).lower()

    try:
        normalize_players(["A"])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "minimal" in str(exc).lower()


def test_build_round_matches_validates_duplicate_pair_and_player_reuse():
    players = ["A", "B", "C", "D", "E", "F", "G", "H"]

    try:
        build_round_matches(players, "i-2", 1, 2, [("A", "B"), ("B", "C")])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "lebih dari sekali" in str(exc).lower()

    try:
        build_round_matches(players, "i-2", 1, 2, [("A", "B"), ("B", "A")])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "duplikat" in str(exc).lower()


def test_build_round_matches_supports_partial_and_mirror():
    players = ["A", "B", "C", "D", "E", "F", "G", "H"]
    matches = build_round_matches(
        players,
        "i-2",
        1,
        2,
        [("A", "B"), ("C", "D"), ("E", "MIRROR"), ("", "")],
    )
    assert len(matches) == 3
    assert matches[2]["player1"] == "E"
    assert matches[2]["player2"] == "MIRROR"


def test_build_round_matches_rejects_multiple_mirror():
    players = ["A", "B", "C", "D", "E", "F", "G", "H"]
    try:
        build_round_matches(players, "i-2", 1, 2, [("A", "MIRROR"), ("B", "MIRROR")])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "maksimal 1" in str(exc).lower()


def test_upsert_round_matches_replaces_same_round_key_only():
    existing = [
        {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "A", "player2": "B"},
        {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "C", "player2": "D"},
        {"round_label": "i-3", "phase": 1, "round_no": 3, "player1": "A", "player2": "C"},
    ]
    replacement = [
        {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "A", "player2": "C"},
        {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "B", "player2": "D"},
    ]

    merged = upsert_round_matches(existing, replacement)
    assert len(merged) == 3
    assert sum(1 for m in merged if round_key(m) == ("i-2", 1, 2)) == 2
    assert sum(1 for m in merged if round_key(m) == ("i-3", 1, 3)) == 1


def test_suggest_next_round_increments_round_number_and_default_label_pattern():
    assert suggest_next_round("i-2", 2) == ("i-3", 3)
    assert suggest_next_round("custom", 4) == ("custom", 5)
