from src.analytics.job_dashboard import summarize_jobs


def test_summarize_jobs_counts_total_city_degree_and_keywords():
    jobs = [
        {
            "job_name": "Python Developer",
            "area_name": "Guangzhou",
            "degree_name": "Bachelor",
            "keyword": "Python",
            "update_date": "2026-07-01",
        },
        {
            "job_name": "Data Analyst",
            "area_name": "Shenzhen",
            "degree_name": "Bachelor",
            "keyword": "SQL",
            "update_date": "2026-07-02",
        },
        {
            "job_name": "Python Engineer",
            "area_name": "Guangzhou",
            "degree_name": "Master",
            "keyword": "Python",
            "update_date": "2026-06-30",
        },
    ]

    summary = summarize_jobs(jobs, top_n=2)

    assert summary["total_jobs"] == 3
    assert summary["latest_update"] == "2026-07-02"
    assert summary["city_distribution"] == [
        {"name": "Guangzhou", "count": 2},
        {"name": "Shenzhen", "count": 1},
    ]
    assert summary["degree_distribution"][0] == {"name": "Bachelor", "count": 2}
    assert summary["keyword_distribution"][0] == {"name": "Python", "count": 2}
