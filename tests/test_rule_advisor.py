from src.llm.rule_advisor import build_rule_based_report


def test_build_rule_based_report_uses_top_evidence_jobs():
    report = build_rule_based_report(
        profile_text="skills: Python SQL",
        evidence_jobs=[
            {
                "job_name": "Data Analyst",
                "company_name": "Demo Tech",
                "similarity": 0.82,
                "description": "Python SQL dashboard",
            },
            {
                "job_name": "Backend Engineer",
                "company_name": "API Ltd",
                "similarity": 0.72,
                "description": "Java API",
            },
        ],
        failure_reason="model timeout",
    )

    assert report["fallback_reason"] == "model timeout"
    assert report["recommendations"][0]["title"] == "Data Analyst"
    assert report["recommendations"][0]["llm_score"] == 65
    assert report["recommendations"][0]["reference_jobs"] == ["Data Analyst"]
    assert "规则兜底" in report["recommendations"][0]["reason"]
