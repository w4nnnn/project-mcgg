from pattern_analyzer.rounds import is_monster_round, next_player_round, next_round, round_label


def test_round_label():
    assert round_label(1, 2) == "i-2"
    assert round_label(2, 4) == "ii-4"


def test_monster_round_mapping():
    assert is_monster_round(1, 1)
    assert not is_monster_round(1, 2)
    assert is_monster_round(2, 3)
    assert is_monster_round(3, 3)
    assert not is_monster_round(3, 4)


def test_skip_monster_rounds():
    assert next_player_round(1, 1) == (1, 2)
    assert next_player_round(2, 3) == (2, 4)
    assert next_player_round(3, 3) == (3, 4)


def test_next_round_transition():
    assert next_round(1, 4) == (2, 1)
    assert next_round(2, 6) == (3, 1)

