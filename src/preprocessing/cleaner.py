import re

def clean_text(text: str) -> str:
    """
    Cleans and normalizes extracted text.
    Steps:
    - Remove multiple spaces/newlines
    - Strip leading/trailing spaces
    - Normalize unicode characters
    """
    if not text:
        return ""

    # Normalize line breaks and remove extra spaces
    text = text.replace("\r", "\n")  # Windows line endings
    text = re.sub(r'\n+', '\n', text)  # multiple newlines → 1
    text = re.sub(r'\s+', ' ', text)   # multiple spaces → 1
    text = text.strip()

    # Optional: lowercase copy (keep original for extraction if needed)
    # text = text.lower()

    return text
