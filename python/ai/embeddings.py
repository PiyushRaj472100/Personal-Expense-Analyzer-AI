# python/ai/embeddings.py

from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        # Load once (important for FastAPI performance)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def encode(self, text: str):
        """
        Convert text into embedding vector
        """
        return self.model.encode([text])[0]
