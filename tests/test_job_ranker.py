from src.rag.job_ranker import filter_and_rank_jobs, normalized_retrieval_score, relevance_level


def test_normalized_retrieval_score_maps_tfidf_range_to_user_score():
    assert normalized_retrieval_score(0.25) == 100
    assert normalized_retrieval_score(0.125) == 50
    assert normalized_retrieval_score(0.0) == 0


def test_relevance_level_labels_normalized_score():
    assert relevance_level(85) == "高"
    assert relevance_level(55) == "中"
    assert relevance_level(20) == "低"


def test_filter_and_rank_jobs_filters_job_type_and_prefers_domain_terms():
    jobs = [
        {
            "job_name": "Frontend Developer",
            "area_name": "Shanghai",
            "job_type": "full-time",
            "description": "frontend",
            "similarity": 0.2,
        },
        {
            "job_name": "Psychology Intern",
            "area_name": "Shanghai",
            "job_type": "intern",
            "description": "psychology assistant intern",
            "similarity": 0.12,
        },
        {
            "job_name": "AI Intern",
            "area_name": "Beijing",
            "job_type": "intern",
            "description": "AI data",
            "similarity": 0.1,
        },
    ]
    constraints = {
        "job_type": "intern",
        "city": "Beijing",
        "industry": "psychology",
        "major": "psychology",
        "skills": "psychology",
    }

    ranked = filter_and_rank_jobs(jobs, constraints, top_k=3)

    assert [job["job_name"] for job in ranked] == ["Psychology Intern"]
    assert ranked[0]["retrieval_score"] == 48
    assert ranked[0]["domain_score"] > 0


def test_filter_and_rank_jobs_filters_chinese_job_type():
    jobs = [
        {
            "job_name": "Python开发实习生",
            "area_name": "广州",
            "job_type": "实习",
            "description": "Python 数据分析",
            "similarity": 0.2,
        },
        {
            "job_name": "Python开发工程师",
            "area_name": "广州",
            "job_type": "全职",
            "description": "Python 数据分析",
            "similarity": 0.12,
        },
    ]

    ranked = filter_and_rank_jobs(
        jobs,
        {"job_type": "全职", "city": "广州", "industry": "数据分析", "major": "", "skills": "Python"},
        top_k=2,
    )

    assert [job["job_name"] for job in ranked] == ["Python开发工程师"]


def test_filter_and_rank_jobs_prioritizes_requested_city_without_hardcoding_city():
    jobs = [
        {
            "job_name": "Psychology Intern Shanghai",
            "area_name": "Shanghai",
            "job_type": "intern",
            "description": "psychology assistant intern",
            "similarity": 0.18,
        },
        {
            "job_name": "Psychology Intern Guangzhou",
            "area_name": "Guangzhou",
            "job_type": "intern",
            "description": "psychology assistant intern",
            "similarity": 0.16,
        },
    ]

    ranked = filter_and_rank_jobs(
        jobs,
        {
            "job_type": "intern",
            "city": "Guangzhou",
            "industry": "psychology",
            "major": "psychology",
            "skills": "psychology",
        },
        top_k=2,
    )

    assert ranked[0]["job_name"] == "Psychology Intern Guangzhou"


def test_filter_and_rank_jobs_does_not_treat_crawl_keyword_as_domain_match():
    jobs = [
        {
            "job_name": "General Assistant",
            "area_name": "Guangdong",
            "job_type": "intern",
            "keyword": "psychology",
            "detail_status": "list_only",
            "description": "Job: General Assistant crawl keyword psychology",
            "similarity": 0.2,
        },
        {
            "job_name": "Psychology Assistant Intern",
            "area_name": "Guangdong",
            "job_type": "intern",
            "keyword": "general",
            "description": "psychology counseling support",
            "similarity": 0.1,
        },
    ]

    ranked = filter_and_rank_jobs(
        jobs,
        {"job_type": "intern", "major": "psychology", "industry": "psychology", "skills": ""},
        top_k=2,
    )

    assert ranked[0]["job_name"] == "Psychology Assistant Intern"
    assert len(ranked) == 1


def test_filter_and_rank_jobs_returns_empty_when_requested_job_type_has_no_matches():
    ranked = filter_and_rank_jobs(
        [{"job_name": "Full Time Analyst", "job_type": "full-time", "description": "analyst", "similarity": 0.3}],
        {"job_type": "intern", "major": "psychology"},
        top_k=2,
    )

    assert ranked == []


def test_filter_and_rank_jobs_returns_empty_when_domain_terms_do_not_match_any_job():
    ranked = filter_and_rank_jobs(
        [
            {
                "job_name": "General Assistant",
                "job_type": "intern",
                "description": "office support",
                "similarity": 0.3,
            }
        ],
        {"job_type": "intern", "major": "psychology", "industry": "counseling", "skills": ""},
        top_k=2,
    )

    assert ranked == []


def test_filter_and_rank_jobs_does_not_keep_jobs_only_matching_city_or_job_type():
    ranked = filter_and_rank_jobs(
        [
            {
                "job_name": "北京运营实习生",
                "area_name": "北京",
                "job_type": "实习",
                "description": "用户运营 内容运营",
                "similarity": 0.3,
            }
        ],
        {"job_type": "实习", "city": "北京", "major": "心理", "industry": "心理咨询", "skills": ""},
        top_k=2,
    )

    assert ranked == []


def test_filter_and_rank_jobs_does_not_keep_jobs_only_matching_broad_major_when_interest_is_specific():
    ranked = filter_and_rank_jobs(
        [
            {
                "job_name": "用户运营实习生",
                "area_name": "北京",
                "job_type": "实习",
                "description": "分析用户心理，负责内容运营",
                "similarity": 0.3,
            }
        ],
        {"job_type": "实习", "city": "北京", "major": "心理", "industry": "心理咨询 心理医生", "skills": ""},
        top_k=2,
    )

    assert ranked == []


def test_filter_and_rank_jobs_does_not_let_generic_skill_override_specific_interest():
    ranked = filter_and_rank_jobs(
        [
            {
                "job_name": "前端开发实习生",
                "area_name": "上海",
                "job_type": "实习",
                "description": "英语四级优先，熟悉 Web 开发",
                "similarity": 0.3,
            }
        ],
        {"job_type": "实习", "city": "北京", "major": "心理", "industry": "心理咨询 心理医生", "skills": "英语四级"},
        top_k=2,
    )

    assert ranked == []
