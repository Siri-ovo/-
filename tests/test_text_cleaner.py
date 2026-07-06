from src.utils.text_cleaner import clean_html, normalize_space


def test_clean_html_removes_tags_and_keeps_text():
    html = "<div>岗位职责<br>熟悉 Python&nbsp;&nbsp;<b>RAG</b></div>"
    assert clean_html(html) == "岗位职责 熟悉 Python RAG"


def test_normalize_space_collapses_blank_lines():
    text = "Python   RAG\n\n\n岗位要求\t本科"
    assert normalize_space(text) == "Python RAG 岗位要求 本科"
