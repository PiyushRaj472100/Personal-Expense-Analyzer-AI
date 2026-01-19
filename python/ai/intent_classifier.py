import pickle
import os
import numpy as np
from ai.embeddings import EmbeddingModel


class IntentClassifier:
    def __init__(self):
        self.embedder = EmbeddingModel()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "intent_classifier.pkl")
        with open(model_path, "rb") as f:
         self.model = pickle.load(f)

        model_path1 = os.path.join(base_dir, "intent_label_encoder.pkl")
        with open(model_path1, "rb") as f:
            self.label_encoder = pickle.load(f)

    def predict(self, text: str):
        """
        Predict intent with confidence
        """
        embedding = self.embedder.encode(text)
        probs = self.model.predict_proba([embedding])[0]

        idx = int(np.argmax(probs))
        intent = self.label_encoder.inverse_transform([idx])[0]
        confidence = float(probs[idx])

        return {
            "intent": intent,
            "confidence": round(confidence, 3)
        }
