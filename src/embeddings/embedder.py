"""
Embedder module: Handles text chunking and embedding generation.
"""

from typing import List, Dict
from sentence_transformers import SentenceTransformer
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME


class TextChunker:
    """
    Chunks text into overlapping segments for embedding.
    """
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        """
        Args:
            chunk_size: Number of characters per chunk
            overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks with metadata.
        
        Args:
            text: The text to chunk
            metadata: Optional metadata dict (e.g., file_name, document_class)
            
        Returns:
            List of chunk dicts with text, chunk_id, and metadata
        """
        if not text or len(text.strip()) == 0:
            return []
        
        chunks = []
        step = self.chunk_size - self.overlap
        
        for i in range(0, len(text), step):
            chunk_text = text[i:i + self.chunk_size]
            if len(chunk_text.strip()) > 0:
                chunk_dict = {
                    "text": chunk_text,
                    "chunk_id": len(chunks),
                    "start_pos": i,
                    "end_pos": min(i + self.chunk_size, len(text))
                }
                if metadata:
                    chunk_dict.update(metadata)
                chunks.append(chunk_dict)
        
        return chunks


class DocumentEmbedder:
    """
    Generates embeddings for text using SentenceTransformers.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        """
        Initialize embedder with a sentence transformer model.
        
        Args:
            model_name: Name of the SentenceTransformer model
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_tensor=False,
            show_progress_bar=False
        )
        
        return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
    
    def embed_chunks(self, chunks: List[Dict], batch_size: int = 32) -> List[Dict]:
        """
        Generate embeddings for a list of chunks.
        
        Args:
            chunks: List of chunk dicts with 'text' key
            batch_size: Batch size for encoding
            
        Returns:
            List of chunk dicts with added 'embedding' key
        """
        if not chunks:
            return []
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embed_texts(texts, batch_size=batch_size)
        
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]
        
        return chunks
