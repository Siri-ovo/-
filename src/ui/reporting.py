from __future__ import annotations


def text(value: str) -> str:
    return value.encode("ascii").decode("unicode_escape")


COL_STAGE = text(r"\u9636\u6bb5")
COL_PROCESS = text(r"\u7cfb\u7edf\u5904\u7406")
COL_EVIDENCE = text(r"\u9875\u9762\u8bc1\u636e")
COL_ITEM = text(r"\u9879\u76ee")
COL_DESC = text(r"\u8bf4\u660e")
COL_ADVICE = text(r"\u5efa\u8bae")
COL_SCORE_ITEM = text(r"\u8bc4\u5206\u9879")
COL_RAW_SCORE = text(r"\u539f\u59cb\u5206")
COL_WEIGHT = text(r"\u6743\u91cd")
COL_WEIGHT_PERCENT = text(r"\u6743\u91cd(%)")
COL_WEIGHTED = text(r"\u52a0\u6743\u5206")
COL_GOAL = text(r"\u9636\u6bb5\u76ee\u6807")
COL_TASKS = text(r"\u5177\u4f53\u4efb\u52a1")
COL_DELIVERABLE = text(r"\u53ef\u4ea4\u4ed8\u6210\u679c")
COL_JOB_NAME = text(r"\u5c97\u4f4d\u540d\u79f0")
COL_COMPANY = text(r"\u516c\u53f8")
COL_AREA = text(r"\u5730\u533a")
COL_DEGREE = text(r"\u5b66\u5386")
COL_RETRIEVAL = text(r"\u68c0\u7d22\u5f97\u5206")
COL_SIMILARITY = text(r"\u539f\u59cb\u76f8\u4f3c\u5ea6")
COL_REASON = text(r"\u4e3a\u4ec0\u4e48\u5339\u914d")
COL_SOURCE = text(r"\u6765\u6e90")
COL_RELEVANCE = text(r"\u76f8\u5173\u7b49\u7ea7")
SEP_COLON = text(r"\uff1a")
UNKNOWN = text(r"\u672a\u586b\u5199")
DEFAULT_CAREER_TITLE = text(r"\u804c\u4e1a\u65b9\u5411")
MATCH_SCORE_LABEL = text(r"\u5339\u914d\u5206")


