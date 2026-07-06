from __future__ import annotations

import json
from collections.abc import Callable
from json import JSONDecodeError

import requests


def build_prompt(profile_text: str, evidence_jobs: list[dict]) -> str:
    compact_jobs = [
        {
            "job_name": job.get("job_name", ""),
            "company_name": job.get("company_name", ""),
            "area_name": job.get("area_name", ""),
            "degree_name": job.get("degree_name", ""),
            "major": job.get("major", ""),
            "salary_low": job.get("salary_low", ""),
            "salary_high": job.get("salary_high", ""),
            "similarity": round(float(job.get("similarity", 0)), 4),
            "source_url": job.get("source_url", ""),
            "description": str(job.get("description") or job.get("document", ""))[:600],
        }
        for job in evidence_jobs[:10]
    ]
    evidence = json.dumps(compact_jobs, ensure_ascii=False, indent=2)
    return f"""
You are a career planning assistant for Chinese college students and fresh graduates.
Use Simplified Chinese in all user-facing fields.
Base your advice only on the user profile and the retrieved real job examples.
Do not invent job examples that are not present in the evidence.
If the user provided a target job link or target job description, analyze it together with the retrieved evidence.
Do not output chain-of-thought, Markdown, or fenced code. Output strict JSON only.

Scoring rule:
The application computes final_score with this explainable formula:
RAG job retrieval relevance 40% + skill match 20% + city match 10% + degree match 10% + industry preference match 10% + LLM holistic evaluation 10%.
You only output llm_score from 0 to 100. Do not invent final_score.

Learning path rule:
Keep the plan within 8 weeks. Each stage must contain a concrete goal, 2-3 practical tasks, and one visible deliverable. Avoid vague goals and long schedules such as 3-6 months.

User profile:
{profile_text}

Retrieved real job examples:
{evidence}

Return strict JSON in this schema:
{{
  "recommendations": [
    {{
      "title": "career direction in Chinese",
      "llm_score": 80,
      "reason": "why this direction matches the user",
      "gaps": ["skill gap"],
      "learning_path": {{
        "1_week": {{
          "goal": "1-2周阶段目标：one concrete capability target in Chinese",
          "tasks": ["2-3 practical tasks in Chinese"],
          "deliverable": "可交付成果：one visible output, such as a project, portfolio item, or resume evidence"
        }},
        "2_weeks": {{
          "goal": "3-4周阶段目标：one concrete practice target in Chinese",
          "tasks": ["2-3 practical tasks in Chinese"],
          "deliverable": "可交付成果：one visible output"
        }},
        "1_month": {{
          "goal": "5-6周阶段目标：one application-ready target in Chinese",
          "tasks": ["2-3 practical tasks in Chinese"],
          "deliverable": "可交付成果：one visible output"
        }},
        "3_months": {{
          "goal": "7-8周阶段目标：one delivery/review target in Chinese",
          "tasks": ["2-3 practical tasks in Chinese"],
          "deliverable": "可交付成果：one visible output"
        }}
      }},
      "resume_advice": ["resume improvement advice"],
      "reference_jobs": ["job_name copied exactly from the retrieved examples"]
    }}
  ]
}}
"""


def _extract_balanced_json(text: str) -> str:
    start = text.find("{")
    if start < 0:
        raise ValueError("model response does not contain JSON")
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("model response JSON is incomplete")


def parse_advisor_response(text: str) -> dict:
    raw = _extract_balanced_json(text)
    try:
        payload = json.loads(raw)
    except JSONDecodeError as exc:
        raise ValueError(f"model response JSON is invalid: {exc}") from exc
    recommendations = payload.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        raise ValueError("model response must contain non-empty recommendations")
    for item in recommendations:
        if not isinstance(item, dict):
            raise ValueError("each recommendation must be an object")
        item["llm_score"] = max(0, min(100, round(float(item.get("llm_score", 0)))))
        item.setdefault("title", "Career Direction")
        item.setdefault("reason", "")
        item.setdefault("gaps", [])
        item.setdefault("learning_path", {})
        item.setdefault("resume_advice", [])
        item.setdefault("reference_jobs", [])
    return payload


def call_ollama(prompt: str, model: str = "qwen3:4b", base_url: str = "http://127.0.0.1:11434") -> dict:
    response = requests.post(
        f"{base_url}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}},
        timeout=240,
    )
    response.raise_for_status()
    payload = response.json()
    return parse_advisor_response(payload.get("response", ""))


def call_ollama_with_fallback(
    prompt: str,
    models: list[str],
    base_url: str = "http://127.0.0.1:11434",
    caller: Callable[[str, str, str], dict] = call_ollama,
) -> dict:
    last_error: Exception | None = None
    for model in models:
        try:
            return {"model_used": model, "report": caller(prompt, model, base_url)}
        except Exception as exc:
            last_error = exc
    if last_error is None:
        raise ValueError("at least one model is required")
    raise last_error
