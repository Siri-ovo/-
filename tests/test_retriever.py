from src.rag.retriever import job_to_document_text, normalize_similarity


def test_job_to_document_text_contains_key_fields():
    job = {
        "job_name": "数据分析师",
        "company_name": "某科技公司",
        "area_name": "广州",
        "degree_name": "本科及以上",
        "major": "统计学 计算机",
        "description": "负责 SQL 数据分析",
    }
    text = job_to_document_text(job)
    assert "岗位：数据分析师" in text
    assert "地区：广州" in text
    assert "负责 SQL 数据分析" in text


def test_normalize_similarity():
    assert normalize_similarity(0.9) == 0.9
    assert normalize_similarity(1.2) == 1.0
    assert normalize_similarity(-0.2) == 0.0
