"""
Vector store module: Handles FAISS index creation, saving, loading, and similarity search.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
import faiss
from pathlib import Path
from src.config import FAISS_INDEX_PATH, TOP_K_RESULTS


class VectorStore:
    """
    FAISS-based vector store for document chunk embeddings.
    """
    
    def __init__(self, embedding_dim: int = 384, index_path: Path = FAISS_INDEX_PATH):
        """
        Initialize vector store.
        
        Args:
            embedding_dim: Dimension of embeddings (384 for all-MiniLM-L6-v2)
            index_path: Path to save/load FAISS index
        """
        self.embedding_dim = embedding_dim
        self.index_path = Path(index_path)
        self.metadata_path = self.index_path.parent / "metadata.pkl"
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.chunks_metadata = []  # List of chunk metadata dicts
    
    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Add embedded chunks to the vector store.
        
        Args:
            chunks: List of chunk dicts with 'embedding' and metadata
        """
        if not chunks:
            return
        
        embeddings = np.array([chunk["embedding"] for chunk in chunks], dtype=np.float32)
        self.index.add(embeddings)
        
        # Store metadata (without embeddings to save space)
        for chunk in chunks:
            metadata = {k: v for k, v in chunk.items() if k != "embedding"}
            self.chunks_metadata.append(metadata)
    
    def search(self, query_embedding: List[float], k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Search for the k most similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of top results to return
            
        Returns:
            List of result dicts with chunk info and similarity distance
        """
        if self.index.ntotal == 0:
            return []
        
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks_metadata):
                result = self.chunks_metadata[idx].copy()
                result["distance"] = float(dist)
                result["similarity_score"] = 1 / (1 + float(dist))  # Convert distance to similarity
                results.append(result)
        
        return results
    
    def save(self) -> None:
        """
        Save FAISS index and metadata to disk.
        """
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.chunks_metadata, f)
    
    def load(self) -> bool:
        """
        Load FAISS index and metadata from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.index_path.exists() or not self.metadata_path.exists():
            return False
        
        try:
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, "rb") as f:
                self.chunks_metadata = pickle.load(f)
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dict with index stats
        """
        return {
            "total_chunks": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "index_path": str(self.index_path),
            "metadata_path": str(self.metadata_path)
        }
    
    def reset(self) -> None:
        """
        Clear the vector store.
        """
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.chunks_metadata = []
