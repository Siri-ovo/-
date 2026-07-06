import ast
from pathlib import Path


def text(value: str) -> str:
    return value.encode("ascii").decode("unicode_escape")


def _string_constants(tree: ast.AST) -> set[str]:
    return {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}


def _tabs_label_values(tree: ast.AST) -> list[str]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute) and node.func.attr == "tabs"):
            continue
        if not node.args or not isinstance(node.args[0], ast.List):
            continue
        labels = []
        for item in node.args[0].elts:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                labels.append(item.value)
            elif (
                isinstance(item, ast.Call)
                and isinstance(item.func, ast.Name)
                and item.func.id == "T"
                and item.args
                and isinstance(item.args[0], ast.Constant)
            ):
                labels.append(item.args[0].value)
        return labels
    return []


def test_sidebar_exposes_resume_upload_target_job_and_profile_tags():
    source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    constants = _string_constants(tree)
    called_attrs = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert "file_uploader" in called_attrs
    assert text(r"\u7b80\u5386\u6587\u4ef6\u4e0a\u4f20\uff08\u53ef\u9009\uff09") in constants
    assert text(r"\u76ee\u6807\u5c97\u4f4d\u94fe\u63a5\uff08\u53ef\u9009\uff09") in constants
    assert text(r"\u76ee\u6807\u5c97\u4f4d\u63cf\u8ff0\uff08\u53ef\u9009\uff09") in constants
    assert r"\u80fd\u529b\u6807\u7b7e" in constants
    assert r"\u5174\u8da3\u6807\u7b7e" in constants
    assert r"\u4e00\u952e\u52a0\u8f7d\u6f14\u793a\u6848\u4f8b" in constants


def test_app_uses_product_theme_helpers_and_career_first_tabs():
    source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    constants = _string_constants(tree)
    imported_names = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "src.ui.theme"
        for alias in node.names
    }

    assert {
        "apply_app_theme",
        "evidence_cards_html",
        "field_label",
        "hero_html",
        "metric_card_html",
        "section_title_html",
        "tag_cloud_html",
        "pipeline_html",
        "process_steps_html",
        "bar_list_html",
    } <= imported_names
    assert r"\u57fa\u7840\u4fe1\u606f" in constants
    assert r"\u6c42\u804c\u504f\u597d" in constants
    assert r"\u7b80\u5386\u4e0e\u5c97\u4f4d" in constants
    assert r"\u6a21\u578b\u8bbe\u7f6e" in constants
    assert _tabs_label_values(tree)[:2] == [
        r"\u804c\u4e1a\u5339\u914d\u4e0e\u53d1\u5c55\u5efa\u8bae",
        r"\u5c97\u4f4d\u6570\u636e",
    ]


def test_report_formula_section_does_not_use_nested_expander():
    source = Path("app.py").read_text(encoding="utf-8")
    render_report_source = source[source.index("def render_report") : source.index("def render_history")]

    assert "st.expander" not in render_report_source
    assert r"\u5339\u914d\u5206\u6570\u600e\u4e48\u7b97" in render_report_source


def test_matching_and_evidence_sections_use_visual_cards():
    source = Path("app.py").read_text(encoding="utf-8")
    render_matching_source = source[source.index("def render_matching_process") : source.index("def candidate_table")]
    render_evidence_source = source[source.index("def render_evidence") : source.index("def render_target_job_input")]

    assert "process_steps_html" in render_matching_source
    assert "st.dataframe" not in render_matching_source
    assert "evidence_cards_html" in render_evidence_source
