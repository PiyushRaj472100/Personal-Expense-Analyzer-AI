import pickle
from sklearn.metrics.pairwise import cosine_similarity
from ai.embeddings import EmbeddingModel
import os

class EmotionDetector:
    def __init__(self):
        self.embedder = EmbeddingModel()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "emotion_classifier.pkl"), "rb") as f:
            self.model = pickle.load(f)

        with open(os.path.join(base_dir, "emotion_label_encoder.pkl"), "rb") as f:
            self.label_encoder = pickle.load(f)

        with open(os.path.join(base_dir,"emotion_centroids.pkl"), "rb") as f:
            self.centroids = pickle.load(f)

    def predict(self, text: str):
        """
        Predict emotion + emotion score
        """
        embedding = self.embedder.encode(text)

        # Emotion classification
        probs = self.model.predict_proba([embedding])[0]
        idx = int(probs.argmax())
        emotion = self.encoder.inverse_transform([idx])[0]

        # Emotion score via centroid similarity
        score = cosine_similarity(
            [embedding], [self.centroids[emotion]]
        )[0][0]

        return {
            "emotion": emotion,
            "emotion_score": round(float(score), 3),
            "confidence": round(float(probs[idx]), 3)
        }
