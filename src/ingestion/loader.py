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

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}


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
    Reads a document (PDF, TXT, or DOCX) and returns its text content.
    Falls back to pdfplumber if PyPDF2 fails for PDFs.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() == ".txt":
        # Read text file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    elif file_path.suffix.lower() == ".docx":
        # Read Word document
        try:
            try:
                from docx import Document
            except ImportError:
                print(f"Warning: python-docx not installed. Install with: pip install python-docx")
                raise
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            # Normalize unicode characters (Word uses smart quotes and em-dashes)
            text = text.replace('\u2014', '-').replace('\u2013', '-')  # em-dash and en-dash
            text = text.replace('\u201c', '"').replace('\u201d', '"')  # smart quotes
            text = text.replace('\u2019', "'").replace('\u2018', "'")  # smart apostrophes
            return text
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    elif file_path.suffix.lower() == ".pdf":
        # Try PyPDF2 first, then fallback to pdfplumber
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            if text.strip():
                return text
        except Exception as e:
            print(f"PyPDF2 failed for {file_path}: {e}. Trying pdfplumber...")
        
        # Fallback to pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text
        except Exception as e:
            print(f"Error reading {file_path} with both PyPDF2 and pdfplumber: {e}")
            return ""
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
