from src.scoring.match_score import build_score_breakdown, score_profile_match
from src.ui.reporting import text


def test_build_score_breakdown_uses_explainable_weights():
    breakdown = build_score_breakdown(
        retrieval_score=80,
        skill_score=90,
        city_score=100,
        degree_score=60,
        industry_score=70,
        llm_score=85,
    )

    assert breakdown["final_score"] == 82
    assert breakdown["components"] == [
        {"name": text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"), "score": 80, "weight": 0.4, "weighted": 32.0},
        {"name": text(r"\u6280\u80fd\u5339\u914d\u5ea6"), "score": 90, "weight": 0.2, "weighted": 18.0},
        {"name": text(r"\u57ce\u5e02\u5339\u914d\u5ea6"), "score": 100, "weight": 0.1, "weighted": 10.0},
        {"name": text(r"\u5b66\u5386\u5339\u914d\u5ea6"), "score": 60, "weight": 0.1, "weighted": 6.0},
        {"name": text(r"\u884c\u4e1a\u504f\u597d\u5339\u914d\u5ea6"), "score": 70, "weight": 0.1, "weighted": 7.0},
        {"name": text(r"\u5927\u6a21\u578b\u7efc\u5408\u8bc4\u4ef7"), "score": 85, "weight": 0.1, "weighted": 8.5},
    ]


def test_score_profile_match_scores_field_matches_against_evidence():
    form = {
        "skills": "Python, SQL",
        "city": "Guangzhou",
        "degree": "Bachelor",
        "industry": "AI",
    }
    recommendation = {
        "title": "AI Data Analyst",
        "reason": "Use Python and SQL for analytics.",
        "llm_score": 80,
        "reference_jobs": ["AI Data Analyst"],
    }
    evidence_jobs = [
        {
            "job_name": "AI Data Analyst",
            "area_name": "Guangzhou",
            "degree_name": "Bachelor",
            "industry": "AI",
            "description": "Python SQL analytics",
            "similarity": 0.75,
        }
    ]

    breakdown = score_profile_match(form, recommendation, evidence_jobs)

    assert breakdown["final_score"] == 88
    assert {item["name"]: item["score"] for item in breakdown["components"]} == {
        text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"): 75,
        text(r"\u6280\u80fd\u5339\u914d\u5ea6"): 100,
        text(r"\u57ce\u5e02\u5339\u914d\u5ea6"): 100,
        text(r"\u5b66\u5386\u5339\u914d\u5ea6"): 100,
        text(r"\u884c\u4e1a\u504f\u597d\u5339\u914d\u5ea6"): 100,
        text(r"\u5927\u6a21\u578b\u7efc\u5408\u8bc4\u4ef7"): 80,
    }
