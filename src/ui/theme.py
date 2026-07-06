from __future__ import annotations

from html import escape

import streamlit as st


APP_CSS = """
<style>
:root {
  --app-bg: #f3f5f8;
  --panel: #ffffff;
  --panel-muted: #f7f9fc;
  --text-main: #172033;
  --text-muted: #5f6f84;
  --border: #d8e0ea;
  --accent: #1e3a8a;
  --accent-hover: #172f70;
  --accent-soft: #e8eef8;
  --accent-border: #b9c7e6;
  --green: #047857;
  --green-soft: #e7f4ef;
  --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 6px 16px rgba(15, 23, 42, 0.08);
  --font-sans: "MiSans", "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
  --font-number: "DIN Alternate", "Segoe UI", Arial, sans-serif;
}

html, body,
[class*="css"],
[data-testid="stAppViewContainer"],
p, div, span, label, input, textarea, button {
  font-family: var(--font-sans) !important;
}

.stApp {
  background: var(--app-bg);
  font-family: var(--font-sans);
}

header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
.stDeployButton,
#MainMenu,
footer {
  display: none;
  visibility: hidden;
  height: 0;
}

section[data-testid="stSidebar"] {
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  width: 320px !important;
  min-width: 320px !important;
  box-shadow: none;
}

section[data-testid="stSidebar"] h3 {
  margin: 1rem 0 0.45rem;
  padding-top: 0.9rem;
  border-top: 1px solid var(--border);
  color: var(--text-main);
  font-size: 0.95rem;
  font-weight: 650;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {
  border-radius: 8px;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] input,
section[data-testid="stSidebar"] textarea {
  border: 1px solid #cbd5e1;
  background: #ffffff;
}

section[data-testid="stSidebar"] label p {
  color: #243247;
  font-weight: 600;
}

section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {
  color: #64748b;
  opacity: 1;
}

.block-container {
  padding-top: 1.35rem;
  padding-bottom: 2.5rem;
  max-width: 1320px;
}

.app-hero {
  background: var(--panel);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: 10px;
  padding: 22px 28px;
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
}

.app-hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.app-kicker,
.section-kicker {
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 650;
  letter-spacing: -0.01em;
}

.app-title {
  font-family: var(--font-sans) !important;
  color: var(--text-main);
  font-size: 1.62rem;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: 0.015em;
  margin: 4px 0 4px;
  max-width: 820px;
}

.app-subtitle,
.section-caption,
.metric-note,
.report-meta {
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.55;
  font-weight: 400;
}

.hero-badges,
.profile-tags,
.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  align-items: center;
}

.hero-badge,
.profile-tag,
.keyword-tag {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 0.8rem;
  padding: 3px 9px;
  white-space: nowrap;
}

.profile-tags,
.keyword-tags {
  margin: 6px 0 10px;
}

.profile-tag {
  background: var(--accent-soft);
  border-color: var(--accent-border);
  color: var(--accent);
  font-weight: 600;
}

.metric-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
  min-height: 108px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.metric-head {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.83rem;
  margin-bottom: 6px;
}

.metric-icon {
  color: var(--accent);
  font-weight: 700;
}

.metric-value {
  font-family: var(--font-number) !important;
  color: var(--text-main);
  font-size: 1.72rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  line-height: 1.1;
}

.empty-state {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  min-height: 320px;
  padding: 52px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.empty-state-visual {
  position: relative;
  width: 78px;
  height: 78px;
  margin-bottom: 18px;
  border-radius: 50%;
  background: var(--accent-soft);
  border: 1px solid var(--accent-border);
}

.empty-state-visual::before {
  content: "";
  position: absolute;
  left: 20px;
  top: 18px;
  width: 27px;
  height: 27px;
  border: 3px solid var(--accent);
  border-radius: 50%;
}

.empty-state-visual::after {
  content: "";
  position: absolute;
  left: 45px;
  top: 45px;
  width: 18px;
  height: 3px;
  background: var(--accent);
  border-radius: 999px;
  transform: rotate(45deg);
  transform-origin: left center;
}

.empty-state-title {
  color: var(--text-main);
  font-size: 1.05rem;
  font-weight: 650;
  margin-bottom: 8px;
}

.empty-state-text {
  color: #6b7280;
  font-size: 0.92rem;
  line-height: 1.6;
  max-width: 460px;
}

.section-title {
  margin: 2px 0 6px;
}

.section-title h2 {
  margin: 1px 0 0;
  font-size: 1.18rem;
  color: var(--text-main);
  font-weight: 650;
  letter-spacing: -0.02em;
}

.section-title + div[data-testid="stHorizontalBlock"],
.section-title + .pipeline-flow,
.section-title + .bar-list {
  margin-top: -0.35rem;
}

.pipeline-flow {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.pipeline-step {
  background: var(--accent-soft);
  border: 1px solid var(--accent-border);
  border-radius: 8px;
  color: var(--text-main);
  padding: 8px 10px;
  font-weight: 650;
  font-size: 0.88rem;
}

.pipeline-arrow {
  color: var(--accent);
  font-weight: 700;
}

.bar-list {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  box-shadow: var(--shadow-sm);
}

.bar-row {
  display: grid;
  grid-template-columns: 78px 1fr 48px;
  align-items: center;
  gap: 10px;
  margin: 8px 0;
  color: var(--text-main);
  font-size: 0.88rem;
}

.bar-track {
  background: #e3e8ef;
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
}

.bar-fill {
  background: var(--accent);
  height: 8px;
  border-radius: 999px;
}

.process-steps {
  display: grid;
  gap: 10px;
  margin: 8px 0 18px;
}

.process-step-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  box-shadow: var(--shadow-sm);
}

.process-stage {
  color: var(--text-main);
  font-weight: 650;
  margin-bottom: 6px;
}

.process-body {
  color: var(--text-main);
  font-size: 0.9rem;
  line-height: 1.55;
}

.process-evidence {
  color: var(--text-muted);
  font-size: 0.84rem;
  line-height: 1.55;
  margin-top: 6px;
}

.evidence-grid {
  display: grid;
  gap: 10px;
  margin: 8px 0 14px;
}

.evidence-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
}

.evidence-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.evidence-title {
  color: var(--text-main);
  font-weight: 650;
  line-height: 1.4;
}

.evidence-company {
  color: var(--text-muted);
  font-size: 0.84rem;
  margin-top: 2px;
}

.evidence-score {
  color: var(--accent);
  background: var(--accent-soft);
  border: 1px solid var(--accent-border);
  border-radius: 8px;
  padding: 4px 9px;
  font-weight: 650;
  white-space: nowrap;
}

.evidence-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 9px;
}

.evidence-tag {
  background: #f7f9fc;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 0.78rem;
  padding: 3px 8px;
}

.evidence-link {
  color: var(--text-muted);
  font-size: 0.78rem;
  margin-top: 8px;
  word-break: break-all;
}

.report-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  margin: 12px 0 10px;
  box-shadow: var(--shadow-sm);
}

.report-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.report-title {
  color: var(--text-main);
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.score-pill {
  background: var(--green-soft);
  border: 1px solid #b8e4d8;
  color: var(--green);
  border-radius: 8px;
  font-weight: 700;
  padding: 6px 12px;
  white-space: nowrap;
}

div[data-testid="stTabs"] button {
  color: #6b7280;
  font-weight: 650;
}

div[data-testid="stTabs"] button p {
  color: inherit;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--accent);
  border-bottom: 3px solid var(--accent);
}

div[data-testid="stDataFrame"] {
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.stButton button[kind="primary"] {
  background: var(--accent);
  border: 1px solid var(--accent);
  border-radius: 8px;
  font-weight: 650;
}

.stButton button[kind="secondary"] {
  background: transparent;
  border: 1px solid var(--accent-border);
  color: var(--accent);
  border-radius: 8px;
  font-weight: 650;
}

.stButton button[kind="secondary"]:hover {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
}

.stButton button[kind="primary"]:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

.stButton button {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.stButton button:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

div[data-testid="stAlert"] {
  border-radius: 10px;
  border: 1px solid var(--border);
}

div[data-testid="stExpander"] {
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow-sm);
}

@media (max-width: 900px) {
  section[data-testid="stSidebar"] {
    width: 100% !important;
    min-width: 100% !important;
  }

  .app-hero-top,
  .report-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
"""


