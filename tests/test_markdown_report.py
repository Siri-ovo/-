from src.ui.reporting import build_markdown_report, text


def test_build_markdown_report_contains_profile_scores_formula_and_evidence():
    report = {
        "model_used": "qwen3:4b",
        "recommendations": [
            {
                "title": "Data Analyst",
                "final_score": 82,
                "score_explanation": text(r"\u5339\u914d\u5206 82 \u5206"),
                "score_breakdown": [
                    {"name": text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"), "score": 80, "weight": 0.4, "weighted": 32.0},
                    {"name": text(r"\u6280\u80fd\u5339\u914d\u5ea6"), "score": 90, "weight": 0.2, "weighted": 18.0},
                ],
                "reason": "Matches Python and SQL.",
                "gaps": ["statistics"],
                "learning_path": {
                    "1_week": {
                        "goal": text(r"\u8865\u9f50\u6570\u636e\u5206\u6790\u57fa\u7840"),
                        "tasks": [text(r"\u590d\u4e60 SQL"), text(r"\u5b8c\u6210 Pandas \u7ec3\u4e60")],
                        "deliverable": text(r"\u4e00\u4efd\u6570\u636e\u6e05\u6d17\u7b14\u8bb0"),
                    },
                    "2_weeks": "BI",
                },
                "resume_advice": ["Add projects"],
                "reference_jobs": ["Data Analyst Intern"],
            }
        ],
    }
    evidence_jobs = [
        {
            "job_name": "Data Analyst Intern",
            "company_name": "Demo Tech",
            "area_name": "Guangzhou",
            "degree_name": "Bachelor",
            "retrieval_score": 88,
            "similarity": 0.72,
            "source_url": "https://example.com/job",
            "description": "Python SQL",
        }
    ]

    markdown = build_markdown_report(
        "major: software\nskills: Python",
        report,
        evidence_jobs,
        constraints={"skills": "Python, SQL", "city": "Guangzhou"},
    )

    assert text(r"# \u5927\u5b66\u751f\u804c\u4e1a\u5339\u914d\u4e0e\u53d1\u5c55\u5efa\u8bae\u62a5\u544a") in markdown
    assert text(r"## \u4e8c\u3001\u6570\u636e\u6765\u6e90\u4e0e\u5904\u7406") in markdown
    assert "NCSS" in markdown
    assert text(r"## \u56db\u3001\u8bc4\u5206\u516c\u5f0f") in markdown
    assert text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6") in markdown
    assert "major: software" in markdown
    assert "Data Analyst - " + text(r"\u5339\u914d\u5206") + " 82" in markdown
    assert text(r"\u8bc4\u5206\u660e\u7ec6") in markdown
    assert text(r"\u52a0\u6743\u5206") in markdown
    assert text(r"\u80fd\u529b\u77ed\u677f") in markdown
    assert text(r"\u80fd\u529b\u63d0\u5347\u8ba1\u5212") in markdown
    assert text(r"1-2 \u5468") in markdown
    assert text(r"3-4 \u5468") in markdown
    assert text(r"\u9636\u6bb5\u76ee\u6807") in markdown
    assert text(r"\u590d\u4e60 SQL\uff1b\u5b8c\u6210 Pandas \u7ec3\u4e60") in markdown
    assert text(r"\u4e00\u4efd\u6570\u636e\u6e05\u6d17\u7b14\u8bb0") in markdown
    assert text(r"\u4e3a\u4ec0\u4e48\u5339\u914d") in markdown
    assert "Data Analyst Intern" in markdown
    assert "https://example.com/job" in markdown
