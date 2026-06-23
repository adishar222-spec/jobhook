import pdfplumber
from docx import Document as DocxDocument
import re
import os


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from DOCX."""
    doc = DocxDocument(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_resume_text(file_path: str) -> str:
    """Route extraction based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    raise ValueError(f"Unsupported file type: {ext}")


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(
        r"(\+?\d{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})", text
    )
    return match.group(0).strip() if match else ""


def extract_skills_basic(text: str, skill_list: list) -> list:
    """Simple keyword match against a known skill vocabulary."""
    text_lower = text.lower()
    return [skill for skill in skill_list if skill.lower() in text_lower]
