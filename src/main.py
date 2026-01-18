# from src.ingestion.loader import list_documents
# from src.ingestion import extract_text
# from src.preprocessing.cleaner import clean_text
# from src.extraction.dispatcher import extract_fields
# from src.classification.classifier import DocumentClassifier
# from src.config import EMBEDDING_MODEL_NAME

# docs = list_documents()
# processed_docs = []

# for doc in docs:
#     raw_text = extract_text(doc)
#     cleaned = clean_text(raw_text)
#     processed_docs.append({
#         "file_name": doc.name,
#         "raw_text": raw_text,
#         "cleaned_text": cleaned
#     })

# # Quick test print
# for d in processed_docs:
#     print(d["file_name"], "→", len(d["cleaned_text"]))


# classifier = DocumentClassifier(EMBEDDING_MODEL_NAME)

# classified_docs = []
# for doc in processed_docs:
#     result = classifier.classify(doc["cleaned_text"])
#     classified_docs.append({
#         "file_name": doc["file_name"],
#         "class": result["label"],
#         "confidence": result["confidence"]
#     })

# # Quick test
# for d in classified_docs:
#     print(d["file_name"], "->", d["class"], d["confidence"])



# final_docs = []

# for doc, cls in zip(processed_docs, classified_docs):
#     extracted = extract_fields(cls["class"], doc["cleaned_text"])
#     final_docs.append({
#         "file_name": doc["file_name"],
#         "class": cls["class"],
#         "confidence": cls["confidence"],
#         **extracted
#     })

# # Optional: save to JSON
# import json
# from src.config import OUTPUT_FILE

# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump({d["file_name"]: d for d in final_docs}, f, indent=2)


import json
from src.config import DATA_DIR
from src.ingestion.loader import list_documents, read_document
from src.classification.classifier import DocumentClassifier
from src.extraction.dispatcher import extract_fields

# Step 1: Load documents
docs = list_documents()  # returns list of file paths from INPUT_DOCS_DIR
documents = []
print(f"Found {len(docs)} documents to process...")

for path in docs:
    try:
        text = read_document(path)
        documents.append({
            "file_name": path.name, 
            "text": text,
            "readable": bool(text and text.strip())
        })
    except Exception as e:
        print(f"Error reading {path.name}: {e}")
        # Still add it but mark as not readable
        documents.append({
            "file_name": path.name,
            "text": "",
            "readable": False,
            "error": str(e)
        })

print(f"Successfully loaded {len(documents)} documents.\n")

# Step 2: Initialize classifier
classifier = DocumentClassifier()

# Step 3: Classify + extract
final_output = {}

for doc in documents:
    try:
        # If document couldn't be read, mark as Unclassifiable
        if not doc["readable"]:
            final_output[doc["file_name"]] = {
                "class": "Unclassifiable",
                "confidence": 0.0,
                "reason": doc.get("error", "Unable to read file")
            }
            print(f"✗ {doc['file_name']}: Unclassifiable (unreadable - {doc.get('error', 'Unknown error')})")
            continue
        
        cls_result = classifier.classify(doc["text"])
        extracted = extract_fields(cls_result["label"], doc["text"])
        
        final_output[doc["file_name"]] = {
            "class": cls_result["label"],
            "confidence": cls_result["confidence"],
            **extracted
        }
        print(f"✓ {doc['file_name']}: {cls_result['label']} ({cls_result['confidence']:.2%})")
    except Exception as e:
        print(f"✗ {doc['file_name']}: Error during classification - {e}")
        final_output[doc["file_name"]] = {
            "class": "Unclassifiable",
            "confidence": 0.0,
            "reason": f"Classification error: {str(e)}"
        }
        continue

# Step 4: Save output.json
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=2)

print(f"\nExtraction complete! {len(final_output)} documents processed. Results saved to output.json")
