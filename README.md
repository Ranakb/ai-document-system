# AI Document System - Local Document Classification & Retrieval

A comprehensive local AI system for ingesting, classifying, and extracting structured data from documents (Invoices, Resumes, Utility Bills) using only open-source tools and models.

## 🎯 Features

- **Document Ingestion**: Read PDF and TXT files from a folder
- **Document Classification**: Semantic classification into 5 categories using SentenceTransformers
- **Structured Data Extraction**: Extract specific fields based on document type using regex patterns
- **Semantic Search**: Query documents by meaning using FAISS vector search
- **100% Local**: No external APIs or paid services required

## 📋 Project Structure

```
ai-document-system/
├── src/
│   ├── main.py                 # Main pipeline orchestration
│   ├── config.py               # Configuration and constants
│   ├── __init__.py
│   ├── ingestion/              # Document loading and reading
│   │   ├── loader.py           # List and read documents
│   │   ├── pdf_reader.py       # PDF extraction helper
│   │   └── __init__.py
│   ├── preprocessing/          # Text cleaning
│   │   ├── cleaner.py          # Text normalization
│   │   └── __init__.py
│   ├── classification/         # Document classification
│   │   ├── classifier.py       # Semantic classifier using embeddings
│   │   └── __init__.py
│   ├── extraction/             # Structured data extraction
│   │   ├── dispatcher.py       # Route to appropriate extractor
│   │   ├── invoice.py          # Invoice field extraction
│   │   ├── resume.py           # Resume field extraction
│   │   ├── utility_bill.py     # Utility bill field extraction
│   │   └── __init__.py
│   ├── embeddings/             # Embedding generation
│   │   ├── embedder.py         # Text chunking and embedding
│   │   ├── vector_store.py     # FAISS index management
│   │   └── __init__.py
│   └── retrieval/              # Semantic search
│       ├── search.py           # Query interface
│       └── __init__.py
├── data/
│   ├── input_docs/             # Place your PDF/TXT files here
├── environment.yml             # Conda environment file
├── output.json                 # Classification and extraction results
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

#### Option A: Using Conda (Recommended)

```bash
conda env create -f environment.yml
conda activate ai-doc
```

#### Option B: Using pip

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.10+
- PyTorch
- sentence-transformers
- transformers
- faiss-cpu
- pdfplumber
- PyPDF2
- scikit-learn
- tqdm
- python-dateutil
- regex
- ctransformers (optional)

### 2. Prepare Documents

Place your PDF or TXT documents in `data/input_docs/` folder:

```bash
data/input_docs/
├── invoice_1.pdf
├── invoice_2.pdf
├── resume_1.pdf
├── resume_2.pdf
├── utility_bill_1.pdf
└── other_document.txt
```

### 3. Run the Pipeline

#### Run Full Pipeline (Classification + Extraction)

```bash
python -m src.main
```

This will:
1. Load all documents from `data/input_docs/`
2. Classify each document
3. Extract structured fields
4. Save results to `output.json`

#### Run Semantic Search

```python
from src.ingestion.loader import list_documents, read_document
from src.retrieval.search import SemanticSearchEngine
import json

# Load classification results
with open("output.json", "r") as f:
    results = json.load(f)

# Prepare documents for indexing
documents = []
for doc_path in list_documents():
    text = read_document(doc_path)
    doc_result = results.get(doc_path.name, {})
    documents.append({
        "file_name": doc_path.name,
        "text": text,
        "class": doc_result.get("class", "Unknown")
    })

# Initialize search engine
search_engine = SemanticSearchEngine(rebuild_index=True)
search_engine.index_documents(documents)

# Search
query = "Find all documents mentioning payments due in January"
results = search_engine.search(query, k=5)

for result in results:
    print(f"File: {result['file_name']}")
    print(f"Similarity: {result['similarity_score']:.4f}")
    print(f"Chunk: {result['text'][:100]}...")
    print()
