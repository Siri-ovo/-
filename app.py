from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.analytics.crawl_log import summarize_crawl_batches
from src.analytics.job_dashboard import summarize_jobs
from src.inputs.resume_upload import extract_resume_text
from src.inputs.target_job import build_target_job_context, find_job_by_source_url, merge_target_job_with_evidence
from src.llm.career_advisor import build_prompt, call_ollama_with_fallback
from src.llm.rule_advisor import build_rule_based_report
from src.rag.job_ranker import filter_and_rank_jobs
from src.rag.retriever import JobRetriever
from src.scoring.match_score import score_profile_match
from src.storage.history import load_history_records, save_history_record
from src.ui.reporting import (
    build_markdown_report,
    build_profile_text,
    data_source_rows,
    detailed_score_caption,
    evidence_table_rows,
    learning_path_rows,
    matching_process_rows,
    no_match_guidance_rows,
    score_chart_rows,
    score_formula_rows,
    text as T,
)
from src.ui.theme import (
    apply_app_theme,
    bar_list_html,
    evidence_cards_html,
    empty_state_html,
    field_label,
    hero_html,
    metric_card_html,
    pipeline_html,
    process_steps_html,
    report_card_html,
    section_title_html,
    tag_cloud_html,
)

HISTORY_PATH = Path("data/reports/history.jsonl")
BATCH_DIR = Path("data/raw/batches")


def split_tags(value: object) -> list[str]:
    text_value = str(value or "")
    for sep in ["，", "、", ";", "；", "\n"]:
        text_value = text_value.replace(sep, ",")
    return [item.strip() for item in text_value.split(",") if item.strip()]


def demo_defaults() -> dict[str, str]:
    return {
        "profile_major": T(r"\u8f6f\u4ef6\u5de5\u7a0b"),
        "profile_grade": T(r"\u5927\u4e09"),
        "profile_degree": T(r"\u672c\u79d1"),
        "profile_skills": "Python, SQL, Web, Pandas",
        "profile_interest": T(r"\u4eba\u5de5\u667a\u80fd\u3001\u6570\u636e\u5206\u6790"),
        "profile_city": T(r"\u5e7f\u5dde"),
        "profile_industry": T(r"\u4e92\u8054\u7f51\u3001\u4eba\u5de5\u667a\u80fd"),
        "profile_job_type": T(r"\u5168\u804c"),
        "target_job_url": "",
        "target_job_description": "",
        "profile_resume": T(
            r"\u672c\u79d1\u8f6f\u4ef6\u5de5\u7a0b\u5b66\u751f\uff0c"
            r"\u719f\u6089 Python\u3001SQL \u548c Web \u5f00\u53d1\uff0c"
            r"\u505a\u8fc7\u6570\u636e\u53ef\u89c6\u5316\u548c\u7b80\u5355\u673a\u5668\u5b66\u4e60\u9879\u76ee\u3002"
        ),
    }


def ensure_profile_defaults() -> None:
    for key, value in demo_defaults().items():
        st.session_state.setdefault(key, value)


def load_demo_profile() -> None:
    for key, value in demo_defaults().items():
        st.session_state[key] = value


def evidence_table(evidence_jobs: list[dict]) -> list[dict]:
    return evidence_table_rows(evidence_jobs, normalized_form_for_scoring())


def normalized_form_for_scoring() -> dict:
    return {
        "skills": st.session_state.get("profile_skills", ""),
        "city": st.session_state.get("profile_city", ""),
        "degree": st.session_state.get("profile_degree", ""),
        "industry": st.session_state.get("profile_industry", ""),
    }


def retrieval_constraints() -> dict:
    return {
        "major": st.session_state.get("profile_major", ""),
        "skills": st.session_state.get("profile_skills", ""),
        "city": st.session_state.get("profile_city", ""),
        "industry": st.session_state.get("profile_industry", ""),
        "job_type": st.session_state.get("profile_job_type", ""),
        "target_job_url": st.session_state.get("target_job_url", ""),
    }


def component_score(components: list[dict], names: tuple[str, ...]) -> int:
    return next((int(item.get("score", 0)) for item in components if item.get("name") in names), 0)


def render_metric_cards(cards: list[tuple]) -> None:
    columns = st.columns(len(cards))
    for column, card in zip(columns, cards):
        label, value, note = card[:3]
        icon = card[3] if len(card) > 3 else ""
        column.markdown(metric_card_html(label, value, note, icon=icon), unsafe_allow_html=True)


