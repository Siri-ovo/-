from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


def _record_id(created_at: str, profile_text: str) -> str:
    payload = f"{created_at}\n{profile_text}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:12]


def load_history_records(history_path: Path, limit: int | None = None) -> list[dict]:
    if not history_path.exists():
        return []
    records = []
    with history_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    return records[:limit] if limit is not None else records


def save_history_record(
    history_path: Path,
    profile_text: str,
    report: dict,
    evidence_jobs: list[dict],
    model_used: str,
    created_at: str | None = None,
) -> dict:
    created_at = created_at or datetime.now().isoformat(timespec="seconds")
    recommendations = report.get("recommendations", [])
    first = recommendations[0] if recommendations else {}
    record = {
        "id": _record_id(created_at, profile_text),
        "created_at": created_at,
        "profile_text": profile_text,
        "report": report,
        "evidence_jobs": evidence_jobs,
        "model_used": model_used,
        "top_recommendation": first.get("title", ""),
        "top_score": first.get("final_score", 0),
        "evidence_count": len(evidence_jobs),
    }
    history_path.parent.mkdir(parents=True, exist_ok=True)
    records = [record] + load_history_records(history_path)
    with history_path.open("w", encoding="utf-8") as fh:
        for item in records:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    return record
