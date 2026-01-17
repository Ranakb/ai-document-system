# from pathlib import Path
# from typing import List, Dict

# from src.config import INPUT_DOCS_DIR


# SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


# def list_documents(directory: Path = INPUT_DOCS_DIR) -> List[Path]:
#     """
#     Lists all supported document files in the input directory.
#     """
#     if not directory.exists():
#         raise FileNotFoundError(f"Input directory not found: {directory}")

#     files = [
#         file for file in directory.iterdir()
#         if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
#     ]

#     return files


from pathlib import Path
from typing import List, Dict
from src.config import INPUT_DOCS_DIR
import PyPDF2  # PDF reading

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def list_documents(directory: Path = INPUT_DOCS_DIR) -> List[Path]:
    """
    Lists all supported document files in the input directory.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Input directory not found: {directory}")

    files = [
        file for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    return files


def read_document(file_path: Path) -> str:
    """
    Reads a document (PDF or TXT) and returns its text content.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() == ".txt":
        # Read text file
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.suffix.lower() == ".pdf":
        # Read PDF
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