SCORE_FORMULA = [
    (text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"), 40, text(r"\u7531\u771f\u5b9e\u5c97\u4f4d\u5e93\u7684\u68c0\u7d22\u5f97\u5206\u6298\u7b97\uff0c\u4f53\u73b0\u5c97\u4f4d\u8bc1\u636e\u662f\u5426\u76f8\u5173\u3002")),
    (text(r"\u6280\u80fd\u5339\u914d\u5ea6"), 20, text(r"\u5bf9\u6bd4\u7528\u6237\u5df2\u638c\u63e1\u6280\u80fd\u4e0e\u5c97\u4f4d\u8981\u6c42\u4e2d\u7684\u6280\u80fd\u5173\u952e\u8bcd\u3002")),
    (text(r"\u57ce\u5e02\u5339\u914d\u5ea6"), 10, text(r"\u5224\u65ad\u5c97\u4f4d\u5730\u533a\u662f\u5426\u7b26\u5408\u671f\u671b\u57ce\u5e02\u6216\u533a\u57df\u504f\u597d\u3002")),
    (text(r"\u5b66\u5386\u5339\u914d\u5ea6"), 10, text(r"\u5224\u65ad\u7528\u6237\u5b66\u5386\u662f\u5426\u6ee1\u8db3\u5c97\u4f4d\u5b66\u5386\u8981\u6c42\u3002")),
    (text(r"\u884c\u4e1a\u504f\u597d\u5339\u914d\u5ea6"), 10, text(r"\u5bf9\u6bd4\u7528\u6237\u5174\u8da3\u884c\u4e1a\u4e0e\u5c97\u4f4d\u884c\u4e1a\u6216\u804c\u8d23\u63cf\u8ff0\u3002")),
    (text(r"\u5927\u6a21\u578b\u7efc\u5408\u8bc4\u4ef7"), 10, text(r"\u7531\u672c\u5730\u5927\u6a21\u578b\u7efc\u5408\u6280\u80fd\u3001\u7ecf\u5386\u548c\u53d1\u5c55\u7a7a\u95f4\u7ed9\u51fa\u89e3\u91ca\u6027\u8bc4\u4ef7\u3002")),
]


LEGACY_SCORE_NAMES = {
    "RAG妫€绱㈢浉浼煎害": SCORE_FORMULA[0][0],
    "鎶€鑳藉尮閰嶅害": SCORE_FORMULA[1][0],
    "鍩庡競鍖归厤搴?": SCORE_FORMULA[2][0],
    "瀛﹀巻鍖归厤搴?": SCORE_FORMULA[3][0],
    "琛屼笟鍋忓ソ鍖归厤搴?": SCORE_FORMULA[4][0],
    "澶фā鍨嬬患鍚堣瘎浠?": SCORE_FORMULA[5][0],
}


def build_profile_text(form: dict) -> str:
    return "\n".join(f"{key}{SEP_COLON}{value}" for key, value in form.items() if value)


def score_formula_rows() -> list[dict]:
    return [{COL_SCORE_ITEM: name, COL_WEIGHT: weight, COL_DESC: desc} for name, weight, desc in SCORE_FORMULA]


def score_caption(retrieval_score: int, llm_score: int) -> str:
    return (
        text(r"\u5339\u914d\u5206\u6570\u7531\u4e0b\u5217\u9879\u52a0\u6743\u5f97\u5230\uff1a")
        + text(r"\u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6 40% + \u6280\u80fd\u5339\u914d 20% + ")
        + text(r"\u57ce\u5e02\u5339\u914d 10% + \u5b66\u5386\u5339\u914d 10% + ")
        + text(r"\u884c\u4e1a\u504f\u597d 10% + \u5927\u6a21\u578b\u7efc\u5408\u8bc4\u4ef7 10%\u3002")
        + text(r"\u672c\u6b21\u68c0\u7d22\u5f97\u5206 ")
        + f"{retrieval_score}"
        + text(r"\uff0c\u5927\u6a21\u578b\u8bc4\u4ef7\u5f97\u5206 ")
        + f"{llm_score}"
        + text(r"\u3002")
    )


def data_source_rows(total_jobs: int | None = None) -> list[dict]:
    total = f"{total_jobs} " if total_jobs is not None else ""
    return [
        {
            COL_ITEM: text(r"\u6570\u636e\u6765\u6e90"),
            COL_DESC: text(r"NCSS \u56fd\u5bb6\u5927\u5b66\u751f\u5c31\u4e1a\u670d\u52a1\u5e73\u53f0\uff08https://www.ncss.cn\uff09\u5c97\u4f4d\u68c0\u7d22\u63a5\u53e3\u3002"),
        },
        {
            COL_ITEM: text(r"\u6570\u636e\u89c4\u6a21"),
            COL_DESC: total + text(r"\u6761\u771f\u5b9e\u5c97\u4f4d\u8bb0\u5f55\uff0c\u5305\u542b\u5c97\u4f4d\u540d\u79f0\u3001\u516c\u53f8\u3001\u5730\u533a\u3001\u5b66\u5386\u8981\u6c42\u3001\u4e13\u4e1a\u8981\u6c42\u548c\u6765\u6e90\u94fe\u63a5\u3002"),
        },
        {
            COL_ITEM: text(r"\u5904\u7406\u65b9\u5f0f"),
            COL_DESC: text(r"\u6309 job_id/source_url \u53bb\u91cd\uff0c\u8fc7\u6ee4\u4e71\u7801\u548c\u7a7a\u63cf\u8ff0\uff0c\u518d\u6784\u5efa RAG \u68c0\u7d22\u7d22\u5f15\u3002"),
        },
    ]


def detailed_score_caption(breakdown: dict) -> str:
    return (
        text(r"\u5339\u914d\u5206 ")
        + f"{breakdown.get('final_score', 0)}"
        + text(r" \u5206\uff1a\u7531\u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6\u3001\u6280\u80fd\u3001\u57ce\u5e02\u3001\u5b66\u5386\u3001\u884c\u4e1a\u504f\u597d\u548c\u5927\u6a21\u578b\u8bc4\u4ef7\u6309\u6743\u91cd\u76f8\u52a0\u5f97\u5230\u3002")
    )


def _score_name(name: object) -> str:
    return LEGACY_SCORE_NAMES.get(str(name), str(name))


def score_chart_rows(components: list[dict]) -> list[dict]:
    return [
        {
            COL_SCORE_ITEM: _score_name(item.get("name", "")),
            COL_RAW_SCORE: int(round(float(item.get("score", 0)))),
            COL_WEIGHT_PERCENT: int(round(float(item.get("weight", 0)) * 100)),
            COL_WEIGHTED: round(float(item.get("weighted", 0)), 2),
        }
        for item in components
    ]


def _single_line(value: str, limit: int = 140) -> str:
    text_value = text(r"\uff1b").join(part.strip() for part in str(value or "").splitlines() if part.strip())
    return text_value[:limit] + ("..." if len(text_value) > limit else "")


def _constraints_text(constraints: dict) -> str:
    labels = {
        "major": text(r"\u4e13\u4e1a"),
        "skills": text(r"\u6280\u80fd"),
        "city": text(r"\u57ce\u5e02"),
        "industry": text(r"\u884c\u4e1a/\u5174\u8da3"),
        "job_type": text(r"\u5c97\u4f4d\u7c7b\u578b"),
        "target_job_url": text(r"\u76ee\u6807\u5c97\u4f4d\u94fe\u63a5"),
    }
    parts = [f"{label}={constraints.get(key)}" for key, label in labels.items() if constraints.get(key)]
    return text(r"\uff1b").join(parts) if parts else text(r"\u672a\u586b\u5199\u660e\u786e\u7b5b\u9009\u6761\u4ef6")


def matching_process_rows(
    profile_text: str,
    constraints: dict,
    candidate_count: int,
    evidence_jobs: list[dict],
) -> list[dict]:
    return [
        {
            COL_STAGE: text(r"\u7528\u6237\u753b\u50cf"),
            COL_PROCESS: text(r"\u63d0\u53d6\u4e13\u4e1a\u3001\u6280\u80fd\u3001\u57ce\u5e02\u3001\u884c\u4e1a\u504f\u597d\u3001\u5c97\u4f4d\u7c7b\u578b\u548c\u76ee\u6807\u5c97\u4f4d\u8f93\u5165\u3002"),
            COL_EVIDENCE: _single_line(profile_text),
        },
        {
            COL_STAGE: text(r"RAG \u5c97\u4f4d\u53ec\u56de"),
            COL_PROCESS: text(r"\u4ece\u5c97\u4f4d\u5e93\u53ec\u56de ") + f"{candidate_count}" + text(r" \u6761\u5019\u9009\u5c97\u4f4d\u3002"),
            COL_EVIDENCE: _constraints_text(constraints),
        },
        {
            COL_STAGE: text(r"\u89c4\u5219\u8fc7\u6ee4"),
            COL_PROCESS: text(r"\u6309\u5c97\u4f4d\u7c7b\u578b\u3001\u9886\u57df\u5173\u952e\u8bcd\u548c\u57ce\u5e02\u504f\u597d\u8fc7\u6ee4\u4f4e\u76f8\u5173\u5c97\u4f4d\u3002"),
            COL_EVIDENCE: text(r"\u4fdd\u7559 ") + f"{len(evidence_jobs)}" + text(r" \u6761\u771f\u5b9e\u5c97\u4f4d\u6837\u4f8b\uff1b") + _constraints_text(constraints),
        },
        {
            COL_STAGE: text(r"\u89e3\u91ca\u6027\u8bc4\u5206"),
            COL_PROCESS: text(r"\u7efc\u5408 RAG \u68c0\u7d22\u5f97\u5206\u3001\u6280\u80fd\u3001\u57ce\u5e02\u3001\u5b66\u5386\u3001\u884c\u4e1a\u504f\u597d\u548c\u5927\u6a21\u578b\u8bc4\u4ef7\u3002"),
            COL_EVIDENCE: text(r"\u4e0b\u65b9\u8868\u683c\u5c55\u793a\u6bcf\u4e2a\u8bc4\u5206\u9879\u7684\u539f\u59cb\u5206\u3001\u6743\u91cd\u548c\u52a0\u6743\u5206\u3002"),
        },
    ]


def no_match_guidance_rows(constraints: dict, candidate_count: int) -> list[dict]:
    return [
        {
            COL_ITEM: text(r"\u63a8\u8350\u72b6\u6001"),
            COL_DESC: text(r"\u7cfb\u7edf\u6ca1\u6709\u751f\u6210\u63a8\u8350\uff0c\u662f\u4e3a\u4e86\u907f\u514d\u628a\u4f4e\u76f8\u5173\u5c97\u4f4d\u8bef\u5224\u4e3a\u5408\u9002\u5c97\u4f4d\u3002"),
            COL_ADVICE: text(r"\u672c\u6b21 RAG \u521d\u6b65\u53ec\u56de ") + f"{candidate_count}" + text(r" \u6761\u5019\u9009\uff0c\u4f46\u8fc7\u6ee4\u540e\u6ca1\u6709\u8db3\u591f\u76f8\u5173\u7684\u771f\u5b9e\u5c97\u4f4d\u8bc1\u636e\u3002"),
        },
        {
            COL_ITEM: text(r"\u57ce\u5e02\u6761\u4ef6"),
            COL_DESC: text(r"\u57ce\u5e02\u8fc7\u7a84\u4f1a\u51cf\u5c11\u5c97\u4f4d\u6837\u4f8b\u3002"),
            COL_ADVICE: text(r"\u5f53\u524d\u57ce\u5e02\uff1a") + f"{constraints.get('city') or UNKNOWN}" + text(r"\u3002\u53ef\u4ee5\u6539\u4e3a\u7701\u4efd\u3001\u5168\u56fd\uff0c\u6216\u5148\u7559\u7a7a\u3002"),
        },
        {
            COL_ITEM: text(r"\u5c97\u4f4d\u7c7b\u578b"),
            COL_DESC: text(r"\u5b9e\u4e60\u3001\u5168\u804c\u3001\u517c\u804c\u4f1a\u88ab\u533a\u5206\u3002"),
            COL_ADVICE: text(r"\u5f53\u524d\u5c97\u4f4d\u7c7b\u578b\uff1a") + f"{constraints.get('job_type') or UNKNOWN}" + text(r"\u3002\u53ef\u4ee5\u5207\u6362\u5c97\u4f4d\u7c7b\u578b\u540e\u91cd\u65b0\u68c0\u7d22\u3002"),
        },
        {
            COL_ITEM: text(r"\u65b9\u5411\u5173\u952e\u8bcd"),
            COL_DESC: text(r"\u7cfb\u7edf\u4f18\u5148\u4fdd\u8bc1\u804c\u4e1a\u65b9\u5411\u76f8\u5173\uff0c\u800c\u4e0d\u662f\u53ea\u5339\u914d\u57ce\u5e02\u6216\u901a\u7528\u6280\u80fd\u3002"),
            COL_ADVICE: text(r"\u5f53\u524d\u65b9\u5411\uff1a") + f"{constraints.get('industry') or constraints.get('major') or UNKNOWN}" + text(r"\u3002\u53ef\u4ee5\u6362\u6210\u66f4\u5e38\u89c1\u5c97\u4f4d\u540d\u79f0\uff0c\u5982\u6570\u636e\u5206\u6790\u3001\u8f6f\u4ef6\u5f00\u53d1\u3001\u8fd0\u8425\u7b49\u3002"),
        },
    ]


def _split_terms(value: object) -> list[str]:
    separators = [",", text(r"\uff0c"), text(r"\u3001"), ";", text(r"\uff1b"), "\n", " "]
    terms = [str(value or "")]
    for sep in separators:
        terms = [piece for term in terms for piece in term.split(sep)]
    return [term.strip() for term in terms if term.strip()]


def _job_search_text(job: dict) -> str:
    return " ".join(
        str(job.get(key, "") or "")
        for key in ("job_name", "company_name", "area_name", "degree_name", "major", "industry", "description", "document")
    ).lower()


def _matched_terms(terms: list[str], corpus: str) -> list[str]:
    return [term for term in terms if term.lower() in corpus]


def job_match_reason(job: dict, profile: dict) -> str:
    corpus = _job_search_text(job)
    skills = _split_terms(profile.get("skills", ""))
    matched_skills = _matched_terms(skills, corpus)
    missing_skills = [term for term in skills if term not in matched_skills]
    city_terms = _split_terms(profile.get("city", ""))
    degree_terms = _split_terms(profile.get("degree", ""))
    industry_terms = _split_terms(profile.get("industry", ""))

    parts: list[str] = []
    if matched_skills:
        parts.append(text(r"\u6280\u80fd\u547d\u4e2d\uff1a") + text(r"\u3001").join(matched_skills))
    if _matched_terms(city_terms, corpus):
        parts.append(text(r"\u57ce\u5e02\u547d\u4e2d\uff1a") + text(r"\u3001").join(_matched_terms(city_terms, corpus)))
    if _matched_terms(degree_terms, corpus):
        parts.append(text(r"\u5b66\u5386\u547d\u4e2d\uff1a") + text(r"\u3001").join(_matched_terms(degree_terms, corpus)))
    if _matched_terms(industry_terms, corpus):
        parts.append(text(r"\u884c\u4e1a\u547d\u4e2d\uff1a") + text(r"\u3001").join(_matched_terms(industry_terms, corpus)))
    if missing_skills:
        parts.append(text(r"\u672a\u547d\u4e2d\uff1a") + text(r"\u3001").join(missing_skills[:3]))
    return text(r"\uff1b").join(parts) if parts else text(r"\u4e3b\u8981\u7531 RAG \u68c0\u7d22\u76f8\u4f3c\u5ea6\u53ec\u56de\uff0c\u5efa\u8bae\u4eba\u5de5\u590d\u6838\u5c97\u4f4d\u8be6\u60c5\u3002")


def evidence_table_rows(evidence_jobs: list[dict], profile: dict | None = None) -> list[dict]:
    profile = profile or {}
    return [
        {
            COL_JOB_NAME: job.get("job_name", ""),
            COL_COMPANY: job.get("company_name", ""),
            COL_AREA: job.get("area_name", ""),
            COL_DEGREE: job.get("degree_name", ""),
            COL_RETRIEVAL: job.get("retrieval_score", 0),
            COL_RELEVANCE: job.get("relevance_level", ""),
            COL_SIMILARITY: round(float(job.get("similarity", 0)), 4),
            COL_REASON: job_match_reason(job, profile),
            COL_SOURCE: job.get("source_url", ""),
        }
        for job in evidence_jobs
    ]


LEARNING_ORDER = [
    ("1_week", text(r"1-2 \u5468")),
    ("2_weeks", text(r"3-4 \u5468")),
    ("1_month", text(r"5-6 \u5468")),
    ("3_months", text(r"7-8 \u5468")),
    ("6_months", text(r"7-8 \u5468")),
]


DEFAULT_LEARNING_PATH = {
    "1_week": {
        "goal": text(r"\u660e\u786e\u5c97\u4f4d\u5171\u6027\u8981\u6c42\uff0c\u8865\u9f50\u6700\u57fa\u7840\u7684\u5de5\u5177\u548c\u6982\u5ff5\u3002"),
        "tasks": [text(r"\u590d\u76d8 5 \u4e2a\u76f8\u5173\u5c97\u4f4d"), text(r"\u6574\u7406\u6280\u80fd\u7f3a\u53e3\u6e05\u5355"), text(r"\u8865\u4e00\u4e2a\u6838\u5fc3\u57fa\u7840\u70b9")],
        "deliverable": text(r"\u4e00\u4efd\u5c97\u4f4d\u5173\u952e\u8bcd\u8868\u548c\u6280\u80fd\u7f3a\u53e3\u6e05\u5355"),
    },
    "2_weeks": {
        "goal": text(r"\u505a\u51fa\u4e00\u4e2a\u80fd\u5bf9\u5e94\u5c97\u4f4d\u8981\u6c42\u7684\u5c0f\u9879\u76ee\u6216\u6848\u4f8b\u3002"),
        "tasks": [text(r"\u9009\u4e00\u4e2a\u5c97\u4f4d\u573a\u666f"), text(r"\u5b8c\u6210\u6700\u5c0f\u53ef\u6f14\u793a\u4f5c\u54c1"), text(r"\u8bb0\u5f55\u8fc7\u7a0b\u622a\u56fe")],
        "deliverable": text(r"\u4e00\u4e2a\u53ef\u5c55\u793a\u7684\u4f5c\u54c1\u6216\u9879\u76ee\u622a\u56fe"),
    },
    "1_month": {
        "goal": text(r"\u628a\u5b66\u4e60\u6210\u679c\u8f6c\u6210\u7b80\u5386\u548c\u9762\u8bd5\u8bc1\u636e\u3002"),
        "tasks": [text(r"\u6539\u5199\u7b80\u5386\u9879\u76ee\u6bb5"), text(r"\u51c6\u5907 2 \u5206\u949f\u9879\u76ee\u8bb2\u89e3"), text(r"\u5bf9\u7167\u5c97\u4f4d\u518d\u6295\u9012")],
        "deliverable": text(r"\u4e00\u7248\u5c97\u4f4d\u5b9a\u5236\u7b80\u5386\u548c\u9879\u76ee\u8bb2\u89e3\u7a3f"),
    },
    "3_months": {
        "goal": text(r"\u5b8c\u6210\u6295\u9012\u590d\u76d8\uff0c\u8c03\u6574\u4e0b\u4e00\u8f6e\u804c\u4e1a\u76ee\u6807\u3002"),
        "tasks": [text(r"\u8bb0\u5f55\u6295\u9012\u53cd\u9988"), text(r"\u8865\u9f50\u9ad8\u9891\u9762\u8bd5\u95ee\u9898"), text(r"\u4f18\u5316\u4f5c\u54c1\u96c6")],
        "deliverable": text(r"\u4e00\u4efd\u6295\u9012\u590d\u76d8\u8868\u548c\u4e0b\u8f6e\u884c\u52a8\u6e05\u5355"),
    },
}


def _learning_row(label: str, value: object) -> dict:
    if isinstance(value, dict):
        tasks = value.get("tasks", "")
        if isinstance(tasks, list):
            tasks = text(r"\uff1b").join(str(item) for item in tasks if item)
        return {
            COL_STAGE: label,
            COL_GOAL: str(value.get("goal", "") or value.get("target", "") or value.get(COL_GOAL, "")),
            COL_TASKS: str(tasks or value.get(COL_TASKS, "")),
            COL_DELIVERABLE: str(value.get("deliverable", "") or value.get("output", "") or value.get(COL_DELIVERABLE, "")),
        }
    return {COL_STAGE: label, COL_GOAL: str(value), COL_TASKS: "", COL_DELIVERABLE: ""}


def learning_path_rows(learning_path: object) -> list[dict]:
    if not isinstance(learning_path, dict):
        return [{COL_STAGE: text(r"\u5efa\u8bae"), COL_GOAL: str(learning_path), COL_TASKS: "", COL_DELIVERABLE: ""}] if learning_path else []
    source = learning_path or DEFAULT_LEARNING_PATH
    rows = []
    used: set[str] = set()
    labels_seen: set[str] = set()
    for key, label in LEARNING_ORDER:
        if key in source and source.get(key) and label not in labels_seen:
            rows.append(_learning_row(label, source[key]))
            labels_seen.add(label)
            used.add(key)
    rows.extend(_learning_row(str(key), value) for key, value in source.items() if key not in used and value)
    return rows


def _markdown_list(items: object) -> str:
    if isinstance(items, dict):
        return "\n".join(f"- {key}: {value}" for key, value in items.items())
    if isinstance(items, list):
        return "\n".join(f"- {item}" for item in items)
    return f"- {items}" if items else "- "


def build_markdown_report(
    profile_text: str,
    report: dict,
    evidence_jobs: list[dict],
    constraints: dict | None = None,
    candidate_count: int | None = None,
) -> str:
    process_rows = matching_process_rows(
        profile_text,
        constraints or {},
        len(evidence_jobs) if candidate_count is None else candidate_count,
        evidence_jobs,
    )
    lines = [
        text(r"# \u5927\u5b66\u751f\u804c\u4e1a\u5339\u914d\u4e0e\u53d1\u5c55\u5efa\u8bae\u62a5\u544a"),
        "",
        text(r"## \u4e00\u3001\u7528\u6237\u753b\u50cf\u6458\u8981"),
        "",
        "```text",
        profile_text,
        "```",
        "",
        text(r"\u751f\u6210\u6a21\u578b\uff1a") + str(report.get("model_used", "")),
        "",
        text(r"## \u4e8c\u3001\u6570\u636e\u6765\u6e90\u4e0e\u5904\u7406"),
        "",
        f"| {COL_ITEM} | {COL_DESC} |",
        "|---|---|",
    ]
    for row in data_source_rows():
        lines.append(f"| {row[COL_ITEM]} | {row[COL_DESC]} |")
    lines.extend(
        [
            "",
            text(r"## \u4e09\u3001\u5339\u914d\u8fc7\u7a0b\u8bf4\u660e"),
            "",
            f"| {COL_STAGE} | {COL_PROCESS} | {COL_EVIDENCE} |",
            "|---|---|---|",
        ]
    )
    for row in process_rows:
        lines.append(f"| {row[COL_STAGE]} | {row[COL_PROCESS]} | {row[COL_EVIDENCE]} |")
    lines.extend(["", text(r"## \u56db\u3001\u8bc4\u5206\u516c\u5f0f"), "", f"| {COL_SCORE_ITEM} | {COL_WEIGHT} | {COL_DESC} |", "|---|---:|---|"])
    for row in score_formula_rows():
        lines.append(f"| {row[COL_SCORE_ITEM]} | {row[COL_WEIGHT]}% | {row[COL_DESC]} |")
    lines.extend(["", text(r"## \u4e94\u3001\u63a8\u8350\u804c\u4e1a Top 3"), ""])
    for index, rec in enumerate(report.get("recommendations", []), start=1):
        rec_title = rec.get("title") or DEFAULT_CAREER_TITLE
        lines.extend(
            [
                f"### {index}. {rec_title} - {MATCH_SCORE_LABEL} {rec.get('final_score', 0)}",
                "",
                text(r"\u5339\u914d\u5206\u8bf4\u660e\uff1a") + str(rec.get("score_explanation", "")),
                "",
                text(r"\u63a8\u8350\u7406\u7531\uff1a") + str(rec.get("reason", "")),
                "",
                text(r"\u8bc4\u5206\u660e\u7ec6\uff1a"),
                "",
                f"| {COL_SCORE_ITEM} | {COL_RAW_SCORE} | {COL_WEIGHT_PERCENT} | {COL_WEIGHTED} |",
                "|---|---:|---:|---:|",
            ]
        )
        for row in score_chart_rows(rec.get("score_breakdown", [])):
            lines.append(f"| {row[COL_SCORE_ITEM]} | {row[COL_RAW_SCORE]} | {row[COL_WEIGHT_PERCENT]} | {row[COL_WEIGHTED]} |")
        lines.extend(
            [
                "",
                text(r"\u80fd\u529b\u77ed\u677f\uff1a"),
                _markdown_list(rec.get("gaps", [])),
                "",
                text(r"\u80fd\u529b\u63d0\u5347\u8ba1\u5212\uff1a"),
                "",
                f"| {COL_STAGE} | {COL_GOAL} | {COL_TASKS} | {COL_DELIVERABLE} |",
                "|---|---|---|---|",
            ]
        )
        for row in learning_path_rows(rec.get("learning_path", {})):
            lines.append(f"| {row[COL_STAGE]} | {row[COL_GOAL]} | {row[COL_TASKS]} | {row[COL_DELIVERABLE]} |")
        lines.extend(
            [
                "",
                text(r"\u7b80\u5386\u4f18\u5316\u5efa\u8bae\uff1a"),
                _markdown_list(rec.get("resume_advice", [])),
                "",
                text(r"\u5173\u8054\u5c97\u4f4d\u6837\u4f8b\uff1a"),
                _markdown_list(rec.get("reference_jobs", [])),
                "",
            ]
        )
    lines.extend(
        [
            text(r"## \u516d\u3001RAG \u68c0\u7d22\u5230\u7684\u771f\u5b9e\u5c97\u4f4d\u8bc1\u636e"),
            "",
            text(r"| \u5c97\u4f4d\u540d\u79f0 | \u516c\u53f8 | \u5730\u533a | \u5b66\u5386 | \u68c0\u7d22\u5f97\u5206 | \u539f\u59cb\u76f8\u4f3c\u5ea6 | \u4e3a\u4ec0\u4e48\u5339\u914d | \u6765\u6e90 |"),
            "|---|---|---|---|---:|---:|---|---|",
        ]
    )
    for row in evidence_table_rows(evidence_jobs[:10], constraints or {}):
        lines.append(
            "| "
            + f"{row[COL_JOB_NAME]} | {row[COL_COMPANY]} | "
            + f"{row[COL_AREA]} | {row[COL_DEGREE]} | "
            + f"{row[COL_RETRIEVAL]} | {float(row[COL_SIMILARITY]):.4f} | "
            + f"{row[COL_REASON]} | {row[COL_SOURCE]} |"
        )
    return "\n".join(lines).strip() + "\n"
