"""End-of-session analysis for matchup patterns."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from pattern_analyzer.models import SessionState



def build_record(session: SessionState) -> dict[str, Any]:
    """Return only id, players, and matches (no analysis)."""
    return {
        "id": session.id,
        "players": session.players,
        "matches": [
            {
                k: v
                for k, v in match.items()
                if k in ("round_label", "phase", "round_no", "player1", "player2")
            }
            for match in session.matches
        ],
    }


def find_static_rules(round_pairs: dict[str, list[tuple[str, str]]], player_opponents: dict[str, list[str]]) -> list[dict[str, str]]:
    """
    Analisis otomatis untuk mendeteksi rule statis baru pada pairing antar ronde.
    Mencari hubungan konsisten antar lawan di ronde-ronde berurutan.
    """
    # Kumpulkan semua label ronde dan urutkan secara natural (misal: i-2, i-3, i-4, ii-1, ...)
    import re
    def round_sort_key(label):
        m = re.match(r"([ivx]+)-(\d+)", label)
        if not m:
            return (label, 0)
        roman, num = m.groups()
        roman_map = {"i":1,"ii":2,"iii":3,"iv":4,"v":5,"vi":6,"vii":7,"viii":8,"ix":9,"x":10}
        return (roman_map.get(roman, 0), int(num))
    labels = sorted(round_pairs.keys(), key=round_sort_key)

    # Cek untuk setiap pemain, apakah lawan di ronde N+1 selalu punya hubungan tetap dengan lawan di ronde N
    rules = []
    for idx in range(1, len(labels)):
        prev_label = labels[idx-1]
        curr_label = labels[idx]
        prev_pairs = round_pairs[prev_label]
        curr_pairs = round_pairs[curr_label]
        # Buat mapping: pemain -> lawan di prev dan curr
        prev_map = {p1: p2 for p1, p2 in prev_pairs}
        prev_map.update({p2: p1 for p1, p2 in prev_pairs})
        curr_map = {p1: p2 for p1, p2 in curr_pairs}
        curr_map.update({p2: p1 for p1, p2 in curr_pairs})
        # Cek apakah ada pola tetap, misal: lawan di curr selalu lawan dari lawan di prev
        candidate = {}
        for player in prev_map:
            if player in curr_map:
                prev_opp = prev_map[player]
                curr_opp = curr_map[player]
                candidate.setdefault((prev_opp, curr_opp), 0)
                candidate[(prev_opp, curr_opp)] += 1
        # Jika ada pola dominan, catat sebagai kandidat rule statis
        if candidate:
            most_common = max(candidate.items(), key=lambda x: x[1])
            if most_common[1] >= len(prev_map) // 2:
                rules.append({
                    "from_round": prev_label,
                    "to_round": curr_label,
                    "pattern": f"Lawan di {curr_label} cenderung adalah lawan dari lawan di {prev_label}",
                    "example": f"{most_common[0][0]} → {most_common[0][1]}",
                    "support": f"{most_common[1]}/{len(prev_map)} pemain"
                })
    return rules

