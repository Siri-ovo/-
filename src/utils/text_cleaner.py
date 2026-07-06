import re

from bs4 import BeautifulSoup


def normalize_space(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def clean_html(html: str) -> str:
    if not html:
        return ""
    if "<" not in html and ">" not in html:
        return normalize_space(html)
    soup = BeautifulSoup(html, "html.parser")
    return normalize_space(soup.get_text(" "))
