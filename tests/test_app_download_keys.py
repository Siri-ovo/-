import ast
from pathlib import Path


def test_render_report_download_buttons_have_unique_keys():
    tree = ast.parse(Path("app.py").read_text(encoding="utf-8"))
    render_report = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "render_report"
    )
    arg_names = [arg.arg for arg in render_report.args.args]
    assert "key_prefix" in arg_names

    download_calls = [
        node
        for node in ast.walk(render_report)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "download_button"
    ]
    assert len(download_calls) == 2
    assert all(any(keyword.arg == "key" for keyword in call.keywords) for call in download_calls)
