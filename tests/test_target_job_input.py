from src.inputs.target_job import (
    build_target_job_context,
    find_job_by_source_url,
    merge_target_job_with_evidence,
)


def test_build_target_job_context_combines_link_and_description():
    context = build_target_job_context(
        "https://www.ncss.cn/student/m/jobs/abc?from=copy",
        "岗位名称：Python数据分析实习生\n岗位要求：Python、SQL、Pandas",
    )

    assert context.has_content is True
    assert "目标岗位链接：https://www.ncss.cn/student/m/jobs/abc?from=copy" in context.text
    assert "目标岗位描述：岗位名称：Python数据分析实习生" in context.text
    assert "Python、SQL、Pandas" in context.search_text


def test_find_job_by_source_url_ignores_query_and_fragment():
    jobs = [
        {"job_name": "Java开发", "source_url": "https://www.ncss.cn/student/m/jobs/java"},
        {"job_name": "Python开发", "source_url": "https://www.ncss.cn/student/m/jobs/python"},
    ]

    matched = find_job_by_source_url(jobs, "https://www.ncss.cn/student/m/jobs/python?from=copy#top")

    assert matched["job_name"] == "Python开发"


def test_merge_target_job_with_evidence_prepends_target_and_removes_duplicate():
    target = {"job_name": "Python开发", "source_url": "https://example.com/job", "similarity": 0.31}
    evidence = [
        {"job_name": "Python开发", "source_url": "https://example.com/job", "similarity": 0.2},
        {"job_name": "数据分析", "source_url": "https://example.com/analyst", "similarity": 0.25},
    ]

    merged = merge_target_job_with_evidence(target, evidence, top_k=2)

    assert [job["job_name"] for job in merged] == ["Python开发", "数据分析"]
    assert merged[0]["target_job"] is True
    assert merged[0]["retrieval_score"] == 100
