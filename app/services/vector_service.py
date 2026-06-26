import os
from typing import List, Dict, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class VectorStoreManager:
    """
    Manages vector databases in-memory.
    Uses SentenceTransformers for embedding generation and FAISS for similarity searches.
    """
    def __init__(self):
        # Cache the model to avoid re-loading on each operation
        self._model: Optional[SentenceTransformer] = None
        # Maps unique session or document keys to their respective FAISS index & text chunks
        self._stores: Dict[str, Dict] = {}
        # Stores the ID of the currently active document session
        self.active_session_id: Optional[str] = None

    def _get_model(self) -> SentenceTransformer:
        """Lazily instantiates the SentenceTransformer model to optimize startup time."""
        if self._model is None:
            # We load the model from a local folder to avoid Hugging Face Hub calls when offline.
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = os.path.join(base_dir, "models", "all-MiniLM-L6-v2")
            
            if os.path.exists(model_dir) and os.listdir(model_dir):
                try:
                    # Try loading the cached model strictly offline
                    self._model = SentenceTransformer(model_dir, local_files_only=True)
                except Exception as e:
                    # Fallback to standard load if offline load failed for some reason
                    pass
            
            if self._model is None:
                # If local model is not present, we download it online, and then save it locally
                try:
                    self._model = SentenceTransformer('all-MiniLM-L6-v2')
                    os.makedirs(model_dir, exist_ok=True)
                    self._model.save(model_dir)
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to initialize SentenceTransformer model. If you are offline, "
                        f"please make sure the model is downloaded and saved in '{model_dir}'. "
                        f"Error: {str(e)}"
                    )
        return self._model

    def create_session(self, session_id: str, chunks: List[str]) -> bool:
        """
        Creates a new vector store session for a given document.
        
        Args:
            session_id: A unique identifier (e.g. filename or hash)
            chunks: A list of text chunks extracted from the PDF.
            
        Returns:
            True if successful, False otherwise.
        """
        if not chunks:
            return False
            
        model = self._get_model()
        
        # Convert text chunks to vector embeddings
        embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
        dimension = embeddings.shape[1]
        
        # FAISS IndexFlatL2 measures simple Euclidean distance between vectors
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        # Store chunks and index in-memory
        self._stores[session_id] = {
            "index": index,
            "chunks": chunks
        }
        self.active_session_id = session_id
        return True

    def search(self, query: str, session_id: Optional[str] = None, top_k: int = 4) -> List[str]:
        """
        Searches for the most semantically similar text chunks related to a query.
        
        Args:
            query: The user's question or search query.
            session_id: Optional specific session ID; defaults to the active session.
            top_k: Number of matching chunks to return.
            
        Returns:
            A list of matching text chunks.
        """
        target_session = session_id or self.active_session_id
        if not target_session or target_session not in self._stores:
            return []
            
        store = self._stores[target_session]
        index = store["index"]
        chunks = store["chunks"]
        
        model = self._get_model()
        query_embedding = model.encode([query], convert_to_numpy=True, show_progress_bar=False)
        
        # Execute search in FAISS
        distances, indices = index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(chunks):
                results.append(chunks[idx])
                
        return results

    def clear_session(self, session_id: str):
        """Removes a session's vector store from memory."""
        if session_id in self._stores:
            del self._stores[session_id]
        if self.active_session_id == session_id:
            self.active_session_id = None

# Singleton instance to import across the app
vector_store = VectorStoreManager()
