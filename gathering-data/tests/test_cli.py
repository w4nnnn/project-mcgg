import builtins

from pattern_analyzer.cli import _collect_round_pairs, run_tui
from pattern_analyzer.service import SessionService
from pattern_analyzer.storage import SessionStore


def test_collect_round_pairs_with_custom_chooser():
    players = ["A", "B", "C", "D", "E", "F", "G", "H"]
    picks = iter(["A", "B", "C", "D", "E", "F", "G", "H"])

    def fake_chooser(_title, _options, _helper):
        return next(picks)

    pairs = _collect_round_pairs("i-2", players, chooser=fake_chooser)
    assert pairs == ["A:B", "C:D", "E:F", "G:H"]


def test_tui_flow_single_round_then_stop(tmp_path, monkeypatch, capsys):
    store = SessionStore(tmp_path)
    service = SessionService(store)

    inputs = iter(
        [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",  # players
            "stop",
        ]
    )
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))
    monkeypatch.setattr(
        "pattern_analyzer.cli._collect_round_pairs",
        lambda _label, _players: ["A:B", "C:D", "E:F", "G:H"],
    )

    run_tui(service)
    out = capsys.readouterr().out
    assert "Sesi baru dibuat" in out
    assert "Sesi selesai. Analisis dibuat." in out

    sessions = store.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["is_finished"] is True