```

## 📊 Output Format

`output.json` contains classification and extraction results:

```json
{
  "invoice_1.pdf": {
    "file_name": "invoice_1.pdf",
    "class": "Invoice",
    "confidence": 0.64,
    "invoice_number": "INV-1234",
    "date": "2025-01-15",
    "company": "ACME Corp",
    "total_amount": "$500.00"
  },
  "resume_1.pdf": {
    "file_name": "resume_1.pdf",
    "class": "Resume",
    "confidence": 0.95,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "experience_years": 5
  },
  "utility_bill_1.pdf": {
    "file_name": "utility_bill_1.pdf",
    "class": "Utility Bill",
    "confidence": 0.87,
    "account_number": "ACC-123456",
    "date": "2025-01-01",
    "usage_kwh": 850.5,
    "amount_due": "$125.00"
  },
  "other_doc.txt": {
    "file_name": "other_doc.txt",
    "class": "Other",
    "confidence": 0.72
  }
}
```

## 🔍 Classification Details

The system classifies documents into 5 categories:

| Category | Detection Method | Fields Extracted |
|----------|-----------------|------------------|
| **Invoice** | Semantic similarity to invoice keywords | invoice_number, date, company, total_amount |
| **Resume** | Heuristic (email, phone, experience keywords) + Semantic | name, email, phone, experience_years |
| **Utility Bill** | Semantic similarity to utility keywords | account_number, date, usage_kwh, amount_due |
| **Other** | Semantic similarity above threshold but no specific class | None |
| **Unclassifiable** | Similarity below threshold (0.25) | None |

### Classification Algorithm

1. **Heuristic Check**: Resume keywords detected → classified as Resume
2. **Semantic Similarity**: Text chunked into sentences, embedded using `sentence-transformers/all-MiniLM-L6-v2`
3. **Similarity Matching**: Cosine similarity computed against label embeddings
4. **Threshold Check**: If max similarity < 0.25 → Unclassifiable

## 📚 Libraries & Methods

### Core Libraries

| Library | Purpose | Usage |
|---------|---------|-------|
| **sentence-transformers** | Semantic embeddings | Classification + Search |
| **faiss-cpu** | Vector similarity search | Semantic search index |
| **PyPDF2 / pdfplumber** | PDF text extraction | Document ingestion |
| **transformers** | NLP models | Model downloading |
| **scikit-learn** | ML utilities | Used for preprocessing |
| **regex** | Advanced regex | Pattern matching |

### Key Methods

#### 1. **Classification** (`src/classification/classifier.py`)
```python
classifier = DocumentClassifier(model_name="sentence-transformers/all-MiniLM-L6-v2")
result = classifier.classify(text)
# Returns: {"label": "Invoice", "confidence": 0.85}
```

- **Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Approach**: Semantic similarity via cosine distance
- **Threshold**: 0.25

#### 2. **Extraction** (`src/extraction/`)
- **Method**: Regex-based pattern matching
- **Invoice**: Invoice number, date (YYYY-MM-DD), company name, currency amounts
- **Resume**: Email, phone, experience years, name
- **Utility Bill**: Account number, date, kWh usage, currency amounts

#### 3. **Semantic Search** (`src/retrieval/search.py`)
```python
engine = SemanticSearchEngine(rebuild_index=True)
engine.index_documents(documents)
results = engine.search("query text", k=5)
```

- **Chunking**: Overlapping chunks (500 chars, 100-char overlap)
- **Index**: FAISS L2 distance
- **Similarity**: Converted from L2 distance to 0-1 score

#### 4. **Text Preprocessing** (`src/preprocessing/cleaner.py`)
- Remove multiple spaces/newlines
- Normalize unicode
- Strip whitespace

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# Document labels and thresholds
DOC_LABELS = {
    "Invoice": "...",
    "Resume": "...",
    "Utility Bill": "...",
    "Other": "..."
}
CLASSIFICATION_THRESHOLD = 0.35

# Embedding model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking for retrieval
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Regex patterns
CURRENCY_REGEX = r"..."
EMAIL_REGEX = r"..."
PHONE_REGEX = r"..."

# Search results
TOP_K_RESULTS = 5

## 🔄 Pipeline Workflow

```
Input Documents (PDF/TXT)
    ↓
[Ingestion] → Load files, extract text
    ↓
[Preprocessing] → Clean and normalize text
    ↓
[Classification] → Semantic classification (384-dim embeddings)
    ↓
[Extraction] → Regex-based field extraction
    ↓
[Indexing] → FAISS vector index for semantic search
    ↓
Output: output.json + FAISS index
```

## 💾 Caching & Storage

- **FAISS Index**: Stored in `data/faiss_index` (binary)
- **Metadata**: `data/metadata.pkl` (chunk metadata)
- **Results**: `output.json` (classification + extraction)

## 🧪 Testing

Run the pipeline on the sample dataset:

```bash
python -m src.main
```

Then search:

```python
from src.retrieval.search import SemanticSearchEngine
import json

# Load indexed documents
engine = SemanticSearchEngine()
results = engine.search("invoice total payment", k=3)
for r in results:
    print(f"{r['file_name']}: {r['similarity_score']:.2%}")
```

## 📈 Performance

- **Classification**: ~2-5ms per document (after model load)
- **Extraction**: ~1-3ms per document
- **Search**: ~10-50ms per query (depending on index size)
- **Model Load**: ~2-5 seconds (first run only)

## 🛑 Limitations

1. **Extraction accuracy** depends on document formatting (regex-based)
2. **Classification threshold** may need tuning for your specific documents
3. **LLM bonus**: Not yet implemented (requires `mistral-7b` or similar)
4. **Language**: Optimized for English documents

## 🔮 Future Enhancements

- [ ] Local LLM Q&A using Mistral-7B or LLaMA
- [ ] Improve extraction with NER models
- [ ] Support more document types
- [ ] REST API interface
- [ ] Web UI dashboard
- [ ] Fine-tune embeddings on domain-specific data

## 📝 License

This project uses open-source libraries under their respective licenses.

## 🤝 Contributing

Feel free to modify and extend the system for your use case!

---

**Last Updated**: January 2026
**Author**: AI Document System
