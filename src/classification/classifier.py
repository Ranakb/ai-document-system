from sentence_transformers import SentenceTransformer, util

# Document label descriptions (for semantic similarity)
DOC_LABELS = {
    "Invoice": ["Invoice", "Billing", "Total Amount", "Invoice number", "Bill from company", "Due date"],
    "Resume": ["Resume", "Curriculum Vitae", "CV", "Experience", "Skills", "Education"],
    "Utility Bill": ["Utility bill", "Electricity bill", "Gas bill", "Water bill", "Account Number", "Usage", "kWh", "Meter", "Amount Due", "Billing Date", "Provider"],
    "Other": ["Document", "General", "Information", "Content"],
}

# Lowered threshold for semantic similarity
CLASSIFICATION_THRESHOLD = 0.15

# Keywords heuristic for resumes
RESUME_KEYWORDS = ["email", "phone", "experience", "skills", "curriculum vitae", "cv"]

# Keywords heuristic for utility bills
UTILITY_BILL_KEYWORDS = ["account number", "usage", "kwh", "amount due", "billing date", "utility", "meter", "provider"]

# Cover letter indicators
COVER_LETTER_KEYWORDS = ["cover letter", "dear ", "hiring manager", "hiring team", "sincerely", "regards", "position", "apply for"]

def is_likely_cover_letter(text: str) -> bool:
    """
    Detect if document is a cover letter, not a resume.
    Cover letters should be classified as 'Other'.
    """
    text_lower = text.lower()
    # Check for cover letter indicators
    cover_letter_count = sum(1 for k in COVER_LETTER_KEYWORDS if k in text_lower)
    return cover_letter_count >= 2  # Need at least 2 indicators

def is_likely_resume(text: str) -> bool:
    """
    Heuristic to detect resumes based on presence of keywords.
    Avoids false positives with assessment/evaluation documents and cover letters.
    """
    text_lower = text.lower()
    
    # First check if it's a cover letter - if so, it's NOT a resume
    if is_likely_cover_letter(text):
        return False
    
    # Words that indicate this is NOT a resume (assessment, task, requirements, etc.)
    not_resume_words = ["assessment", "task", "requirement", "objective:", "build", "implement", "deliverable", "technical"]
    if any(word in text_lower for word in not_resume_words):
        # Even if it has resume keywords, if it's clearly an assessment/task doc, it's not a resume
        return False
    
    # Need at least 3 resume keywords (email, phone, experience, skills, cv, etc.)
    keyword_count = sum(1 for k in RESUME_KEYWORDS if k in text_lower)
    # Specifically look for "resume" or "cv" or "curriculum vitae" for extra confidence
    has_resume_title = any(term in text_lower for term in ["resume", "curriculum vitae", "cv"])
    
    # If has resume title + 2 other keywords = resume
    # Or if has 3+ keywords without title = resume
    if has_resume_title and keyword_count >= 2:
        return True
    if keyword_count >= 3:
        return True
    
    return False

def is_likely_utility_bill(text: str) -> bool:
    """
    Simple heuristic to detect utility bills based on presence of key words
    """
    text_lower = text.lower()
    # Need at least 2 utility bill keywords
    keyword_count = sum(1 for k in UTILITY_BILL_KEYWORDS if k in text_lower)
    return keyword_count >= 2

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
        Always returns one of: Invoice, Resume, Utility Bill, or Other
        """

        if not text or len(text.strip()) == 0:
            return {"label": "Other", "confidence": 0.0}

        # Step 0: Check for cover letters FIRST - they should be classified as "Other"
        if is_likely_cover_letter(text):
            return {"label": "Other", "confidence": 0.75}  # cover letter is a type of "Other"

        # Step 1: Heuristic check for resume
        if is_likely_resume(text):
            return {"label": "Resume", "confidence": 0.95}  # high confidence for heuristic match

        # Step 1b: Heuristic check for utility bill
        if is_likely_utility_bill(text):
            return {"label": "Utility Bill", "confidence": 0.85}  # high confidence for heuristic match

        # Step 2: Semantic similarity for other document types
        text_lower = text.lower()
        chunks = [line.strip() for line in text_lower.split("\n") if line.strip()]
        if not chunks:
            chunks = [text_lower]

        try:
            # Encode chunks
            chunk_embeddings = self.model.encode(chunks, convert_to_tensor=True)

            # Cosine similarity between chunks and all label embeddings
            similarities = util.cos_sim(chunk_embeddings, self.label_embeddings)

            # Max similarity across all chunks and labels
            max_sim_value = similarities.max()
            max_idx_flat = similarities.argmax().item() if hasattr(similarities.argmax(), 'item') else int(similarities.argmax())
            
            # Ensure the index is valid
            if max_idx_flat < 0 or max_idx_flat >= len(self.label_map):
                return {"label": "Other", "confidence": 0.0}
            
            predicted_label = self.label_map[max_idx_flat]

            # Always return the best match (no threshold rejection)
            # If similarity is very low, default to "Other"
            if max_sim_value < 0.05:
                return {"label": "Other", "confidence": float(max_sim_value)}

            return {"label": predicted_label, "confidence": float(max_sim_value)}
        except Exception:
            return {"label": "Other", "confidence": 0.0}
