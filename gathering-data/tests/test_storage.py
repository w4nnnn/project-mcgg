from pattern_analyzer.storage import SessionStore


def test_store_create_load_update_delete(tmp_path):
    store = SessionStore(tmp_path)
    payload = {
        "id": "abc12345",
        "players": ["A", "B", "C", "D", "E", "F", "G", "H"],
        "matches": [],
    }

    store.save(payload)
    loaded = store.load("abc12345")
    assert loaded["id"] == "abc12345"

    payload["matches"].append(
        {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "A", "player2": "B"}
    )
    store.save(payload)
    loaded2 = store.load("abc12345")
    assert len(loaded2["matches"]) == 1

    sessions = store.list_sessions()
    assert sessions == ["abc12345"]

    store.delete("abc12345")
    assert store.list_sessions() == []
