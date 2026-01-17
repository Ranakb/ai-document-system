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
docs = list_documents(folder_path=DATA_DIR)  # returns list of file paths
documents = []
for path in docs:
    text = read_document(path)
    documents.append({"file_name": path, "text": text})

# Step 2: Initialize classifier
classifier = DocumentClassifier()

# Step 3: Classify + extract
final_output = {}

for doc in documents:
    cls_result = classifier.classify(doc["text"])
    extracted = extract_fields(cls_result["label"], doc["text"])
    
    final_output[doc["file_name"]] = {
        "class": cls_result["label"],
        "confidence": cls_result["confidence"],
        **extracted
    }

# Step 4: Save output.json
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=2)

print("Extraction complete! output.json created.")