def render_score_details(chart_rows: list[dict]) -> None:
    st.dataframe(chart_rows, use_container_width=True, hide_index=True)
    st.markdown("**分项匹配程度**")
    for row in chart_rows:
        raw_score = max(0, min(100, int(row.get("原始分", 0))))
        label = (
            f"{row.get('评分项', '')}：原始分 {row.get('原始分', 0)}，"
            f"权重 {row.get('权重(%)', 0)}%，加权分 {row.get('加权分', 0)}"
        )
        st.progress(raw_score, text=label)


def render_matching_process(profile_text: str, constraints: dict, candidate_count: int, evidence_jobs: list[dict]) -> None:
    st.markdown(section_title_html("解释链路", "匹配过程说明", "展示用户画像、RAG 召回、规则过滤和解释性评分的完整过程。"), unsafe_allow_html=True)
    st.markdown(
        process_steps_html(matching_process_rows(profile_text, constraints, candidate_count, evidence_jobs)),
        unsafe_allow_html=True,
    )


def candidate_table(candidate_jobs: list[dict]) -> list[dict]:
    return [
        {
            "岗位名称": job.get("job_name", ""),
            "公司": job.get("company_name", ""),
            "地区": job.get("area_name", ""),
            "岗位类型": job.get("job_type", ""),
            "原始相似度": round(float(job.get("similarity", 0)), 4),
            "来源": job.get("source_url", ""),
        }
        for job in candidate_jobs[:10]
    ]


def render_no_match(candidate_jobs: list[dict], constraints: dict) -> None:
    st.markdown(section_title_html("推荐结果", "暂无可靠匹配", "系统没有强行生成低相关建议，方便答辩时说明推荐边界。"), unsafe_allow_html=True)
    st.warning("未生成职业推荐：当前岗位库中没有足够相关的真实岗位证据。系统已停止推荐，避免生成低相关或误导性的结果。")
    st.dataframe(no_match_guidance_rows(constraints, len(candidate_jobs)), use_container_width=True, hide_index=True)
    if candidate_jobs:
        with st.expander("查看 RAG 初步召回但未作为推荐的候选岗位"):
            st.dataframe(candidate_table(candidate_jobs), use_container_width=True, hide_index=True)


def render_learning_path(learning_path: object) -> None:
    rows = learning_path_rows(learning_path)
    if not rows:
        st.write(learning_path)
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_dashboard(jobs: list[dict]) -> None:
    summary = summarize_jobs(jobs)
    st.markdown(section_title_html("数据概览", T(r"\u5c97\u4f4d\u6570\u636e\u770b\u677f"), "用于证明系统不是凭空生成建议，而是基于真实岗位库检索。"), unsafe_allow_html=True)
    render_metric_cards(
        [
            (T(r"\u5c97\u4f4d\u603b\u6570"), f"{summary['total_jobs']:,}", "已清洗并建立检索索引", "◎"),
            (T(r"\u6570\u636e\u6765\u6e90"), summary["source"], "国家大学生就业服务平台岗位数据", "◇"),
            (T(r"\u6700\u65b0\u66f4\u65b0"), summary["latest_update"] or "-", "数据可用性良好", "□"),
        ]
    )
    st.markdown("**" + T(r"\u6570\u636e\u6765\u6e90\u4e0e\u5904\u7406") + "**")
    st.markdown(
        pipeline_html(["NCSS岗位接口", "岗位去重与字段清洗", "RAG 检索索引构建", "职业匹配与解释性评分"]),
        unsafe_allow_html=True,
    )

    city_col, degree_col, keyword_col = st.columns(3)
    city_col.markdown("**" + T(r"\u57ce\u5e02\u5206\u5e03") + "**")
    city_col.markdown(bar_list_html(summary["city_distribution"]), unsafe_allow_html=True)
    degree_col.markdown("**" + T(r"\u5b66\u5386\u8981\u6c42") + "**")
    degree_col.markdown(bar_list_html(summary["degree_distribution"]), unsafe_allow_html=True)
    keyword_col.markdown("**" + T(r"\u91c7\u96c6\u5173\u952e\u8bcd") + "**")
    keyword_col.markdown(
        tag_cloud_html([item["name"] for item in summary["keyword_distribution"]], css_class="keyword-tags"),
        unsafe_allow_html=True,
    )


