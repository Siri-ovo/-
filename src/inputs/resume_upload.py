from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class ResumeExtractionResult:
    ok: bool
    text: str
    message: str


TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
SUPPORTED_EXTENSIONS = sorted(TEXT_EXTENSIONS | {".docx", ".pdf"})


def _clean_text(value: str, limit: int = 12000) -> str:
    lines = [line.strip() for line in str(value or "").replace("\r\n", "\n").split("\n")]
    text = "\n".join(line for line in lines if line)
    return text[:limit]


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _extract_docx_text(data: bytes) -> str:
    try:
        with ZipFile(BytesIO(data)) as docx:
            xml_bytes = docx.read("word/document.xml")
    except (BadZipFile, KeyError):
        return ""
    root = ET.fromstring(xml_bytes)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    return "\n".join(node.text or "" for node in root.iter(f"{namespace}t"))


def _extract_pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as exc:
        raise RuntimeError("PDF 简历解析需要安装 pypdf；当前可上传 txt、md、docx，或直接复制简历文本。") from exc

    reader = PdfReader(BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_resume_text(filename: str, data: bytes) -> ResumeExtractionResult:
    extension = Path(filename or "").suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = "、".join(item.lstrip(".") for item in SUPPORTED_EXTENSIONS)
        return ResumeExtractionResult(False, "", f"简历文件仅支持 {supported} 格式；也可以直接粘贴简历文本。")

    try:
        if extension in TEXT_EXTENSIONS:
            text = _decode_text(data)
        elif extension == ".docx":
            text = _extract_docx_text(data)
        else:
            text = _extract_pdf_text(data)
    except RuntimeError as exc:
        return ResumeExtractionResult(False, "", str(exc))

    cleaned = _clean_text(text)
    if not cleaned:
        return ResumeExtractionResult(False, "", "没有提取到有效文本，请换一个文件或直接粘贴简历内容。")
    return ResumeExtractionResult(True, cleaned, "已从简历文件中提取文本。")
