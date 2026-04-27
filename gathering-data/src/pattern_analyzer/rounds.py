"""Round helpers for MCGG phase-round progression."""

from __future__ import annotations


ROMAN = {
    1: "i",
    2: "ii",
    3: "iii",
    4: "iv",
    5: "v",
    6: "vi",
    7: "vii",
    8: "viii",
    9: "ix",
    10: "x",
}


def round_label(phase: int, round_no: int) -> str:
    """Build label such as i-2, ii-4."""
    prefix = ROMAN.get(phase, f"p{phase}")
    return f"{prefix}-{round_no}"


def is_monster_round(phase: int, round_no: int) -> bool:
    """Monster rounds based on the rule reference."""
    if phase == 1:
        return round_no == 1
    return round_no == 3


def max_round_in_phase(phase: int) -> int:
    """Phase 1 has 4 rounds, phase 2+ has 6 rounds."""
    return 4 if phase == 1 else 6


def next_round(phase: int, round_no: int) -> tuple[int, int]:
    """Advance to next phase/round."""
    maximum = max_round_in_phase(phase)
    if round_no < maximum:
        return phase, round_no + 1
    return phase + 1, 1


def next_player_round(phase: int, round_no: int) -> tuple[int, int]:
    """Advance until a non-monster round is found."""
    p, r = phase, round_no
    while is_monster_round(p, r):
        p, r = next_round(p, r)
    return p, r

