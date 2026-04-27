import json

from pattern_analyzer.service import SessionService
from pattern_analyzer.storage import SessionStore
from pattern_analyzer.rounds import round_label


def test_create_session_starts_at_i2(tmp_path):
    store = SessionStore(tmp_path)
    service = SessionService(store)
    session = service.create_session(["A", "B", "C", "D", "E", "F", "G", "H"])
    assert (session.phase, session.round_no) == (1, 2)
    assert round_label(session.phase, session.round_no) == "i-2"


def test_save_round_writes_each_match_to_json(tmp_path):
    store = SessionStore(tmp_path)
    service = SessionService(store)
    session = service.create_session(["A", "B", "C", "D", "E", "F", "G", "H"])

    session = service.save_round_pairs(session, ["A:B", "C:D", "E:F", "G:H"])
    assert len(session.matches) == 4
    assert (session.phase, session.round_no) == (1, 3)

    saved = json.loads(store.session_path(session.id).read_text(encoding="utf-8"))
    assert len(saved["matches"]) == 4
    assert saved["matches"][0]["round_label"] == "i-2"


def test_auto_skip_monster_ii3_after_ii2(tmp_path):
    store = SessionStore(tmp_path)
    service = SessionService(store)
    session = service.create_session(["A", "B", "C", "D", "E", "F", "G", "H"])

    service.save_round_pairs(session, ["A:B", "C:D", "E:F", "G:H"])  # i-2 -> i-3
    session = service.load_session(session.id)
    service.save_round_pairs(session, ["A:C", "B:D", "E:G", "F:H"])  # i-3 -> i-4
    session = service.load_session(session.id)
    service.save_round_pairs(session, ["A:D", "B:C", "E:H", "F:G"])  # i-4 -> ii-1
    session = service.load_session(session.id)
    session = service.save_round_pairs(session, ["A:E", "B:F", "C:G", "D:H"])  # ii-1 -> ii-2
    session = service.load_session(session.id)
    session = service.save_round_pairs(session, ["A:F", "B:E", "C:H", "D:G"])  # ii-2 -> ii-4 (skip ii-3)

    assert round_label(session.phase, session.round_no) == "ii-4"


def test_finish_session_creates_report(tmp_path):
    store = SessionStore(tmp_path)
    service = SessionService(store)
    session = service.create_session(["A", "B", "C", "D", "E", "F", "G", "H"])
    session = service.save_round_pairs(session, ["A:B", "C:D", "E:F", "G:H"])
    session = service.finish_session(session)
    assert session.is_finished is True
    assert session.report is not None
    assert session.report["summary"]["total_matches_recorded"] == 4

