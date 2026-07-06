from src.scoring.match_score import (
    clamp_score,
    retrieval_score_from_similarity,
    score_for_reference_jobs,
)
from src.ui.reporting import text


def test_clamp_score_bounds_values():
    assert clamp_score(-5) == 0
    assert clamp_score(120) == 100
    assert clamp_score(88.6) == 89


def test_retrieval_score_from_similarity_normalizes_cosine_similarity():
    assert retrieval_score_from_similarity(0.91) == 91
    assert retrieval_score_from_similarity(1.2) == 100
    assert retrieval_score_from_similarity(-0.2) == 0


def test_score_for_reference_jobs_uses_matched_jobs():
    evidence = [
        {"job_name": text(r"AI\u5e94\u7528\u5f00\u53d1\u5de5\u7a0b\u5e08"), "similarity": 0.9},
        {"job_name": text(r"\u6570\u636e\u5206\u6790\u5e08"), "similarity": 0.7},
    ]
    assert score_for_reference_jobs([text(r"AI\u5e94\u7528\u5f00\u53d1\u5de5\u7a0b\u5e08")], evidence) == 90
