from pathlib import Path

import pytest
import requests

from src.crawler import ncss_crawler
from src.crawler.ncss_crawler import build_detail_url, build_list_description, crawl_keywords, parse_detail_html, parse_list_item


def test_build_detail_url():
    assert build_detail_url("abc123") == "https://www.ncss.cn/student/m/jobs/abc123/detail.html"


def test_fetch_list_handles_null_data_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": None}

    class FakeSession:
        def get(self, *args, **kwargs):
            return FakeResponse()

    assert ncss_crawler.fetch_list(FakeSession(), "不存在的岗位", offset=1, limit=20) == []


def test_parse_list_item_maps_fields():
    item = {
        "jobId": "job1",
        "jobName": "数据分析师",
        "corpName": "某科技公司",
        "areaName": "广东",
        "lowMonthPay": 8.0,
        "highMonthPay": 12.0,
        "degreeName": "本科及以上",
        "major": "统计学 计算机",
        "property": "民营企业",
        "corpScale": "100-499人",
        "updateDate": "2026-07-01",
    }
    parsed = parse_list_item(item, keyword="数据分析")
    assert parsed["job_id"] == "job1"
    assert parsed["job_name"] == "数据分析师"
    assert parsed["salary_low"] == 8.0
    assert parsed["source_url"].endswith("/job1/detail.html")


def test_parse_detail_html_extracts_embedded_description():
    html = '''
    <script>
    var data = {"job":{"description":"岗位职责\\n熟悉 Python 和 SQL","jobType":"全职"},"company":{"primaryIndustry":"计算机软件"}};
    </script>
    '''
    parsed = parse_detail_html(html)
    assert parsed["description"] == "岗位职责 熟悉 Python 和 SQL"
    assert parsed["job_type"] == "全职"
    assert parsed["industry"] == "计算机软件"


def test_parse_detail_html_handles_missing_data():
    parsed = parse_detail_html("<html>404</html>")
    assert parsed == {"description": "", "job_type": "", "industry": ""}


def test_build_list_description_keeps_structured_fields_searchable():
    record = {
        "job_name": "Python Developer",
        "company_name": "Demo Tech",
        "area_name": "Guangzhou",
        "degree_name": "Bachelor",
        "major": "Computer Science",
        "salary_low": 8,
        "salary_high": 12,
        "keyword": "Python",
    }

    description = build_list_description(record)

    assert "Python Developer" in description
    assert "Guangzhou" in description
    assert "Bachelor" in description
    assert "Computer Science" in description


def test_crawl_keywords_can_keep_list_items_without_detail_requests(tmp_path, monkeypatch):
    output = tmp_path / "jobs.jsonl"
    detail_called = False

    def fake_fetch_list(session, keyword, offset, limit):
        if offset > 1:
            return []
        return [
            {
                "jobId": "job-list-1",
                "jobName": "List Only Developer",
                "corpName": "Demo Tech",
                "areaName": "Guangzhou",
                "degreeName": "Bachelor",
                "major": "Software",
            }
        ]

    def fake_fetch_detail(session, job_id):
        nonlocal detail_called
        detail_called = True
        raise AssertionError("detail should not be called when fetch_details is False")

    monkeypatch.setattr(ncss_crawler, "fetch_list", fake_fetch_list)
    monkeypatch.setattr(ncss_crawler, "fetch_detail", fake_fetch_detail)

    count = crawl_keywords(["Python"], pages=2, limit=10, output_path=output, delay=0, fetch_details=False)

    assert count == 1
    assert detail_called is False
    text = output.read_text(encoding="utf-8")
    assert "List Only Developer" in text
    assert "list_only" in text


def test_crawl_keywords_skips_server_error_keyword(tmp_path, monkeypatch):
    output = tmp_path / "jobs.jsonl"
    calls = []

    def make_http_error(status_code: int):
        response = requests.Response()
        response.status_code = status_code
        return requests.HTTPError(response=response)

    def fake_fetch_list(session, keyword, offset, limit):
        calls.append((keyword, offset))
        if keyword == "bad":
            raise make_http_error(500)
        if offset > 1:
            return []
        return [
            {
                "jobId": f"{keyword}-1",
                "jobName": f"{keyword} Developer",
                "corpName": "Demo Tech",
                "areaName": "Guangzhou",
            }
        ]

    monkeypatch.setattr(ncss_crawler, "fetch_list", fake_fetch_list)

    count = crawl_keywords(["bad", "good"], pages=2, limit=10, output_path=output, delay=0, fetch_details=False)

    assert count == 1
    assert ("good", 1) in calls
    assert "good Developer" in output.read_text(encoding="utf-8")
