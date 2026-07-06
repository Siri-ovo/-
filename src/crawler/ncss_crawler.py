from __future__ import annotations

import argparse
import json
import re
import time
from json import JSONDecodeError
from pathlib import Path
from typing import Any

import requests
from requests import HTTPError

from src.utils.text_cleaner import clean_html, normalize_space

BASE_URL = "https://www.ncss.cn"
LIST_URL = f"{BASE_URL}/student/m/api/jobs/jobslist"
HEADERS = {
    "User-Agent": "Mozilla/5.0 career-match-course-project",
    "Referer": f"{BASE_URL}/student/m/jobs/index.html",
}


def build_detail_url(job_id: str) -> str:
    return f"{BASE_URL}/student/m/jobs/{job_id}/detail.html"


def parse_list_item(item: dict[str, Any], keyword: str) -> dict[str, Any]:
    job_id = normalize_space(str(item.get("jobId", "")))
    return {
        "job_id": job_id,
        "job_name": normalize_space(str(item.get("jobName", ""))),
        "company_name": normalize_space(str(item.get("corpName", ""))),
        "area_name": normalize_space(str(item.get("areaName", ""))),
        "salary_low": item.get("lowMonthPay"),
        "salary_high": item.get("highMonthPay"),
        "degree_name": normalize_space(str(item.get("degreeName", ""))),
        "major": normalize_space(str(item.get("major", ""))),
        "company_type": normalize_space(str(item.get("property", ""))),
        "company_size": normalize_space(str(item.get("corpScale", ""))),
        "job_type": "",
        "update_date": normalize_space(str(item.get("updateDate", ""))),
        "description": "",
        "industry": "",
        "source_url": build_detail_url(job_id),
        "keyword": keyword,
        "detail_status": "list_only",
    }


def build_list_description(record: dict[str, Any]) -> str:
    parts = [
        f"岗位：{record.get('job_name', '')}",
        f"公司：{record.get('company_name', '')}",
        f"地区：{record.get('area_name', '')}",
        f"学历：{record.get('degree_name', '')}",
        f"专业要求：{record.get('major', '')}",
        f"薪资：{record.get('salary_low', '')}k-{record.get('salary_high', '')}k",
        f"公司类型：{record.get('company_type', '')}",
        f"公司规模：{record.get('company_size', '')}",
        f"采集关键词：{record.get('keyword', '')}",
    ]
    return normalize_space(" ".join(part for part in parts if part.split("：", 1)[-1]))


def parse_detail_html(html: str) -> dict[str, str]:
    match = re.search(r"var\s+data\s*=\s*(\{.*?\});", html, re.S)
    if not match:
        return {"description": "", "job_type": "", "industry": ""}
    try:
        data = json.loads(match.group(1))
    except JSONDecodeError:
        return {"description": "", "job_type": "", "industry": ""}
    job = data.get("job", {}) or {}
    company = data.get("company", {}) or {}
    return {
        "description": clean_html(str(job.get("description", ""))),
        "job_type": normalize_space(str(job.get("jobType", ""))),
        "industry": normalize_space(str(company.get("primaryIndustry", ""))),
    }


def fetch_list(session: requests.Session, keyword: str, offset: int, limit: int) -> list[dict[str, Any]]:
    response = session.get(
        LIST_URL,
        params={"offset": offset, "limit": limit, "jobName": keyword, "sourcesName": "0"},
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data") or {}
    if not isinstance(data, dict):
        return []
    items = data.get("list") or []
    return items if isinstance(items, list) else []


def fetch_detail(session: requests.Session, job_id: str) -> dict[str, str]:
    response = session.get(build_detail_url(job_id), headers=HEADERS, timeout=20)
    response.raise_for_status()
    return parse_detail_html(response.text)


def crawl_keywords(
    keywords: list[str],
    pages: int,
    limit: int,
    output_path: Path,
    delay: float,
    fetch_details: bool = True,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    seen: set[str] = set()
    count = 0
    try:
        with requests.Session() as session, temp_path.open("w", encoding="utf-8") as fh:
            for keyword in keywords:
                for page in range(1, pages + 1):
                    try:
                        items = fetch_list(session, keyword, page, limit)
                    except HTTPError as exc:
                        status = exc.response.status_code if exc.response is not None else "unknown"
                        if isinstance(status, int) and 500 <= status < 600:
                            print(f"skip keyword after HTTP {status} for keyword={keyword}")
                            break
                        print(f"skip remaining requests after HTTP {status} for keyword={keyword}")
                        raise SystemExit(2) from exc
                    if not items:
                        break
                    for item in items:
                        record = parse_list_item(item, keyword)
                        if not record["job_id"] or record["job_id"] in seen:
                            continue
                        if fetch_details:
                            try:
                                detail = fetch_detail(session, record["job_id"])
                                record.update(detail)
                                if record.get("description"):
                                    record["detail_status"] = "detail"
                            except HTTPError as exc:
                                status = exc.response.status_code if exc.response is not None else "unknown"
                                print(f"keep list item {record['job_id']} after detail HTTP {status}")
                        if not record.get("description"):
                            record["description"] = build_list_description(record)
                            record["detail_status"] = "list_only"
                        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                        seen.add(record["job_id"])
                        count += 1
                        if fetch_details:
                            time.sleep(delay)
                    if not fetch_details and delay > 0:
                        time.sleep(delay)
    except SystemExit:
        if count == 0 and temp_path.exists():
            temp_path.unlink()
        raise
    temp_path.replace(output_path)
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", default="人工智能,软件开发,数据分析,前端开发,测试开发,产品经理,算法工程师,大模型,网络安全,运营,Python,Java,SQL")
    parser.add_argument("--pages", type=int, default=10)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--output", default="data/raw/ncss_jobs_raw.jsonl")
    parser.add_argument("--skip-details", action="store_true", help="Keep list-page jobs without requesting detail pages.")
    args = parser.parse_args()
    keywords = [item.strip() for item in args.keywords.split(",") if item.strip()]
    count = crawl_keywords(keywords, args.pages, args.limit, Path(args.output), args.delay, fetch_details=not args.skip_details)
    print(f"crawled {count} jobs")


if __name__ == "__main__":
    main()
