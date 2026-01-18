"""
Semantic search module: Query interface for retrieving relevant documents.
"""

from typing import List, Dict
from src.embeddings.embedder import DocumentEmbedder, TextChunker
from src.embeddings.vector_store import VectorStore
from src.config import TOP_K_RESULTS


class SemanticSearchEngine:
    """
    Semantic search engine for querying documents by meaning.
    """
    
    def __init__(self, rebuild_index: bool = False):
        """
        Initialize search engine.
        
        Args:
            rebuild_index: If True, will rebuild index from scratch on index() call
        """
        self.embedder = DocumentEmbedder()
        self.chunker = TextChunker()
        self.vector_store = VectorStore()
        self.rebuild_index = rebuild_index
        
        # Try to load existing index
        if not rebuild_index:
            if self.vector_store.load():
                print("Loaded existing FAISS index.")
            else:
                print("No existing index found. Will create new one on index() call.")
    
    def index_documents(self, documents: List[Dict]) -> None:
        """
        Index a list of documents by chunking and embedding them.
        
        Args:
            documents: List of dicts with 'file_name', 'text', and optionally 'class'
        """
        if self.rebuild_index:
            self.vector_store.reset()
        
        all_chunks = []
        
        for doc in documents:
            file_name = doc.get("file_name", "unknown")
            text = doc.get("text", "")
            doc_class = doc.get("class", "Unknown")
            
            # Chunk the document
            metadata = {
                "file_name": file_name,
                "class": doc_class
            }
            chunks = self.chunker.chunk_text(text, metadata=metadata)
            
            # Embed the chunks
            chunks = self.embedder.embed_chunks(chunks)
            all_chunks.extend(chunks)
        
        # Add all chunks to vector store
        self.vector_store.add_chunks(all_chunks)
        self.vector_store.save()
        
        stats = self.vector_store.get_stats()
        print(f"Indexed {stats['total_chunks']} chunks from {len(documents)} documents.")
    
    def search(self, query: str, k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Search for documents matching the query.
        
        Args:
            query: Natural language query string
            k: Number of top results to return
            
        Returns:
            List of result dicts with file_name, class, chunk_id, and similarity_score
        """
        if self.vector_store.index.ntotal == 0:
            print("Vector store is empty. Please index documents first.")
            return []
        
        # Embed the query
        query_embedding = self.embedder.embed_texts([query])[0]
        
        # Search
        results = self.vector_store.search(query_embedding, k=k)
        
        return results
    
    def search_by_class(self, query: str, doc_class: str, k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Search for documents of a specific class matching the query.
        
        Args:
            query: Natural language query string
            doc_class: Document class filter (e.g., "Invoice", "Resume")
            k: Number of top results to return
            
        Returns:
            Filtered list of results
        """
        all_results = self.search(query, k=k * 2)  # Get extra results for filtering
        
        # Filter by class
        filtered = [r for r in all_results if r.get("class") == doc_class]
        
        return filtered[:k]
    
    def get_stats(self) -> Dict:
        """
        Get search engine statistics.
        
        Returns:
            Dict with stats
        """
        stats = self.vector_store.get_stats()
        stats["embedder_model"] = self.embedder.model_name
        stats["chunk_size"] = self.chunker.chunk_size
        stats["chunk_overlap"] = self.chunker.overlap
        return stats
