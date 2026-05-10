import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDB:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []

    def add_texts(self, chunks: list[str]):
        """Embeds text chunks and adds them to the FAISS index."""
        if not chunks:
            return
        self.chunks.extend(chunks)
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """Searches for the most relevant chunks given a query."""
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results

    def clear(self):
        """Clears the current index and chunks."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []

# Global instance for the application
vector_db = VectorDB()
