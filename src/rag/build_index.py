from __future__ import annotations

import argparse
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from src.rag.retriever import job_to_document_text, load_jobs


def build_index(input_path: Path, store_path: Path) -> int:
    jobs = load_jobs(input_path)
    if not jobs:
        raise ValueError(f"没有可索引岗位数据: {input_path}")
    documents = [job_to_document_text(job) for job in jobs]
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=50000)
    matrix = vectorizer.fit_transform(documents)
    store_path.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"vectorizer": vectorizer, "matrix": matrix, "jobs": jobs, "documents": documents},
        store_path / "tfidf.joblib",
    )
    return len(jobs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/ncss_jobs_clean.jsonl")
    parser.add_argument("--store", default="vector_store")
    args = parser.parse_args()
    count = build_index(Path(args.input), Path(args.store))
    print(f"indexed {count} jobs")


if __name__ == "__main__":
    main()
