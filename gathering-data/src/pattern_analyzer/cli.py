"""CLI launcher for Tkinter GUI."""

from __future__ import annotations

from pattern_analyzer.gui import run_gui


def main(argv: list[str] | None = None) -> int:
    _ = argv
    run_gui()
    return 0