def render_crawl_log() -> None:
    summary = summarize_crawl_batches(BATCH_DIR)
    st.markdown(section_title_html("采集审计", T(r"\u6570\u636e\u91c7\u96c6\u8bb0\u5f55"), "保留采集批次，便于展示岗位库来源和数据处理过程。"), unsafe_allow_html=True)
    render_metric_cards(
        [
            (T(r"\u91c7\u96c6\u6279\u6b21"), summary["total_batches"], "历史采集文件数量"),
            (T(r"\u6279\u6b21\u539f\u59cb\u884c\u6570"), summary["total_rows"], "采集到的原始记录"),
            (T(r"\u5217\u8868\u9875\u5c97\u4f4d"), summary["list_only_rows"], "仅列表页记录数量"),
        ]
    )
    if not summary["batches"]:
        st.info(T(r"\u6682\u65e0\u91c7\u96c6\u6279\u6b21\u6587\u4ef6\u3002"))
        return
    table = [
        {
            T(r"\u6587\u4ef6"): item["file"],
            T(r"\u6a21\u5f0f"): item["mode"],
            T(r"\u884c\u6570"): item["rows"],
            T(r"\u5217\u8868\u9875"): item["list_only_rows"],
            T(r"\u8be6\u60c5\u9875"): item["detail_rows"],
            T(r"\u5173\u952e\u8bcd"): item["keywords"],
        }
        for item in summary["batches"]
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)


def render_evidence(evidence_jobs: list[dict]) -> None:
    st.markdown(section_title_html("RAG 证据", T(r"RAG \u68c0\u7d22\u5230\u7684\u771f\u5b9e\u5c97\u4f4d\u6837\u4f8b"), "这些岗位会进入大模型提示词和最终评分，是推荐结果的证据来源。"), unsafe_allow_html=True)
    if len(evidence_jobs) < 5:
        st.warning(T(r"\u5c97\u4f4d\u6837\u4f8b\u4e0d\u8db3 5 \u6761\uff0c\u63a8\u8350\u7ed3\u679c\u53ef\u4fe1\u5ea6\u4f1a\u964d\u4f4e\u3002"))
    st.markdown(evidence_cards_html(evidence_jobs, normalized_form_for_scoring(), max_rows=10), unsafe_allow_html=True)
    for job in evidence_jobs[:10]:
        title = (
            f"{job.get('job_name', '')} - {job.get('company_name', '')} | "
            f"检索得分 {job.get('retrieval_score', 0)} | 原始相似度 {job.get('similarity', 0):.2f}"
        )
        with st.expander(title):
            st.write(T(r"\u5730\u533a") + f": {job.get('area_name', '')}")
            st.write(T(r"\u85aa\u8d44") + f": {job.get('salary_low', '')}k-{job.get('salary_high', '')}k")
            st.write(T(r"\u5b66\u5386") + f": {job.get('degree_name', '')}")
            st.write(T(r"\u4e13\u4e1a\u8981\u6c42") + f": {job.get('major', '')}")
            st.write(T(r"\u6765\u6e90") + f": {job.get('source_url', '')}")
            st.write(str(job.get("description") or job.get("document", ""))[:500])


def render_target_job_input(target_context, matched_job: dict | None) -> None:
    if not target_context.has_content:
        return
    st.markdown(section_title_html("单岗位分析", "目标岗位输入", "用于对齐课程流程图中的职位链接上传/岗位描述分析环节。"), unsafe_allow_html=True)
    rows = []
    if target_context.url:
        rows.append({"项目": "岗位链接", "内容": target_context.url})
    if target_context.description:
        rows.append({"项目": "岗位描述", "内容": target_context.description[:300]})
    rows.append(
        {
            "项目": "岗位库命中",
            "内容": (
                f"{matched_job.get('job_name', '')} - {matched_job.get('company_name', '')}"
                if matched_job
                else "未在当前岗位库中找到同链接岗位，将使用链接/描述参与检索。"
            ),
        }
    )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def enrich_report(report: dict, evidence_jobs: list[dict], model_used: str, scoring_form: dict) -> dict:
    enriched = {"model_used": model_used, "recommendations": []}
    for rec in report.get("recommendations", []):
        breakdown = score_profile_match(scoring_form, rec, evidence_jobs)
        item = dict(rec)
        item["score_breakdown"] = breakdown["components"]
        item["retrieval_score"] = component_score(breakdown["components"], ("RAG 岗位检索相关度", "RAG检索相似度", "RAG similarity"))
        item["llm_score"] = component_score(breakdown["components"], ("大模型综合评价", "LLM evaluation"))
        item["final_score"] = breakdown["final_score"]
        item["score_explanation"] = detailed_score_caption(breakdown)
        enriched["recommendations"].append(item)
    return enriched


