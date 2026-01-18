# src/config.py
from pathlib import Path

# Root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
DATA_DIR = BASE_DIR / "data"
INPUT_DOCS_DIR = DATA_DIR / "input_docs"
PROCESSED_TEXT_DIR = DATA_DIR / "processed"

# Output
OUTPUT_FILE = BASE_DIR / "output.json"

# Classification labels and descriptions
DOC_LABELS = {
    "Invoice": "invoice billing total amount due payment tax",
    "Resume": "resume cv experience skills education work history",
    "Utility Bill": "electricity gas water utility bill meter usage kwh",
    "Other": "general document",
}

# Classification: Always returns one of Invoice, Resume, Utility Bill, or Other
# Files that cannot be read are marked as Unclassifiable in main pipeline

# Embedding model (used for classification + retrieval)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking config for retrieval
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# FAISS
FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss_index"

TOP_K_RESULTS = 5

# Regex assumptions (can be refined later)
CURRENCY_REGEX = r"(?:USD|Rs\.?|₹|\$)?\s?\d+(?:,\d{3})*(?:\.\d{2})?"
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d\s\-()]{8,}"

# Optional local LLM (bonus)
LOCAL_LLM_MODEL = "mistral-7b-instruct"
MAX_CONTEXT_LENGTH = 4096
