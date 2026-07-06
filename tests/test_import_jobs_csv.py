import json

from src.importers.import_jobs_csv import import_csv_jobs, merge_jsonl_files, normalize_csv_row


def test_normalize_csv_row_supports_chinese_headers_and_generates_id():
    row = {
        "岗位名称": "心理咨询实习生",
        "公司名称": "心桥咨询中心",
        "城市": "北京",
        "学历要求": "本科及以上",
        "专业要求": "心理学",
        "岗位类型": "实习",
        "行业": "心理咨询",
        "岗位描述": "协助心理咨询师完成来访者资料整理。",
        "岗位链接": "https://example.com/jobs/psy-1",
    }

    normalized = normalize_csv_row(row)

    assert normalized["job_id"].startswith("csv_")
    assert normalized["job_name"] == "心理咨询实习生"
    assert normalized["company_name"] == "心桥咨询中心"
    assert normalized["area_name"] == "北京"
    assert normalized["job_type"] == "实习"
    assert normalized["industry"] == "心理咨询"
    assert normalized["detail_status"] == "imported"
    assert normalized["source"] == "csv_import"


def test_normalize_csv_row_builds_description_when_missing():
    normalized = normalize_csv_row(
        {
            "job_name": "Education Consultant",
            "company_name": "Demo Edu",
            "area_name": "Guangzhou",
            "degree_name": "Bachelor",
            "major": "Education",
            "job_type": "full-time",
            "industry": "Education",
        }
    )

    assert "Education Consultant" in normalized["description"]
    assert "Guangzhou" in normalized["description"]
    assert "Education" in normalized["description"]


def test_import_csv_jobs_writes_jsonl(tmp_path):
    csv_path = tmp_path / "jobs.csv"
    output_path = tmp_path / "batch.jsonl"
    csv_path.write_text(
        "job_name,company_name,area_name,description,source_url\n"
        "User Researcher,UX Lab,Shanghai,Interview users,https://example.com/jobs/ux\n",
        encoding="utf-8",
    )

    count = import_csv_jobs(csv_path, output_path)

    assert count == 1
    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["job_name"] == "User Researcher"
    assert rows[0]["keyword"] == "csv_import"


def test_merge_jsonl_files_deduplicates_by_job_id(tmp_path):
    main = tmp_path / "main.jsonl"
    batch = tmp_path / "batch.jsonl"
    main.write_text(json.dumps({"job_id": "same", "job_name": "Old"}, ensure_ascii=False) + "\n", encoding="utf-8")
    batch.write_text(
        json.dumps({"job_id": "same", "job_name": "Duplicate"}, ensure_ascii=False)
        + "\n"
        + json.dumps({"job_id": "new", "job_name": "New"}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

    merged_count = merge_jsonl_files(main, batch)

    rows = [json.loads(line) for line in main.read_text(encoding="utf-8").splitlines()]
    assert merged_count == 2
    assert [row["job_name"] for row in rows] == ["Old", "New"]