def apply_app_theme() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def _format_count(value: int) -> str:
    return f"{int(value):,}"


def field_label(icon: str, label: str) -> str:
    return f"{icon} {label}"


def hero_html(job_count: int, model: str) -> str:
    return f"""
<div class="app-hero">
  <div class="app-hero-top">
    <div>
      <div class="app-kicker">RAG + 本地大语言模型</div>
      <div class="app-title">大学生职业匹配与发展建议系统</div>
      <div class="app-subtitle">基于真实岗位库的职业匹配、技能差距分析与发展建议</div>
    </div>
    <div class="hero-badges">
      <span class="hero-badge">真实岗位库 {escape(_format_count(job_count))} 条</span>
      <span class="hero-badge">当前模型 {escape(str(model))}</span>
      <span class="hero-badge">支持简历上传</span>
    </div>
  </div>
</div>
"""


def metric_card_html(label: str, value: object, note: str = "", icon: str = "") -> str:
    note_html = f'<div class="metric-note">{escape(str(note))}</div>' if note else ""
    icon_html = f'<span class="metric-icon">{escape(str(icon))}</span>' if icon else ""
    return f"""
<div class="metric-card">
  <div class="metric-head">{icon_html}<span>{escape(str(label))}</span></div>
  <div class="metric-value">{escape(str(value))}</div>
  {note_html}
</div>
"""


def empty_state_html(title: str, text: str) -> str:
    return f"""
<div class="empty-state">
  <div class="empty-state-visual" aria-hidden="true"></div>
  <div class="empty-state-title">{escape(str(title))}</div>
  <div class="empty-state-text">{escape(str(text))}</div>
</div>
"""


