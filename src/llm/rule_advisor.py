from __future__ import annotations


def _job_title(job: dict, index: int) -> str:
    return str(job.get("job_name") or f"职业方向 {index}")


def build_rule_based_report(profile_text: str, evidence_jobs: list[dict], failure_reason: str = "") -> dict:
    recommendations = []
    for index, job in enumerate(evidence_jobs[:3], start=1):
        title = _job_title(job, index)
        company = str(job.get("company_name", ""))
        similarity = float(job.get("similarity", 0))
        recommendations.append(
            {
                "title": title,
                "llm_score": 65,
                "reason": (
                    "由于大模型暂时不可用，系统启用规则兜底报告。"
                    f"RAG 检索到的真实岗位“{title}”（{company}）与用户画像的原始相似度为 {similarity:.2f}，"
                    "因此作为保守推荐保留。"
                ),
                "gaps": [
                    "人工复核岗位要求中的核心技能。",
                    "优先补齐多个检索岗位反复出现的技能关键词。",
                ],
                "learning_path": {
                    "1_week": {
                        "goal": "快速看懂目标岗位要求。",
                        "tasks": ["整理岗位关键词", "标出已掌握和未掌握技能", "补齐最常见的 1-2 个工具基础"],
                        "deliverable": "一份岗位关键词清单和能力差距清单。",
                    },
                    "2_weeks": {
                        "goal": "做出一个能对应岗位要求的小成果。",
                        "tasks": ["完成一个小型练习项目", "补充业务场景说明", "记录项目过程和关键截图"],
                        "deliverable": "一个可展示的小项目和项目截图。",
                    },
                    "1_month": {
                        "goal": "形成可用于简历和面试的岗位证明材料。",
                        "tasks": ["优化项目 README", "把项目改写成简历条目", "准备 2 分钟项目讲解"],
                        "deliverable": "一版岗位定制简历和一段项目讲解稿。",
                    },
                },
                "resume_advice": [
                    "把已匹配技能和项目证据放在简历前半部分。",
                    "用真实岗位关键词改写项目描述。",
                ],
                "reference_jobs": [title],
            }
        )
    if not recommendations:
        recommendations.append(
            {
                "title": "通用职业发展方向",
                "llm_score": 55,
                "reason": "由于没有足够岗位证据，系统仅生成通用规则兜底建议。",
                "gaps": ["补充技能、城市、行业或简历信息后重新检索。"],
                "learning_path": {
                    "1_week": {
                        "goal": "重新明确目标方向。",
                        "tasks": ["填写更具体的城市和行业偏好", "整理已有技能", "补充简历文本"],
                        "deliverable": "一份更清晰的职业画像和技能清单。",
                    },
                    "2_weeks": {
                        "goal": "完成一个小型实践验证。",
                        "tasks": ["选择一个目标岗位场景", "完成最小项目功能", "记录项目过程"],
                        "deliverable": "一个小型可演示项目。",
                    },
                    "1_month": {
                        "goal": "形成初步投递材料。",
                        "tasks": ["完善简历", "准备自我介绍", "找 3 个同类岗位对照修改"],
                        "deliverable": "一版简历和一份岗位反馈记录。",
                    },
                },
                "resume_advice": ["补充可量化的项目成果。"],
                "reference_jobs": [],
            }
        )
    return {
        "fallback": True,
        "fallback_reason": failure_reason,
        "profile_excerpt": profile_text[:300],
        "recommendations": recommendations,
    }
