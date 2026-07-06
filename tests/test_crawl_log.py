import json

from src.analytics.crawl_log import summarize_crawl_batches


def test_summarize_crawl_batches_counts_jobs_and_modes(tmp_path):
    batches = tmp_path / "batches"
    batches.mkdir()
    first = batches / "ncss_jobs_list_batch_20260702_082531.jsonl"
    second = batches / "ncss_jobs_batch_20260701_132642.jsonl"
    first.write_text(
        "\n".join(
            [
                json.dumps({"job_id": "1", "detail_status": "list_only", "keyword": "Python"}),
                json.dumps({"job_id": "2", "detail_status": "list_only", "keyword": "Java"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    second.write_text(
        json.dumps({"job_id": "3", "detail_status": "detail", "keyword": "SQL"}) + "\n",
        encoding="utf-8",
    )

    summary = summarize_crawl_batches(batches)

    assert summary["total_batches"] == 2
    assert summary["total_rows"] == 3
    assert summary["list_only_rows"] == 2
    assert summary["detail_rows"] == 1
    assert summary["batches"][0]["file"] == "ncss_jobs_list_batch_20260702_082531.jsonl"
    assert summary["batches"][0]["mode"] == "list"
    assert summary["batches"][0]["keywords"] == "Java, Python"


def test_summarize_crawl_batches_ignores_corrupted_keywords(tmp_path):
    batches = tmp_path / "batches"
    batches.mkdir()
    batch = batches / "ncss_jobs_list_batch_20260702_120856.jsonl"
    batch.write_text(
        "\n".join(
            [
                json.dumps({"job_id": "1", "detail_status": "list_only", "keyword": "????"}),
                json.dumps({"job_id": "2", "detail_status": "list_only", "keyword": "Python"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = summarize_crawl_batches(batches)

    assert summary["batches"][0]["keywords"] == "Python"
