from sentence_transformers import SentenceTransformer, util

# Document label descriptions (for semantic similarity)
DOC_LABELS = {
    "Invoice": ["Invoice document", "Billing statement", "Invoice from company"],
    "Resume": ["Resume", "Curriculum Vitae", "Candidate profile"],
    "Utility Bill": ["Utility bill", "Electricity bill", "Water bill"],
    "Other": ["Other document", "Miscellaneous document"],
}

# Lowered threshold for semantic similarity
CLASSIFICATION_THRESHOLD = 0.25

# Keywords heuristic for resumes
RESUME_KEYWORDS = ["email", "phone", "experience", "skills", "curriculum vitae", "cv"]

def is_likely_resume(text: str) -> bool:
    """
    Simple heuristic to detect resumes based on presence of key words
    """
    text_lower = text.lower()
    return any(k in text_lower for k in RESUME_KEYWORDS)

class DocumentClassifier:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initializes the classifier:
        - Loads embedding model
        - Precomputes label embeddings for efficiency
        """
        self.model = SentenceTransformer(model_name)

        # Flatten labels for embeddings
        self.labels = list(DOC_LABELS.keys())
        self.label_texts = [desc for desc_list in DOC_LABELS.values() for desc in desc_list]
        self.label_embeddings = self.model.encode(self.label_texts, convert_to_tensor=True)

        # Map each embedding index back to the original label
        self.label_map = []
        for label, descs in DOC_LABELS.items():
            self.label_map.extend([label] * len(descs))

    def classify(self, text: str) -> dict:
        """
        Classify a document into one of the labels.
        Returns: {"label": str, "confidence": float}
        """

        if not text or len(text.strip()) == 0:
            return {"label": "Unclassifiable", "confidence": 0.0}

        # Step 1: Heuristic check for resume
        if is_likely_resume(text):
            return {"label": "Resume", "confidence": 0.5}  # heuristic confidence

        # Step 2: Semantic similarity for other document types
        text_lower = text.lower()
        chunks = [line.strip() for line in text_lower.split("\n") if line.strip()]
        if not chunks:
            chunks = [text_lower]

        # Encode chunks
        chunk_embeddings = self.model.encode(chunks, convert_to_tensor=True)

        # Cosine similarity between chunks and all label embeddings
        similarities = util.cos_sim(chunk_embeddings, self.label_embeddings)

        # Max similarity across all chunks and labels
        max_sim_value, max_idx_flat = similarities.max(), similarities.argmax()
        predicted_label = self.label_map[max_idx_flat]

        # Threshold check
        if max_sim_value < CLASSIFICATION_THRESHOLD:
            return {"label": "Unclassifiable", "confidence": max_sim_value.item()}

        return {"label": predicted_label, "confidence": max_sim_value.item()}