def render_report(report: dict, profile_text: str, evidence_jobs: list[dict], key_prefix: str = "current") -> None:
    st.markdown(section_title_html("生成结果", T(r"\u804c\u4e1a\u5339\u914d\u62a5\u544a"), "报告包含推荐方向、匹配分来源、能力短板、提升计划和真实岗位证据。"), unsafe_allow_html=True)
    st.caption(f"model: {report.get('model_used', '')}")
    st.markdown("**" + T(r"\u5339\u914d\u5206\u6570\u600e\u4e48\u7b97") + "**")
    st.dataframe(score_formula_rows(), use_container_width=True, hide_index=True)
    for rec in report.get("recommendations", []):
        st.markdown(
            report_card_html(
                rec.get("title", "Career Direction"),
                rec.get("final_score", 0),
                rec.get("score_explanation", ""),
            ),
            unsafe_allow_html=True,
        )
        st.caption(rec.get("score_explanation", ""))
        chart_rows = score_chart_rows(rec.get("score_breakdown", []))
        if chart_rows:
            render_score_details(chart_rows)
        st.write(rec.get("reason", ""))
        st.markdown("**" + T(r"\u80fd\u529b\u77ed\u677f") + "**")
        st.write(rec.get("gaps", []))
        st.markdown("**能力提升计划**")
        render_learning_path(rec.get("learning_path", {}))
        st.markdown("**" + T(r"\u7b80\u5386\u4f18\u5316\u5efa\u8bae") + "**")
        st.write(rec.get("resume_advice", []))
        st.markdown("**" + T(r"\u5173\u8054\u5c97\u4f4d\u6837\u4f8b") + "**")
        st.write(rec.get("reference_jobs", []))

    markdown = build_markdown_report(
        profile_text,
        report,
        evidence_jobs,
        constraints=report.get("matching_constraints", {}),
        candidate_count=report.get("candidate_count"),
    )
    col1, col2 = st.columns(2)
    col1.download_button(
        T(r"\u4e0b\u8f7d JSON \u62a5\u544a"),
        data=json.dumps(report, ensure_ascii=False, indent=2),
        file_name="career_match_report.json",
        mime="application/json",
        key=f"{key_prefix}_json_download",
    )
    col2.download_button(
        T(r"\u4e0b\u8f7d Markdown \u62a5\u544a"),
        data=markdown,
        file_name="career_match_report.md",
        mime="text/markdown",
        key=f"{key_prefix}_markdown_download",
    )


def render_history() -> None:
    st.markdown(section_title_html("历史记录", T(r"\u5386\u53f2\u62a5\u544a"), "保存最近生成的报告，便于演示不同用户画像下的推荐结果。"), unsafe_allow_html=True)
    records = load_history_records(HISTORY_PATH, limit=20)
    if not records:
        st.info(T(r"\u6682\u65e0\u5386\u53f2\u62a5\u544a\u3002"))
        return
    table = [
        {
            T(r"\u751f\u6210\u65f6\u95f4"): item.get("created_at", ""),
            T(r"\u63a8\u8350\u65b9\u5411"): item.get("top_recommendation", ""),
            T(r"\u5339\u914d\u5206"): item.get("top_score", 0),
            T(r"\u6a21\u578b"): item.get("model_used", ""),
            T(r"\u8bc1\u636e\u6570"): item.get("evidence_count", 0),
        }
        for item in records
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)
    for item in records[:5]:
        with st.expander(f"{item.get('created_at', '')} - {item.get('top_recommendation', '')}"):
            st.text(item.get("profile_text", ""))
            render_report(
                item.get("report", {}),
                item.get("profile_text", ""),
                item.get("evidence_jobs", []),
                key_prefix=f"history_{item.get('id', '')}",
            )


st.set_page_config(page_title=T(r"\u5927\u5b66\u751f\u804c\u4e1a\u5339\u914d\u4e0e\u53d1\u5c55\u5efa\u8bae\u7cfb\u7edf"), layout="wide")
apply_app_theme()
ensure_profile_defaults()

