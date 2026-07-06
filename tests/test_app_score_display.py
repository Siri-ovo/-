import ast
from pathlib import Path


def test_score_breakdown_uses_compact_details_instead_of_chart():
    tree = ast.parse(Path("app.py").read_text(encoding="utf-8"))
    function_names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}

    assert "render_score_details" in function_names

    chart_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"altair_chart", "bar_chart"}:
                chart_calls.append(node.func.attr)

    assert chart_calls == []