def tag_cloud_html(tags: list[str], css_class: str = "profile-tags") -> str:
    items = [str(tag).strip() for tag in tags if str(tag).strip()]
    if not items:
        return ""
    item_class = {
        "keyword-tags": "keyword-tag",
        "evidence-tags": "evidence-tag",
    }.get(css_class, "profile-tag")
    spans = "".join(f'<span class="{item_class}">{escape(tag)}</span>' for tag in items)
    return f'<div class="{escape(css_class)}">{spans}</div>'


def _split_terms(value: object) -> list[str]:
    text_value = str(value or "")
    for sep in ["，", "、", ";", "；", "\n"]:
        text_value = text_value.replace(sep, ",")
    return [item.strip() for item in text_value.split(",") if item.strip()]


def _job_search_text(job: dict) -> str:
    return " ".join(
        str(job.get(key, "") or "")
        for key in ("job_name", "company_name", "area_name", "degree_name", "major", "industry", "description", "document")
    ).lower()


def _evidence_tags(job: dict, profile: dict) -> list[str]:
    corpus = _job_search_text(job)
    tags: list[str] = []
    for key in ("skills", "city", "degree", "industry"):
        for term in _split_terms(profile.get(key, "")):
            if term.lower() in corpus and term not in tags:
                tags.append(term)
    for key in ("area_name", "degree_name", "relevance_level"):
        value = str(job.get(key, "") or "").strip()
        if value and value not in tags:
            tags.append(value)
    return tags[:8]


def process_steps_html(rows: list[dict]) -> str:
    cards = []
    for row in rows:
        stage = row.get("阶段") or row.get("stage") or ""
        process = row.get("系统处理") or row.get("process") or ""
        evidence = row.get("页面证据") or row.get("evidence") or ""
        cards.append(
            f"""
<div class="process-step-card">
  <div class="process-stage">{escape(str(stage))}</div>
  <div class="process-body">{escape(str(process))}</div>
  <div class="process-evidence">{escape(str(evidence))}</div>
</div>
"""
        )
    return f'<div class="process-steps">{"".join(cards)}</div>'


def evidence_cards_html(evidence_jobs: list[dict], profile: dict | None = None, max_rows: int = 6) -> str:
    profile = profile or {}
    cards = []
    for job in evidence_jobs[:max_rows]:
        title = str(job.get("job_name", "") or "")
        company = str(job.get("company_name", "") or "")
        score = str(job.get("retrieval_score", "") or "")
        tags_html = tag_cloud_html(_evidence_tags(job, profile), css_class="evidence-tags")
        source = str(job.get("source_url", "") or "")
        source_html = f'<div class="evidence-link">{escape(source)}</div>' if source else ""
        cards.append(
            f"""
<div class="evidence-card">
  <div class="evidence-card-head">
    <div>
      <div class="evidence-title">{escape(title)}</div>
      <div class="evidence-company">{escape(company)}</div>
    </div>
    <div class="evidence-score">{escape(score)}</div>
  </div>
  {tags_html}
  {source_html}
</div>
"""
        )
    return f'<div class="evidence-grid">{"".join(cards)}</div>'


def pipeline_html(steps: list[str]) -> str:
    cleaned = [str(step).strip() for step in steps if str(step).strip()]
    parts: list[str] = []
    for index, step in enumerate(cleaned):
        if index:
            parts.append('<span class="pipeline-arrow">→</span>')
        parts.append(f'<span class="pipeline-step">{escape(step)}</span>')
    return f'<div class="pipeline-flow">{"".join(parts)}</div>'


def bar_list_html(rows: list[dict], max_rows: int = 5) -> str:
    visible = rows[:max_rows]
    max_count = max((int(item.get("count", 0)) for item in visible), default=1)
    body = []
    for item in visible:
        name = str(item.get("name", ""))
        count = int(item.get("count", 0))
        width = round(count / max_count * 100, 1) if max_count else 0
        body.append(
            f"""
<div class="bar-row">
  <span>{escape(name)}</span>
  <div class="bar-track"><div class="bar-fill" style="width: {width}%"></div></div>
  <strong>{escape(str(count))}</strong>
</div>
"""
        )
    return f'<div class="bar-list">{"".join(body)}</div>'


def section_title_html(kicker: str, title: str, caption: str = "") -> str:
    caption_html = f'<div class="section-caption">{escape(str(caption))}</div>' if caption else ""
    return f"""
<div class="section-title">
  <div class="section-kicker">{escape(str(kicker))}</div>
  <h2>{escape(str(title))}</h2>
  {caption_html}
</div>
"""


def report_card_html(title: str, score: object, meta: str = "") -> str:
    meta_html = f'<div class="report-meta">{escape(str(meta))}</div>' if meta else ""
    return f"""
<div class="report-card">
  <div class="report-heading">
    <div>
      <div class="report-title">{escape(str(title))}</div>
      {meta_html}
    </div>
    <div class="score-pill">{escape(str(score))}</div>
  </div>
</div>
"""
