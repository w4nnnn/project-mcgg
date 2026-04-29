"""Domain models and validation for gathering-data GUI app."""

from __future__ import annotations

from typing import Any


def normalize_players(players: list[str]) -> list[str]:
    normalized = [p.strip() for p in players if p.strip()]
    if len(normalized) < 2:
        raise ValueError("Minimal isi 2 nama pemain.")
    if len(normalized) > 8:
        raise ValueError("Maksimal 8 pemain.")
    seen: set[str] = set()
    for player in normalized:
        key = player.lower()
        if key in seen:
            raise ValueError(f"Nama duplikat: {player}")
        seen.add(key)
    return normalized


def build_round_matches(
    players: list[str],
    round_label: str,
    phase: int,
    round_no: int,
    pairs: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    valid_players = {p.lower(): p for p in players}
    used_players: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    matches: list[dict[str, Any]] = []
    mirror_count = 0

    filled_pairs = [(a.strip(), b.strip()) for a, b in pairs if a.strip() or b.strip()]
    if not filled_pairs:
        raise ValueError("Isi minimal 1 pairing.")

    for a, b in filled_pairs:
        if not a or not b:
            raise ValueError("Pairing harus terisi lengkap (player1 dan player2).")

        ka = a.lower()
        kb = b.lower()

        if ka == kb:
            raise ValueError("Satu pairing tidak boleh pemain yang sama.")

        if ka == "mirror" and kb == "mirror":
            raise ValueError("Pairing MIRROR tidak valid.")

        if ka == "mirror" or kb == "mirror":
            mirror_count += 1
            real_key = kb if ka == "mirror" else ka
            if real_key not in valid_players:
                raise ValueError("Player MIRROR harus dipasangkan dengan pemain terdaftar.")
            if real_key in used_players:
                raise ValueError("Pemain tidak boleh muncul lebih dari sekali di ronde yang sama.")
            used_players.add(real_key)
            matches.append(
                {
                    "round_label": round_label.strip(),
                    "phase": int(phase),
                    "round_no": int(round_no),
                    "player1": valid_players[real_key],
                    "player2": "MIRROR",
                }
            )
            continue

        if ka not in valid_players or kb not in valid_players:
            raise ValueError("Ada pemain yang tidak terdaftar pada sesi.")

        canonical = tuple(sorted((ka, kb)))
        if canonical in seen_pairs:
            raise ValueError("Ada pairing duplikat di ronde yang sama.")
        if ka in used_players or kb in used_players:
            raise ValueError("Pemain tidak boleh muncul lebih dari sekali di ronde yang sama.")

        used_players.add(ka)
        used_players.add(kb)
        seen_pairs.add(canonical)

        matches.append(
            {
                "round_label": round_label.strip(),
                "phase": int(phase),
                "round_no": int(round_no),
                "player1": valid_players[ka],
                "player2": valid_players[kb],
            }
        )

    if mirror_count > 1:
        raise ValueError("Maksimal 1 pairing MIRROR per ronde.")

    return matches


def round_key(match: dict[str, Any]) -> tuple[str, int, int]:
    return (str(match["round_label"]), int(match["phase"]), int(match["round_no"]))


def upsert_round_matches(existing_matches: list[dict[str, Any]], new_matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not new_matches:
        return list(existing_matches)

    key = round_key(new_matches[0])
    filtered = [m for m in existing_matches if round_key(m) != key]
    filtered.extend(new_matches)
    return filtered


def suggest_next_round(round_label: str, round_no: int) -> tuple[str, int]:
    next_no = int(round_no) + 1
    clean = round_label.strip()
    if clean.startswith("i-") and clean[2:].isdigit():
        return (f"i-{next_no}", next_no)
    return (clean, next_no)
