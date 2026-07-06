import pytest

from src.llm.career_advisor import build_prompt, parse_advisor_response


def test_build_prompt_includes_evidence_scoring_rule_and_short_learning_path():
    prompt = build_prompt(
        profile_text="major: software engineering\nskills: Python",
        evidence_jobs=[{"job_name": "AI App Engineer", "similarity": 0.9}],
    )

    assert "RAG job retrieval relevance 40%" in prompt
    assert "skill match 20%" in prompt
    assert "Keep the plan within 8 weeks" in prompt
    assert "AI App Engineer" in prompt
    assert "Do not invent job examples" in prompt
    assert '"goal"' in prompt
    assert '"tasks"' in prompt
    assert '"deliverable"' in prompt
    assert "2-3 practical tasks" in prompt
    assert '"1_week"' in prompt
    assert '"2_weeks"' in prompt
    assert '"1_month"' in prompt
    assert '"3_months"' in prompt
    assert '"6_months"' not in prompt


def test_parse_advisor_response_extracts_balanced_json():
    text = 'prefix {"recommendations":[{"title":"Data Analyst","llm_score":80}]} suffix {"bad":true}'

    parsed = parse_advisor_response(text)

    assert parsed["recommendations"][0]["title"] == "Data Analyst"
    assert parsed["recommendations"][0]["llm_score"] == 80


def test_parse_advisor_response_rejects_invalid_json():
    with pytest.raises(ValueError):
        parse_advisor_response("no JSON")
