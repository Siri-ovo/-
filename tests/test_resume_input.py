from src.inputs.resume_upload import extract_resume_text


def test_extract_resume_text_decodes_txt_upload():
    result = extract_resume_text("resume.txt", "本科软件工程，熟悉 Python 和 SQL".encode("utf-8"))

    assert result.ok is True
    assert result.text == "本科软件工程，熟悉 Python 和 SQL"
    assert result.message == "已从简历文件中提取文本。"


def test_extract_resume_text_rejects_empty_upload():
    result = extract_resume_text("resume.txt", b"   \n")

    assert result.ok is False
    assert result.text == ""
    assert "没有提取到有效文本" in result.message


def test_extract_resume_text_reports_unsupported_type():
    result = extract_resume_text("resume.xlsx", b"not a resume")

    assert result.ok is False
    assert result.text == ""
    assert "仅支持" in result.message
