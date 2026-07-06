from __future__ import annotations


def normalized_retrieval_score(similarity: float, strong_match_threshold: float = 0.25) -> int:
    value = max(0.0, float(similarity))
    return max(0, min(100, round(value / strong_match_threshold * 100)))


def relevance_level(score: int) -> str:
    if score >= 75:
        return "高"
    if score >= 40:
        return "中"
    return "低"


def _split_terms(value: str) -> list[str]:
    separators = [",", "，", "、", ";", "；", "\n", " "]
    terms = [str(value or "")]
    for sep in separators:
        terms = [piece for term in terms for piece in term.split(sep)]
    return [term.strip().lower() for term in terms if term.strip()]


def _job_text(job: dict) -> str:
    return " ".join(
        str(job.get(key, "") or "")
        for key in (
            "job_name",
            "company_name",
            "area_name",
            "degree_name",
            "major",
            "job_type",
            "industry",
            "keyword",
            "description",
            "document",
        )
    ).lower()


def _constraint_text(job: dict) -> str:
    keys = [
        "job_name",
        "company_name",
        "area_name",
        "degree_name",
        "major",
        "job_type",
        "industry",
    ]
    if job.get("detail_status") != "list_only":
        keys.extend(["description", "document"])
    return " ".join(str(job.get(key, "") or "") for key in keys).lower()


def _requested_job_type(value: str) -> str:
    text = str(value or "").lower()
    if "实习" in text or "intern" in text:
        return "intern"
    if "兼职" in text or "part" in text:
        return "part_time"
    if "全职" in text or "full" in text:
        return "full_time"
    return ""


def _job_type_matches(job: dict, requested: str) -> bool:
    if not requested:
        return True
    text = _job_text(job)
    if requested == "intern":
        return "实习" in text or "intern" in text
    if requested == "part_time":
        return "兼职" in text or "part" in text
    if requested == "full_time":
        return "实习" not in text and "兼职" not in text and "intern" not in text
    return True


def _term_match_score(terms: list[str], text: str) -> int:
    if not terms:
        return 0
    matched = sum(1 for term in terms if term in text)
    return round(matched / len(terms) * 100)


def _constraint_score(job: dict, constraints: dict) -> int:
    text = _constraint_text(job)
    major_score = _term_match_score(_split_terms(constraints.get("major", "")), text)
    industry_score = _term_match_score(_split_terms(constraints.get("industry", "")), text)
    skill_score = _term_match_score(_split_terms(constraints.get("skills", "")), text)
    city_score = _term_match_score(_split_terms(constraints.get("city", "")), text)
    return round(major_score * 0.25 + industry_score * 0.25 + skill_score * 0.2 + city_score * 0.3)


def _domain_score(job: dict, constraints: dict) -> int:
    text = _constraint_text(job)
    major_terms = _split_terms(constraints.get("major", ""))
    industry_terms = _split_terms(constraints.get("industry", ""))
    skill_terms = _split_terms(constraints.get("skills", ""))
    major_score = _term_match_score(major_terms, text)
    industry_score = _term_match_score(industry_terms, text)
    skill_score = _term_match_score(skill_terms, text)
    if industry_terms:
        return industry_score
    if skill_terms:
        return skill_score
    return major_score


def filter_and_rank_jobs(jobs: list[dict], constraints: dict, top_k: int = 10) -> list[dict]:
    requested_type = _requested_job_type(str(constraints.get("job_type", "")))
    typed = [job for job in jobs if _job_type_matches(job, requested_type)]
    if requested_type and not typed:
        return []
    candidates = typed if requested_type else jobs
    ranked = []
    has_domain_terms = bool(
        _split_terms(str(constraints.get("major", "")))
        or _split_terms(str(constraints.get("industry", "")))
        or _split_terms(str(constraints.get("skills", "")))
    )
    for job in candidates:
        item = dict(job)
        item["retrieval_score"] = normalized_retrieval_score(float(item.get("similarity", 0)))
        item["relevance_level"] = relevance_level(item["retrieval_score"])
        item["constraint_score"] = _constraint_score(item, constraints)
        item["domain_score"] = _domain_score(item, constraints)
        if has_domain_terms and item["domain_score"] == 0:
            continue
        item["rank_score"] = round(item["retrieval_score"] * 0.45 + item["constraint_score"] * 0.55)
        ranked.append(item)
    ranked.sort(key=lambda item: (item["rank_score"], item["retrieval_score"]), reverse=True)
    return ranked[:top_k]
