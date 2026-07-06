from src.ui.reporting import detailed_score_caption, score_chart_rows, text


def test_score_chart_rows_returns_weighted_component_rows():
    rows = score_chart_rows(
        [
            {text(r"name"): text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"), "score": 80, "weight": 0.4, "weighted": 32.0},
            {text(r"name"): text(r"\u6280\u80fd\u5339\u914d\u5ea6"), "score": 90, "weight": 0.2, "weighted": 18.0},
        ]
    )

    assert rows == [
        {text(r"\u8bc4\u5206\u9879"): text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"), text(r"\u539f\u59cb\u5206"): 80, text(r"\u6743\u91cd(%)"): 40, text(r"\u52a0\u6743\u5206"): 32.0},
        {text(r"\u8bc4\u5206\u9879"): text(r"\u6280\u80fd\u5339\u914d\u5ea6"), text(r"\u539f\u59cb\u5206"): 90, text(r"\u6743\u91cd(%)"): 20, text(r"\u52a0\u6743\u5206"): 18.0},
    ]


def test_detailed_score_caption_is_readable_summary():
    caption = detailed_score_caption(
        {
            "final_score": 82,
            "components": [
                {text(r"name"): text(r"RAG \u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6"), "score": 80, "weight": 0.4, "weighted": 32.0},
                {text(r"name"): text(r"\u6280\u80fd\u5339\u914d\u5ea6"), "score": 90, "weight": 0.2, "weighted": 18.0},
            ],
        }
    )

    assert caption == text(
        r"\u5339\u914d\u5206 82 \u5206\uff1a"
        r"\u7531\u5c97\u4f4d\u68c0\u7d22\u76f8\u5173\u5ea6\u3001\u6280\u80fd\u3001\u57ce\u5e02\u3001"
        r"\u5b66\u5386\u3001\u884c\u4e1a\u504f\u597d\u548c\u5927\u6a21\u578b\u8bc4\u4ef7\u6309\u6743\u91cd\u76f8\u52a0\u5f97\u5230\u3002"
    )