with st.sidebar:
    st.markdown("## " + T(r"\u804c\u4e1a\u753b\u50cf"))
    st.caption(T(r"\u586b\u5199\u4f60\u7684\u57fa\u7840\u4fe1\u606f\uff0c\u7cfb\u7edf\u4f1a\u6839\u636e\u5c97\u4f4d\u5e93\u751f\u6210\u5339\u914d\u5efa\u8bae\u3002"))
    if st.button(T(r"\u4e00\u952e\u52a0\u8f7d\u6f14\u793a\u6848\u4f8b"), use_container_width=True):
        load_demo_profile()
    st.caption(T(r"\u5feb\u901f\u586b\u5165\u793a\u4f8b\u5b66\u751f\u753b\u50cf\uff0c\u4fbf\u4e8e\u4f53\u9a8c\u5339\u914d\u6d41\u7a0b\u3002"))
    grade_options = [T(r"\u5927\u4e00"), T(r"\u5927\u4e8c"), T(r"\u5927\u4e09"), T(r"\u5927\u56db"), T(r"\u7814\u7a76\u751f"), T(r"\u5e94\u5c4a\u751f")]
    degree_options = [T(r"\u4e13\u79d1"), T(r"\u672c\u79d1"), T(r"\u7855\u58eb"), T(r"\u535a\u58eb")]
    job_type_options = [T(r"\u5168\u804c"), T(r"\u5b9e\u4e60"), T(r"\u517c\u804c")]
    basic_section = T(r"\u57fa\u7840\u4fe1\u606f")
    preference_section = T(r"\u6c42\u804c\u504f\u597d")
    resume_section = T(r"\u7b80\u5386\u4e0e\u5c97\u4f4d")
    model_section = T(r"\u6a21\u578b\u8bbe\u7f6e")
    st.markdown(f"### {basic_section}")
    form = {
        T(r"\u4e13\u4e1a"): st.text_input(field_label("🎓", T(r"\u4e13\u4e1a")), key="profile_major"),
        T(r"\u5e74\u7ea7"): st.selectbox(field_label("▦", T(r"\u5e74\u7ea7")), grade_options, key="profile_grade"),
        T(r"\u5b66\u5386"): st.selectbox(field_label("🎓", T(r"\u5b66\u5386")), degree_options, key="profile_degree"),
        T(r"\u5df2\u638c\u63e1\u6280\u80fd"): st.text_area(field_label("💻", T(r"\u5df2\u638c\u63e1\u6280\u80fd")), key="profile_skills"),
    }
    st.markdown("**" + T(r"\u80fd\u529b\u6807\u7b7e") + "**")
    st.markdown(tag_cloud_html(split_tags(st.session_state.get("profile_skills", ""))), unsafe_allow_html=True)
    st.markdown(f"### {preference_section}")
    form.update({
        T(r"\u5174\u8da3\u65b9\u5411"): st.text_input(field_label("✦", T(r"\u5174\u8da3\u65b9\u5411")), key="profile_interest"),
        T(r"\u671f\u671b\u57ce\u5e02"): st.text_input(field_label("⌖", T(r"\u671f\u671b\u57ce\u5e02")), key="profile_city"),
        T(r"\u671f\u671b\u884c\u4e1a"): st.text_input(field_label("◇", T(r"\u671f\u671b\u884c\u4e1a")), key="profile_industry"),
        T(r"\u5c97\u4f4d\u7c7b\u578b"): st.selectbox(field_label("▣", T(r"\u5c97\u4f4d\u7c7b\u578b")), job_type_options, key="profile_job_type"),
    })
    st.markdown("**" + T(r"\u5174\u8da3\u6807\u7b7e") + "**")
    st.markdown(tag_cloud_html(split_tags(st.session_state.get("profile_interest", ""))), unsafe_allow_html=True)
    st.markdown(f"### {resume_section}")
    uploaded_resume = st.file_uploader("简历文件上传（可选）", type=["txt", "md", "markdown", "docx", "pdf"])
    if uploaded_resume is not None:
        resume_result = extract_resume_text(uploaded_resume.name, uploaded_resume.getvalue())
        if resume_result.ok:
            st.session_state["profile_resume"] = resume_result.text
            st.success(resume_result.message)
        else:
            st.warning(resume_result.message)
    form[T(r"\u7b80\u5386\u6587\u672c")] = st.text_area(T(r"\u7b80\u5386\u6587\u672c"), height=180, key="profile_resume")
    st.text_input("目标岗位链接（可选）", key="target_job_url")
    st.text_area("目标岗位描述（可选）", height=120, key="target_job_description")
    st.markdown(f"### {model_section}")
    model = st.selectbox(T(r"\u6a21\u578b"), ["qwen3:4b", "qwen2:0.5b", "gemma3:4b"])
    submitted = st.button(T(r"\u5f00\u59cb\u804c\u4e1a\u5339\u914d\u5206\u6790"), type="primary", use_container_width=True)

