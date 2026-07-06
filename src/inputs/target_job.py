from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from src.rag.job_ranker import normalized_retrieval_score, relevance_level


@dataclass(frozen=True)
class TargetJobContext:
    url: str
    description: str
    text: str
    search_text: str
    has_content: bool


def _clean_lines(value: str) -> str:
    return "\n".join(line.strip() for line in str(value or "").splitlines() if line.strip())


def normalize_url(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return value.rstrip("/")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), "", ""))


def build_target_job_context(url: str, description: str) -> TargetJobContext:
    clean_url = str(url or "").strip()
    clean_description = _clean_lines(description)
    parts = []
    search_parts = []
    if clean_url:
        parts.append(f"目标岗位链接：{clean_url}")
        search_parts.append(clean_url)
    if clean_description:
        parts.append(f"目标岗位描述：{clean_description}")
        search_parts.append(clean_description)
    text = "\n".join(parts)
    search_text = "\n".join(search_parts)
    return TargetJobContext(
        url=clean_url,
        description=clean_description,
        text=text,
        search_text=search_text,
        has_content=bool(text),
    )


def find_job_by_source_url(jobs: list[dict], url: str) -> dict | None:
    target_url = normalize_url(url)
    if not target_url:
        return None
    for job in jobs:
        source_url = normalize_url(str(job.get("source_url", "")))
        if source_url and source_url == target_url:
            return dict(job)
    return None


def _same_job(left: dict, right: dict) -> bool:
    left_url = normalize_url(str(left.get("source_url", "")))
    right_url = normalize_url(str(right.get("source_url", "")))
    if left_url and right_url:
        return left_url == right_url
    return (
        str(left.get("job_name", "")).strip(),
        str(left.get("company_name", "")).strip(),
    ) == (
        str(right.get("job_name", "")).strip(),
        str(right.get("company_name", "")).strip(),
    )


def merge_target_job_with_evidence(target_job: dict | None, evidence_jobs: list[dict], top_k: int = 10) -> list[dict]:
    if not target_job:
        return evidence_jobs[:top_k]

    target = dict(target_job)
    target["target_job"] = True
    target["similarity"] = 1.0
    target["retrieval_score"] = 100
    target["relevance_level"] = "用户指定"

    merged = [target]
    for job in evidence_jobs:
        if not _same_job(target, job):
            item = dict(job)
            item.setdefault("retrieval_score", normalized_retrieval_score(float(item.get("similarity", 0))))
            item.setdefault("relevance_level", relevance_level(int(item.get("retrieval_score", 0))))
            merged.append(item)
        if len(merged) >= top_k:
            break
    return merged
