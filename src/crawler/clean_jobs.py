from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.utils.text_cleaner import clean_html, normalize_space


def clean_record(record: dict) -> dict | None:
    description = clean_html(str(record.get("description", "")))
    if not description:
        return None
    cleaned = dict(record)
    cleaned["description"] = description
    for key in ["job_name", "company_name", "area_name", "degree_name", "major", "job_type", "industry"]:
        cleaned[key] = normalize_space(str(cleaned.get(key, "")))
    return cleaned


def clean_file(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    count = 0
    with input_path.open("r", encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as target:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            job_id = record.get("job_id")
            if not job_id or job_id in seen:
                continue
            cleaned = clean_record(record)
            if not cleaned:
                continue
            target.write(json.dumps(cleaned, ensure_ascii=False) + "\n")
            seen.add(job_id)
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/ncss_jobs_raw.jsonl")
    parser.add_argument("--output", default="data/processed/ncss_jobs_clean.jsonl")
    args = parser.parse_args()
    count = clean_file(Path(args.input), Path(args.output))
    print(f"cleaned {count} jobs")


if __name__ == "__main__":
    main()
