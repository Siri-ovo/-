from src.ui.reporting import (
    build_profile_text,
    data_source_rows,
    evidence_table_rows,
    job_match_reason,
    learning_path_rows,
    matching_process_rows,
    no_match_guidance_rows,
    score_caption,
    score_formula_rows,
    text,
)


def test_build_profile_text_uses_readable_separator():
    profile = build_profile_text({text(r"\u4e13\u4e1a"): text(r"\u8f6f\u4ef6\u5de5\u7a0b"), text(r"\u6280\u80fd"): "Python"})
    assert profile == text(r"\u4e13\u4e1a\uff1a\u8f6f\u4ef6\u5de5\u7a0b\n\u6280\u80fd\uff1aPython")


def test_score_caption_explains_score_parts():
    caption = score_caption(retrieval_score=90, llm_score=85)

    assert text(r"\u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6 40%") in caption
    assert text(r"\u6280\u80fd\u5339\u914d 20%") in caption
    assert text(r"\u5927\u6a21\u578b\u7efc\u5408\u8bc4\u4ef7 10%") in caption


def test_score_formula_rows_explain_all_weighted_parts():
    rows = score_formula_rows()

    assert [row[text(r"\u8bc4\u5206\u9879")] for row in rows] == [
        text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"),
        text(r"\u6280\u80fd\u5339\u914d\u5ea6"),
        text(r"\u57ce\u5e02\u5339\u914d\u5ea6"),
        text(r"\u5b66\u5386\u5339\u914d\u5ea6"),
        text(r"\u884c\u4e1a\u504f\u597d\u5339\u914d\u5ea6"),
        text(r"\u5927\u6a21\u578b\u7efc\u5408\u8bc4\u4ef7"),
    ]
    assert sum(row[text(r"\u6743\u91cd")] for row in rows) == 100


def test_data_source_rows_describe_ncss_and_processing():
    rows = data_source_rows(total_jobs=4974)
    joined = "\n".join(row[text(r"\u8bf4\u660e")] for row in rows)

    assert "NCSS" in joined
    assert text(r"\u56fd\u5bb6\u5927\u5b66\u751f\u5c31\u4e1a\u670d\u52a1\u5e73\u53f0") in joined
    assert text(r"\u53bb\u91cd") in joined
    assert text(r"\u7d22\u5f15") in joined
    assert "4974" in joined


def test_job_match_reason_mentions_hits_and_gaps():
    reason = job_match_reason(
        {
            "job_name": text(r"Python\u6570\u636e\u5206\u6790\u5e08"),
            "area_name": text(r"\u5e7f\u5dde"),
            "degree_name": text(r"\u672c\u79d1\u53ca\u4ee5\u4e0a"),
            "industry": text(r"\u4eba\u5de5\u667a\u80fd"),
            "description": "Python SQL Pandas",
        },
        {
            "skills": "Python, SQL, Web",
            "city": text(r"\u5e7f\u5dde"),
            "degree": text(r"\u672c\u79d1"),
            "industry": text(r"\u4eba\u5de5\u667a\u80fd"),
        },
    )

    assert text(r"\u6280\u80fd\u547d\u4e2d\uff1aPython\u3001SQL") in reason
    assert text(r"\u57ce\u5e02\u547d\u4e2d\uff1a\u5e7f\u5dde") in reason
    assert text(r"\u672a\u547d\u4e2d\uff1aWeb") in reason


def test_evidence_table_rows_include_match_reason():
    rows = evidence_table_rows(
        [
            {
                "job_name": text(r"Python\u6570\u636e\u5206\u6790\u5e08"),
                "company_name": "Demo",
                "area_name": text(r"\u5e7f\u5dde"),
                "degree_name": text(r"\u672c\u79d1"),
                "retrieval_score": 88,
                "relevance_level": text(r"\u9ad8"),
                "similarity": 0.22,
                "source_url": "https://www.ncss.cn/student/m/jobs/abc",
                "description": "Python SQL",
            }
        ],
        {"skills": "Python, SQL", "city": text(r"\u5e7f\u5dde")},
    )

    assert rows[0][text(r"\u4e3a\u4ec0\u4e48\u5339\u914d")].startswith(text(r"\u6280\u80fd\u547d\u4e2d"))


