from __future__ import annotations


def clamp_score(value: float) -> int:
    return max(0, min(100, round(float(value))))


def retrieval_score_from_similarity(similarity: float) -> int:
    return clamp_score(float(similarity) * 100)


def combine_scores(retrieval_score: float, llm_score: float) -> int:
    retrieval = clamp_score(retrieval_score)
    llm = clamp_score(llm_score)
    return clamp_score(retrieval * 0.6 + llm * 0.4)


SCORE_WEIGHTS = [
    ("RAG 岗位检索相关度", "retrieval_score", 0.4),
    ("技能匹配度", "skill_score", 0.2),
    ("城市匹配度", "city_score", 0.1),
    ("学历匹配度", "degree_score", 0.1),
    ("行业偏好匹配度", "industry_score", 0.1),
    ("大模型综合评价", "llm_score", 0.1),
]


def build_score_breakdown(
    retrieval_score: float,
    skill_score: float,
    city_score: float,
    degree_score: float,
    industry_score: float,
    llm_score: float,
) -> dict:
    values = {
        "retrieval_score": clamp_score(retrieval_score),
        "skill_score": clamp_score(skill_score),
        "city_score": clamp_score(city_score),
        "degree_score": clamp_score(degree_score),
        "industry_score": clamp_score(industry_score),
        "llm_score": clamp_score(llm_score),
    }
    components = []
    total = 0.0
    for name, key, weight in SCORE_WEIGHTS:
        weighted = round(values[key] * weight, 2)
        total += weighted
        components.append({"name": name, "score": values[key], "weight": weight, "weighted": weighted})
    return {"final_score": clamp_score(total), "components": components}


def score_for_reference_jobs(reference_jobs: list, evidence_jobs: list[dict]) -> int:
    if not evidence_jobs:
        return 0
    if not reference_jobs:
        return retrieval_score_from_similarity(max(job.get("similarity", 0) for job in evidence_jobs))

    names = set()
    for item in reference_jobs:
        if isinstance(item, str):
            names.add(item)
        elif isinstance(item, dict):
            for key in ("job_name", "title"):
                if item.get(key):
                    names.add(str(item[key]))

    matched = []
    for job in evidence_jobs:
        job_name = str(job.get("job_name", ""))
        if any(name and (name in job_name or job_name in name) for name in names):
            matched.append(float(job.get("similarity", 0)))

    if not matched:
        matched = [float(job.get("similarity", 0)) for job in evidence_jobs[:3]]
    return retrieval_score_from_similarity(sum(matched) / len(matched))


def _split_terms(value: str) -> list[str]:
    separators = [",", "，", "、", ";", "；", "\n", " "]
    terms = [value]
    for sep in separators:
        terms = [piece for term in terms for piece in term.split(sep)]
    return [term.strip().lower() for term in terms if term.strip()]


def _collect_text(*values: object) -> str:
    return " ".join(str(value or "") for value in values).lower()


def _match_terms_score(terms: list[str], corpus: str) -> int:
    if not terms:
        return 60
    matched = sum(1 for term in terms if term and term.lower() in corpus)
    return clamp_score(matched / len(terms) * 100)


def score_profile_match(form: dict, recommendation: dict, evidence_jobs: list[dict]) -> dict:
    retrieval_score = score_for_reference_jobs(recommendation.get("reference_jobs", []), evidence_jobs)
    evidence_text = _collect_text(
        recommendation.get("title", ""),
        recommendation.get("reason", ""),
        *[
            _collect_text(
                job.get("job_name", ""),
                job.get("area_name", ""),
                job.get("degree_name", ""),
                job.get("industry", ""),
                job.get("description", ""),
                job.get("document", ""),
            )
            for job in evidence_jobs
        ],
    )
    skill_score = _match_terms_score(_split_terms(str(form.get("skills", ""))), evidence_text)
    city_score = _match_terms_score(_split_terms(str(form.get("city", ""))), evidence_text)
    degree_score = _match_terms_score(_split_terms(str(form.get("degree", ""))), evidence_text)
    industry_score = _match_terms_score(_split_terms(str(form.get("industry", ""))), evidence_text)
    return build_score_breakdown(
        retrieval_score=retrieval_score,
        skill_score=skill_score,
        city_score=city_score,
        degree_score=degree_score,
        industry_score=industry_score,
        llm_score=recommendation.get("llm_score", 0),
    )
