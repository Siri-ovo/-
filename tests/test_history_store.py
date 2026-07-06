from src.storage.history import load_history_records, save_history_record


def test_save_history_record_prepends_latest_record(tmp_path):
    history_path = tmp_path / "history.jsonl"

    first = save_history_record(
        history_path,
        profile_text="first profile",
        report={"recommendations": [{"title": "Old", "final_score": 70}]},
        evidence_jobs=[],
        model_used="qwen2:0.5b",
        created_at="2026-07-01T10:00:00",
    )
    second = save_history_record(
        history_path,
        profile_text="second profile",
        report={"recommendations": [{"title": "New", "final_score": 90}]},
        evidence_jobs=[{"job_name": "Evidence"}],
        model_used="qwen3:4b",
        created_at="2026-07-02T10:00:00",
    )

    records = load_history_records(history_path)

    assert first["id"] != second["id"]
    assert [record["profile_text"] for record in records] == ["second profile", "first profile"]
    assert records[0]["top_recommendation"] == "New"
    assert records[0]["evidence_count"] == 1
