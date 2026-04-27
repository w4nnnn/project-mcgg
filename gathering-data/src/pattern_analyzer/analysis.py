"""End-of-session analysis for matchup patterns."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from pattern_analyzer.models import SessionState


def build_report(session: SessionState) -> dict[str, Any]:
    """Build simple frequency + anomaly report from stored matches."""
    pair_counter: Counter[tuple[str, str]] = Counter()
    player_opponents: dict[str, list[str]] = defaultdict(list)
    active_by_round: dict[str, set[str]] = defaultdict(set)
    round_pairs: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for match in session.matches:
        p1 = match["player1"]
        p2 = match["player2"]
        label = match["round_label"]
        pair = tuple(sorted((p1, p2)))
        pair_counter[pair] += 1
        player_opponents[p1].append(p2)
        player_opponents[p2].append(p1)
        active_by_round[label].add(p1)
        active_by_round[label].add(p2)
        round_pairs[label].append((p1, p2))

    repeated_pairs = [
        {"pair": f"{a} vs {b}", "count": count}
        for (a, b), count in pair_counter.items()
        if count > 1
    ]
    repeated_pairs.sort(key=lambda x: x["count"], reverse=True)

    repeat_streaks: list[dict[str, str]] = []
    for player, opps in player_opponents.items():
        for idx in range(1, len(opps)):
            if opps[idx] == opps[idx - 1]:
                repeat_streaks.append(
                    {
                        "player": player,
                        "opponent": opps[idx],
                        "message": f"{player} bertemu {opps[idx]} beruntun.",
                    }
                )

    active_warnings = []
    for label, players in active_by_round.items():
        if len(players) < 8:
            active_warnings.append(
                {
                    "round": label,
                    "active_players": len(players),
                    "warning": "Pemain aktif < 8, akurasi pola menurun.",
                }
            )

    total_rounds = len(round_pairs)
    total_matches = len(session.matches)
    confidence = "high"
    if active_warnings:
        confidence = "medium"
    if len(active_warnings) > 2:
        confidence = "low"

    return {
        "summary": {
            "session_id": session.id,
            "total_rounds_recorded": total_rounds,
            "total_matches_recorded": total_matches,
            "confidence": confidence,
        },
        "frequent_matchups": repeated_pairs,
        "anomalies": {
            "repeated_consecutive_opponents": repeat_streaks,
            "active_player_warnings": active_warnings,
        },
    }

