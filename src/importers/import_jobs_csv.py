from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from src.utils.text_cleaner import clean_html, normalize_space

FIELD_ALIASES = {
    "job_id": ["job_id", "岗位ID", "职位ID", "编号"],
    "job_name": ["job_name", "岗位名称", "职位名称", "岗位", "职位"],
    "company_name": ["company_name", "公司名称", "单位名称", "企业名称", "公司"],
    "area_name": ["area_name", "城市", "地区", "工作地点", "地点"],
    "degree_name": ["degree_name", "学历", "学历要求"],
    "major": ["major", "专业", "专业要求"],
    "job_type": ["job_type", "岗位类型", "职位类型", "类型"],
    "industry": ["industry", "行业", "行业类别"],
    "salary_low": ["salary_low", "最低薪资", "薪资下限"],
    "salary_high": ["salary_high", "最高薪资", "薪资上限"],
    "description": ["description", "岗位描述", "职位描述", "任职要求", "工作内容"],
    "source_url": ["source_url", "岗位链接", "职位链接", "来源链接", "链接"],
    "keyword": ["keyword", "关键词", "采集关键词"],
}


def _value(row: dict, field: str) -> str:
    for alias in FIELD_ALIASES[field]:
        if alias in row and row[alias] not in (None, ""):
            return normalize_space(str(row[alias]))
    return ""


def _stable_job_id(record: dict) -> str:
    base = "|".join(
        [
            record.get("source_url", ""),
            record.get("job_name", ""),
            record.get("company_name", ""),
            record.get("area_name", ""),
            record.get("description", ""),
        ]
    )
    return "csv_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def build_import_description(record: dict) -> str:
    parts = [
        f"岗位：{record.get('job_name', '')}",
        f"公司：{record.get('company_name', '')}",
        f"地区：{record.get('area_name', '')}",
        f"学历：{record.get('degree_name', '')}",
        f"专业要求：{record.get('major', '')}",
        f"岗位类型：{record.get('job_type', '')}",
        f"行业：{record.get('industry', '')}",
        f"薪资：{record.get('salary_low', '')}-{record.get('salary_high', '')}",
    ]
    return normalize_space(" ".join(part for part in parts if part.split("：", 1)[-1]))


def normalize_csv_row(row: dict) -> dict:
    record = {field: _value(row, field) for field in FIELD_ALIASES}
    record["description"] = clean_html(record["description"])
    if not record["description"]:
        record["description"] = build_import_description(record)
    if not record["job_id"]:
        record["job_id"] = _stable_job_id(record)
    record["source"] = "csv_import"
    record["detail_status"] = "imported"
    record["keyword"] = record["keyword"] or "csv_import"
    record["company_type"] = ""
    record["company_size"] = ""
    record["update_date"] = ""
    return record


def import_csv_jobs(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with input_path.open("r", encoding="utf-8-sig", newline="") as source, output_path.open(
        "w", encoding="utf-8"
    ) as target:
        reader = csv.DictReader(source)
        for row in reader:
            record = normalize_csv_row(row)
            if not record["job_name"] or not record["company_name"] or not record["description"]:
                continue
            target.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def merge_jsonl_files(main_path: Path, batch_path: Path) -> int:
    main_path.parent.mkdir(parents=True, exist_ok=True)
    merged_path = main_path.with_suffix(main_path.suffix + ".merged.tmp")
    seen: set[str] = set()
    count = 0
    with merged_path.open("w", encoding="utf-8") as target:
        for path in [main_path, batch_path]:
            if not path.exists():
                continue
            with path.open("r", encoding="utf-8") as source:
                for line in source:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    job_id = str(record.get("job_id", ""))
                    if not job_id or job_id in seen:
                        continue
                    seen.add(job_id)
                    target.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1
    merged_path.replace(main_path)
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/raw/batches/import_jobs_batch.jsonl")
    parser.add_argument("--merge-raw", default="")
    args = parser.parse_args()
    output_path = Path(args.output)
    count = import_csv_jobs(Path(args.input), output_path)
    print(f"imported {count} jobs to {output_path}")
    if args.merge_raw:
        merged_count = merge_jsonl_files(Path(args.merge_raw), output_path)
        print(f"merged {merged_count} jobs into {args.merge_raw}")


if __name__ == "__main__":
    main()
