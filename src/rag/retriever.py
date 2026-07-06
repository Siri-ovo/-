from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.metrics.pairwise import cosine_similarity


def normalize_similarity(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def job_to_document_text(job: dict) -> str:
    return "\n".join(
        [
            f"岗位：{job.get('job_name', '')}",
            f"公司：{job.get('company_name', '')}",
            f"地区：{job.get('area_name', '')}",
            f"薪资：{job.get('salary_low', '')}k-{job.get('salary_high', '')}k",
            f"学历：{job.get('degree_name', '')}",
            f"专业要求：{job.get('major', '')}",
            f"岗位类型：{job.get('job_type', '')}",
            f"行业：{job.get('industry', '')}",
            f"岗位描述：{job.get('description', '')}",
        ]
    )


def load_jobs(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


class JobRetriever:
    def __init__(self, store_path: str = "vector_store") -> None:
        model_path = Path(store_path) / "tfidf.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"向量索引不存在，请先运行 python -m src.rag.build_index: {model_path}")
        payload = joblib.load(model_path)
        self.vectorizer = payload["vectorizer"]
        self.matrix = payload["matrix"]
        self.jobs = payload["jobs"]
        self.documents = payload["documents"]

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        if not query.strip():
            return []
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.matrix)[0]
        ranked = similarities.argsort()[::-1][:top_k]
        results = []
        for idx in ranked:
            job = dict(self.jobs[int(idx)])
            job["document"] = self.documents[int(idx)]
            job["similarity"] = normalize_similarity(float(similarities[int(idx)]))
            results.append(job)
        return results
