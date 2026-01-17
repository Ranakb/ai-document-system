from pathlib import Path

from .pdf_reader import extract_text_from_pdf


def extract_text(file_path: Path) -> str:
    """
    Unified interface for extracting text from supported files.
    """
    if file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(str(file_path))

    elif file_path.suffix.lower() == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")

    return ""
