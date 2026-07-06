from __future__ import annotations

from collections import Counter


def _top_counts(values: list[str], top_n: int) -> list[dict]:
    counter = Counter(value for value in values if value)
    return [{"name": name, "count": count} for name, count in counter.most_common(top_n)]


def summarize_jobs(jobs: list[dict], top_n: int = 5) -> dict:
    updates = [str(job.get("update_date", "")) for job in jobs if job.get("update_date")]
    return {
        "total_jobs": len(jobs),
        "source": "NCSS",
        "latest_update": max(updates) if updates else "",
        "city_distribution": _top_counts([str(job.get("area_name", "")) for job in jobs], top_n),
        "degree_distribution": _top_counts([str(job.get("degree_name", "")) for job in jobs], top_n),
        "keyword_distribution": _top_counts([str(job.get("keyword", "")) for job in jobs], top_n),
    }
