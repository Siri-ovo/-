from src.crawler.clean_jobs import clean_record


def test_clean_record_filters_empty_description():
    assert clean_record({"job_id": "1", "description": "   "}) is None


def test_clean_record_keeps_required_fields():
    record = {
        "job_id": "1",
        "job_name": "前端开发工程师",
        "company_name": "某公司",
        "description": "<p>熟悉 Vue 和 JavaScript</p>",
    }
    cleaned = clean_record(record)
    assert cleaned["description"] == "熟悉 Vue 和 JavaScript"
    assert cleaned["job_name"] == "前端开发工程师"