try:
    retriever = JobRetriever()
except Exception as exc:
    retriever = None
    st.error(T(r"\u5c97\u4f4d\u5411\u91cf\u7d22\u5f15\u4e0d\u53ef\u7528") + f": {exc}")

st.markdown(hero_html(len(retriever.jobs) if retriever is not None else 0, model), unsafe_allow_html=True)

match_tab, dashboard_tab, crawl_tab, history_tab = st.tabs(
    [
        T(r"\u804c\u4e1a\u5339\u914d\u4e0e\u53d1\u5c55\u5efa\u8bae"),
        T(r"\u5c97\u4f4d\u6570\u636e"),
        T(r"\u6570\u636e\u91c7\u96c6\u8bb0\u5f55"),
        T(r"\u5386\u53f2\u62a5\u544a"),
    ]
)

with dashboard_tab:
    if retriever is None:
        st.stop()
    render_dashboard(retriever.jobs)

with crawl_tab:
    render_crawl_log()

with match_tab:
    if retriever is None:
        st.stop()
    render_metric_cards(
        [
            ("已收录岗位数", f"{len(retriever.jobs):,}", "RAG 检索可用", "◎"),
            ("推荐模式", "画像 + 岗位证据", "支持岗位链接/描述", "◇"),
            ("当前模型", model, "失败时启用规则兜底", "□"),
        ]
    )
    if submitted:
        target_context = build_target_job_context(
            st.session_state.get("target_job_url", ""),
            st.session_state.get("target_job_description", ""),
        )
        if target_context.has_content:
            form["目标岗位输入"] = target_context.text
        profile_text = build_profile_text(form)
        search_text = profile_text + ("\n" + target_context.search_text if target_context.has_content else "")
        candidate_jobs = retriever.search(search_text, top_k=100)
        constraints = retrieval_constraints()
        evidence_jobs = filter_and_rank_jobs(candidate_jobs, constraints, top_k=10)
        matched_target_job = find_job_by_source_url(retriever.jobs, target_context.url)
        evidence_jobs = merge_target_job_with_evidence(matched_target_job, evidence_jobs, top_k=10)
        if not evidence_jobs:
            render_no_match(candidate_jobs, constraints)
            st.stop()

        render_target_job_input(target_context, matched_target_job)
        render_matching_process(profile_text, constraints, len(candidate_jobs), evidence_jobs)
        render_evidence(evidence_jobs)
        prompt = build_prompt(profile_text, evidence_jobs)
        fallback_models = [model] + [item for item in ["qwen2:0.5b", "qwen3:4b", "gemma3:4b"] if item != model]
        with st.spinner(T(r"\u6b63\u5728\u8c03\u7528\u672c\u5730\u5927\u6a21\u578b\u751f\u6210\u62a5\u544a\uff0c\u8bf7\u7a0d\u5019")):
            try:
                result = call_ollama_with_fallback(prompt, models=fallback_models)
            except Exception as exc:
                st.warning(T(r"\u6a21\u578b\u751f\u6210\u5931\u8d25\uff0c\u5df2\u542f\u7528\u89c4\u5219\u515c\u5e95\u62a5\u544a") + f": {exc}")
                result = {
                    "model_used": "rule_fallback",
                    "report": build_rule_based_report(profile_text, evidence_jobs, failure_reason=str(exc)),
                }
        enriched = enrich_report(result["report"], evidence_jobs, result["model_used"], normalized_form_for_scoring())
        enriched["matching_constraints"] = constraints
        enriched["candidate_count"] = len(candidate_jobs)
        save_history_record(HISTORY_PATH, profile_text, enriched, evidence_jobs, result["model_used"])
        render_report(enriched, profile_text, evidence_jobs, key_prefix="current")
    else:
        st.markdown(
            empty_state_html(
                T(r"\u8bf7\u5728\u5de6\u4fa7\u5b8c\u5584\u57fa\u7840\u4fe1\u606f"),
                T(r"\u5f00\u542f\u60a8\u7684\u4e13\u5c5e\u804c\u4e1a\u5339\u914d\u5efa\u8bae"),
            ),
            unsafe_allow_html=True,
        )

with history_tab:
    render_history()
