from __future__ import annotations

import json
from pathlib import Path


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _batch_mode(path: Path, rows: list[dict]) -> str:
    if "list_batch" in path.name:
        return "list"
    if rows and all(row.get("detail_status") == "list_only" for row in rows):
        return "list"
    return "detail"


def _valid_keyword(value: object) -> str:
    keyword = str(value or "").strip()
    if not keyword or set(keyword) == {"?"}:
        return ""
    return keyword


def summarize_crawl_batches(batch_dir: Path, limit: int = 20) -> dict:
    if not batch_dir.exists():
        return {
            "total_batches": 0,
            "total_rows": 0,
            "list_only_rows": 0,
            "detail_rows": 0,
            "batches": [],
        }
    batch_items = []
    total_rows = 0
    list_only_rows = 0
    detail_rows = 0
    for path in sorted(batch_dir.glob("*.jsonl"), key=lambda item: item.name, reverse=True):
        rows = _read_jsonl(path)
        keywords = sorted({keyword for row in rows if (keyword := _valid_keyword(row.get("keyword")))})
        row_count = len(rows)
        list_count = sum(1 for row in rows if row.get("detail_status") == "list_only")
        detail_count = row_count - list_count
        total_rows += row_count
        list_only_rows += list_count
        detail_rows += detail_count
        batch_items.append(
            {
                "file": path.name,
                "mode": _batch_mode(path, rows),
                "rows": row_count,
                "list_only_rows": list_count,
                "detail_rows": detail_count,
                "keywords": ", ".join(keywords),
                "modified_time": path.stat().st_mtime,
            }
        )
    return {
        "total_batches": len(batch_items),
        "total_rows": total_rows,
        "list_only_rows": list_only_rows,
        "detail_rows": detail_rows,
        "batches": batch_items[:limit],
    }
