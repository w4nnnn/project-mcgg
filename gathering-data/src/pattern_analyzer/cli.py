"""CLI and interactive TUI flow."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

try:
    import msvcrt
except ImportError:  # pragma: no cover
    msvcrt = None

from pattern_analyzer.rounds import round_label
from pattern_analyzer.service import SessionService
from pattern_analyzer.storage import SessionStore


def _print_report(report: dict) -> None:
    summary = report.get("summary", {})
    print("\n=== Laporan Pola ===")
    print(f"Sesi: {summary.get('session_id')}")
    print(f"Total ronde: {summary.get('total_rounds_recorded')}")
    print(f"Total match: {summary.get('total_matches_recorded')}")
    print(f"Confidence: {summary.get('confidence')}")

    print("\nFrequent matchups:")
    frequent = report.get("frequent_matchups", [])
    if not frequent:
        print("- Tidak ada pair berulang.")
    for item in frequent:
        print(f"- {item['pair']} ({item['count']}x)")

    anomalies = report.get("anomalies", {})
    print("\nAnomali:")
    streaks = anomalies.get("repeated_consecutive_opponents", [])
    warnings = anomalies.get("active_player_warnings", [])
    if not streaks and not warnings:
        print("- Tidak ada anomali.")
    for item in streaks:
        print(f"- {item['message']}")
    for item in warnings:
        print(f"- {item['round']}: {item['warning']}")


def _collect_players() -> list[str]:
    print("Masukkan 8 nama pemain.")
    players: list[str] = []
    while len(players) < 8:
        name = input(f"Nama pemain #{len(players)+1}: ").strip()
        if not name:
            print("Nama tidak boleh kosong.")
            continue
        if any(name.lower() == existing.lower() for existing in players):
            print("Nama duplikat, masukkan nama lain.")
            continue
        players.append(name)
    return players


def _select_with_arrow(title: str, options: list[str], helper: str = "") -> str:
    """Pick one option with arrow keys on Windows."""
    if not options:
        raise ValueError("Options tidak boleh kosong.")

    if msvcrt is None:
        # Fallback for non-Windows runtime.
        return input(f"{title} ({', '.join(options)}): ").strip()

    idx = 0
    while True:
        print("\n" + title)
        if helper:
            print(helper)
        for i, option in enumerate(options):
            marker = ">" if i == idx else " "
            print(f"{marker} {option}")
        key = msvcrt.getch()
        if key == b"\r":
            return options[idx]
        if key in (b"\x00", b"\xe0"):
            key2 = msvcrt.getch()
            if key2 == b"H":
                idx = (idx - 1) % len(options)
            elif key2 == b"P":
                idx = (idx + 1) % len(options)


def _collect_round_pairs(
    label: str,
    players: list[str],
    chooser: Callable[[str, list[str], str], str] = _select_with_arrow,
) -> list[str]:
    print(f"\nRonde {label}: pilih pairing dengan panah atas/bawah lalu Enter")
    remaining = players.copy()
    pairs: list[str] = []
    pair_no = 1
    while len(remaining) >= 2:
        p1 = chooser(
            f"Pair #{pair_no} - pilih pemain pertama",
            remaining,
            "Gunakan arrow up/down + Enter",
        )
        options_p2 = [name for name in remaining if name.lower() != p1.lower()]
        p2 = chooser(
            f"Pair #{pair_no} - pilih lawan untuk {p1}",
            options_p2,
            "Gunakan arrow up/down + Enter",
        )
        pairs.append(f"{p1}:{p2}")
        remaining = [name for name in remaining if name.lower() not in {p1.lower(), p2.lower()}]
        pair_no += 1
    return pairs


def run_tui(service: SessionService) -> None:
    players = _collect_players()
    session = service.create_session(players)
    print(f"\nSesi baru dibuat: {session.id}")
    print(f"Mulai input dari ronde {round_label(session.phase, session.round_no)}")
    while True:
        current_label = round_label(session.phase, session.round_no)
        pairs = _collect_round_pairs(current_label, session.players)
        try:
            session = service.save_round_pairs(session, pairs)
        except ValueError as exc:
            print(f"Input tidak valid: {exc}")
            continue

        next_label = round_label(session.phase, session.round_no)
        print(f"Tersimpan. Ronde berikutnya: {next_label}")
        action = input("Enter untuk lanjut, ketik 'stop' untuk selesai: ").strip().lower()
        if action == "stop":
            session = service.finish_session(session)
            print("\nSesi selesai. Analisis dibuat.")
            if session.report:
                _print_report(session.report)
            break


def run_resume(service: SessionService, session_id: str | None) -> None:
    sid = session_id
    if not sid:
        sid = service.store.latest_session_id()
        if not sid:
            print("Belum ada sesi tersimpan.")
            return
    session = service.load_session(sid)
    if session.is_finished:
        print(f"Sesi {session.id} sudah selesai. Gunakan 'report --session-id {session.id}'.")
        return
    print(f"Melanjutkan sesi {session.id}. Posisi saat ini: {round_label(session.phase, session.round_no)}")
    while True:
        current_label = round_label(session.phase, session.round_no)
        pairs = _collect_round_pairs(current_label, session.players)
        try:
            session = service.save_round_pairs(session, pairs)
        except ValueError as exc:
            print(f"Input tidak valid: {exc}")
            continue
        next_label = round_label(session.phase, session.round_no)
        print(f"Tersimpan. Ronde berikutnya: {next_label}")
        action = input("Enter untuk lanjut, ketik 'stop' untuk selesai: ").strip().lower()
        if action == "stop":
            session = service.finish_session(session)
            print("\nSesi selesai. Analisis dibuat.")
            if session.report:
                _print_report(session.report)
            break


def run_report(service: SessionService, session_id: str | None) -> None:
    sid = session_id or service.store.latest_session_id()
    if not sid:
        print("Belum ada sesi tersimpan.")
        return
    session = service.load_session(sid)
    if not session.report:
        session = service.finish_session(session)
    assert session.report is not None
    _print_report(session.report)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcgg-data", description="MCGG 8-player data gathering TUI")
    parser.add_argument("--data-dir", type=Path, default=None, help="Path custom folder data")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("tui", help="Mulai sesi baru interaktif")
    resume_parser = subparsers.add_parser("resume", help="Lanjutkan sesi")
    resume_parser.add_argument("--session-id", default=None)
    report_parser = subparsers.add_parser("report", help="Tampilkan laporan")
    report_parser.add_argument("--session-id", default=None)
    subparsers.add_parser("list-sessions", help="Lihat daftar sesi")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = SessionStore(args.data_dir)
    service = SessionService(store)

    if args.command == "tui":
        run_tui(service)
        return 0
    if args.command == "resume":
        run_resume(service, args.session_id)
        return 0
    if args.command == "report":
        run_report(service, args.session_id)
        return 0
    if args.command == "list-sessions":
        sessions = store.list_sessions()
        if not sessions:
            print("Belum ada sesi.")
            return 0
        for item in sessions:
            status = "finished" if item["is_finished"] else "active"
            print(f"{item['id']} | {status} | {round_label(item['phase'], item['round_no'])}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