def test_matching_process_rows_explain_rag_and_scoring():
    rows = matching_process_rows(
        profile_text=text(r"\u4e13\u4e1a\uff1a\u8f6f\u4ef6\u5de5\u7a0b\n\u6280\u80fd\uff1aPython"),
        constraints={
            "city": text(r"\u5e7f\u5dde"),
            "job_type": text(r"\u5168\u804c"),
            "industry": text(r"\u4eba\u5de5\u667a\u80fd"),
            "target_job_url": "https://www.ncss.cn/student/m/jobs/abc",
        },
        candidate_count=100,
        evidence_jobs=[{"job_name": text(r"Python\u5f00\u53d1\u5de5\u7a0b\u5e08")}],
    )

    assert rows[0][text(r"\u9636\u6bb5")] == text(r"\u7528\u6237\u753b\u50cf")
    assert text(r"\u8f6f\u4ef6\u5de5\u7a0b") in rows[0][text(r"\u9875\u9762\u8bc1\u636e")]
    assert rows[1][text(r"\u9636\u6bb5")] == text(r"RAG \u5c97\u4f4d\u53ec\u56de")
    assert "100" in rows[1][text(r"\u7cfb\u7edf\u5904\u7406")]
    assert text(r"\u76ee\u6807\u5c97\u4f4d\u94fe\u63a5") in rows[1][text(r"\u9875\u9762\u8bc1\u636e")]
    assert rows[2][text(r"\u9636\u6bb5")] == text(r"\u89c4\u5219\u8fc7\u6ee4")
    assert text(r"\u5168\u804c") in rows[2][text(r"\u9875\u9762\u8bc1\u636e")]
    assert rows[3][text(r"\u9636\u6bb5")] == text(r"\u89e3\u91ca\u6027\u8bc4\u5206")


def test_no_match_guidance_rows_explain_rejection_and_next_steps():
    rows = no_match_guidance_rows(
        constraints={"city": text(r"\u5317\u4eac"), "job_type": text(r"\u5b9e\u4e60"), "industry": text(r"\u5fc3\u7406\u54a8\u8be2")},
        candidate_count=100,
    )

    assert rows[0][text(r"\u8bf4\u660e")] == text(
        r"\u7cfb\u7edf\u6ca1\u6709\u751f\u6210\u63a8\u8350\uff0c"
        r"\u662f\u4e3a\u4e86\u907f\u514d\u628a\u4f4e\u76f8\u5173\u5c97\u4f4d\u8bef\u5224\u4e3a\u5408\u9002\u5c97\u4f4d\u3002"
    )
    assert any("100" in row[text(r"\u5efa\u8bae")] for row in rows)
    assert any(text(r"\u5fc3\u7406\u54a8\u8be2") in row[text(r"\u5efa\u8bae")] for row in rows)


def test_learning_path_rows_orders_short_periods():
    rows = learning_path_rows(
        {
            "2_weeks": text(r"\u505a\u9879\u76ee"),
            "1_week": text(r"\u8865\u57fa\u7840"),
            "1_month": text(r"\u6295\u9012"),
        }
    )

    assert rows == [
        {text(r"\u9636\u6bb5"): text(r"1-2 \u5468"), text(r"\u9636\u6bb5\u76ee\u6807"): text(r"\u8865\u57fa\u7840"), text(r"\u5177\u4f53\u4efb\u52a1"): "", text(r"\u53ef\u4ea4\u4ed8\u6210\u679c"): ""},
        {text(r"\u9636\u6bb5"): text(r"3-4 \u5468"), text(r"\u9636\u6bb5\u76ee\u6807"): text(r"\u505a\u9879\u76ee"), text(r"\u5177\u4f53\u4efb\u52a1"): "", text(r"\u53ef\u4ea4\u4ed8\u6210\u679c"): ""},
        {text(r"\u9636\u6bb5"): text(r"5-6 \u5468"), text(r"\u9636\u6bb5\u76ee\u6807"): text(r"\u6295\u9012"), text(r"\u5177\u4f53\u4efb\u52a1"): "", text(r"\u53ef\u4ea4\u4ed8\u6210\u679c"): ""},
    ]


def test_learning_path_rows_supports_goal_tasks_and_deliverable():
    rows = learning_path_rows(
        {
            "1_week": {
                "goal": text(r"\u8865\u9f50\u6570\u636e\u5206\u6790\u57fa\u7840"),
                "tasks": [text(r"\u590d\u4e60 SQL"), text(r"\u5b8c\u6210 Pandas \u7ec3\u4e60")],
                "deliverable": text(r"\u4e00\u4efd\u6570\u636e\u6e05\u6d17\u7b14\u8bb0"),
            }
        }
    )

    assert rows == [
        {
            text(r"\u9636\u6bb5"): text(r"1-2 \u5468"),
            text(r"\u9636\u6bb5\u76ee\u6807"): text(r"\u8865\u9f50\u6570\u636e\u5206\u6790\u57fa\u7840"),
            text(r"\u5177\u4f53\u4efb\u52a1"): text(r"\u590d\u4e60 SQL\uff1b\u5b8c\u6210 Pandas \u7ec3\u4e60"),
            text(r"\u53ef\u4ea4\u4ed8\u6210\u679c"): text(r"\u4e00\u4efd\u6570\u636e\u6e05\u6d17\u7b14\u8bb0"),
        }
    ]


def test_learning_path_rows_fills_four_practical_stages_when_empty():
    rows = learning_path_rows({})

    assert [row[text(r"\u9636\u6bb5")] for row in rows] == [
        text(r"1-2 \u5468"),
        text(r"3-4 \u5468"),
        text(r"5-6 \u5468"),
        text(r"7-8 \u5468"),
    ]
    assert all(row[text(r"\u53ef\u4ea4\u4ed8\u6210\u679c")] for row in rows)
