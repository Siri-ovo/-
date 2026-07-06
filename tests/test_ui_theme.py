from src.ui.theme import (
    APP_CSS,
    bar_list_html,
    evidence_cards_html,
    empty_state_html,
    field_label,
    hero_html,
    metric_card_html,
    pipeline_html,
    process_steps_html,
    section_title_html,
    tag_cloud_html,
)


def _css_block(selector: str) -> str:
    start = APP_CSS.index(selector)
    body_start = APP_CSS.index("{", start) + 1
    body_end = APP_CSS.index("}", body_start)
    return APP_CSS[body_start:body_end]


def test_app_css_uses_blue_product_console_style():
    assert "--accent: #1e3a8a" in APP_CSS
    assert "--accent-soft: #e8eef8" in APP_CSS
    assert "--app-bg: #f3f5f8" in APP_CSS
    assert "#2563eb" not in APP_CSS
    assert "--coral" not in APP_CSS
    assert "#ff4b4b" not in APP_CSS.lower()
    assert "gradient(" not in APP_CSS
    assert "backdrop-filter" not in APP_CSS
    assert ".profile-tags" in APP_CSS
    assert ".pipeline-flow" in APP_CSS
    assert ".bar-row" in APP_CSS
    assert ".process-step-card" in APP_CSS
    assert ".evidence-card" in APP_CSS
    assert ".stButton button[kind=\"primary\"]" in APP_CSS


def test_theme_uses_modern_font_stack_and_lighter_headings():
    assert '"MiSans", "HarmonyOS Sans SC", "PingFang SC"' in APP_CSS
    assert "html, body" in APP_CSS
    assert "font-weight: 700" in _css_block(".app-title")
    assert "letter-spacing: 0.015em" in _css_block(".app-title")
    assert "font-weight: 850" not in APP_CSS
    assert "font-weight: 900" not in APP_CSS


def test_sidebar_is_compact_and_tabs_use_blue_accent():
    assert "width: 320px" in APP_CSS
    assert "min-width: 320px" in APP_CSS
    assert "background: #ffffff" in _css_block('section[data-testid="stSidebar"]')
    assert "border-right: 1px solid #e5e7eb" in _css_block('section[data-testid="stSidebar"]')
    assert "color: #6b7280" in _css_block('div[data-testid="stTabs"] button')
    assert "border-bottom: 3px solid var(--accent)" in APP_CSS
    assert ".stButton button[kind=\"secondary\"]" in APP_CSS
    assert "background: transparent" in _css_block(".stButton button[kind=\"secondary\"]")


def test_hero_html_is_compact_product_console_header():
    html = hero_html(job_count=4974, model="qwen3:4b")
    hero = _css_block(".app-hero")
    title = _css_block(".app-title")

    assert "大学生职业匹配与发展建议系统" in html
    assert "基于真实岗位库的职业匹配、技能差距分析与发展建议" in html
    assert "真实岗位库 4,974 条" in html
    assert "当前模型 qwen3:4b" in html
    assert "支持简历上传" in html
    assert "padding: 22px 28px" in hero
    assert "font-size: 1.62rem" in title


def test_tag_cloud_html_renders_tags_and_escapes_text():
    html = tag_cloud_html(["Python", "<SQL>", "数据分析"])

    assert "profile-tags" in html
    assert "Python" in html
    assert "&lt;SQL&gt;" in html
    assert "<SQL>" not in html
    assert "数据分析" in html


def test_pipeline_html_renders_process_steps():
    html = pipeline_html(["NCSS岗位接口", "岗位去重与字段清洗", "RAG 检索索引构建"])

    assert "pipeline-flow" in html
    assert "NCSS岗位接口" in html
    assert "岗位去重与字段清洗" in html
    assert "RAG 检索索引构建" in html
    assert "pipeline-arrow" in html


def test_bar_list_html_renders_counts_as_horizontal_bars():
    html = bar_list_html([{"name": "广州", "count": 30}, {"name": "北京", "count": 15}])

    assert "bar-list" in html
    assert "广州" in html
    assert "北京" in html
    assert "30" in html
    assert "width: 100.0%" in html
    assert "width: 50.0%" in html


def test_metric_card_html_supports_icon_and_escapes_values():
    html = metric_card_html("岗位总数", "<4974>", "已建立索引", icon="◎")

    assert "&lt;4974&gt;" in html
    assert "<4974>" not in html
    assert "metric-icon" in html
    assert "◎" in html


def test_metric_cards_have_soft_shadow_instead_of_heavy_borders():
    metric = _css_block(".metric-card")

    assert "box-shadow:" in metric
    assert "border: 1px solid var(--border)" in metric
    assert "border-radius: 10px" in metric
    assert "padding: 18px 20px" in metric
    assert "min-height: 108px" in metric
    assert "display: flex" in metric
    assert "justify-content: center" in metric


def test_dashboard_section_spacing_is_tight():
    section = _css_block(".section-title")
    heading = _css_block(".section-title h2")

    assert "margin: 2px 0 6px" in section
    assert "margin: 1px 0 0" in heading
    assert ".section-title + div[data-testid=\"stHorizontalBlock\"]" in APP_CSS
    assert "margin-top: -0.35rem" in APP_CSS


def test_hero_uses_plain_enterprise_card_not_gradient_banner():
    hero = _css_block(".app-hero")

    assert "background: var(--panel)" in hero
    assert "border: 1px solid var(--border)" in hero
    assert "linear-gradient" not in hero
    assert "border-left: 4px solid var(--accent)" in hero


def test_section_title_html_has_kicker_title_and_caption():
    html = section_title_html("职业匹配", "RAG 推荐", "展示真实岗位证据")

    assert "职业匹配" in html
    assert "RAG 推荐" in html
    assert "展示真实岗位证据" in html


def test_process_steps_html_renders_readable_cards():
    html = process_steps_html(
        [
            {
                "阶段": "用户画像",
                "系统处理": "提取专业、技能和城市。",
                "页面证据": "Python, SQL, 广州",
            }
        ]
    )

    assert "process-step-card" in html
    assert "process-stage" in html
    assert "用户画像" in html
    assert "Python, SQL, 广州" in html


def test_evidence_cards_html_turns_keywords_into_tags():
    html = evidence_cards_html(
        [
            {
                "job_name": "Python数据分析师",
                "company_name": "Demo",
                "area_name": "广州",
                "degree_name": "本科及以上",
                "retrieval_score": 88,
                "relevance_level": "高",
                "similarity": 0.22,
                "source_url": "https://www.ncss.cn/student/m/jobs/abc",
                "description": "Python SQL Pandas",
            }
        ],
        {"skills": "Python, SQL, Web", "city": "广州", "degree": "本科", "industry": "人工智能"},
    )

    assert "evidence-card" in html
    assert "Python数据分析师" in html
    assert "evidence-tag" in html
    assert "Python" in html
    assert "SQL" in html
    assert "广州" in html


def test_field_label_adds_icon_text_prefix():
    assert field_label("🎓", "学历") == "🎓 学历"


def test_empty_state_html_replaces_heavy_initial_alert():
    html = empty_state_html(
        "请在左侧完善基础信息",
        "开启您的专属职业匹配建议",
    )

    assert "empty-state" in html
    assert "empty-state-visual" in html
    assert "empty-state-title" in html
    assert "empty-state-text" in html
    assert "请在左侧完善基础信息" in html
    assert "开启您的专属职业匹配建议" in html
