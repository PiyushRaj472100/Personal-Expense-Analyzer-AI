# python/ai/categorizer.py

import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity
from ai.embeddings import EmbeddingModel


class SemanticCategorizer:
    def __init__(self):
        self.embedder = EmbeddingModel()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "category_centroids.pkl")

        with open(model_path, "rb") as f:
            self.category_centroids = pickle.load(f)

        self.keyword_rules = {
            "dining": ["lunch", "dinner", "restaurant", "zomato", "swiggy"],
            "groceries": ["grocery", "milk", "vegetables", "dmart", "zepto"],
            "cab": ["uber", "ola", "taxi", "auto"],
            "fuel": ["petrol", "diesel", "fuel"],
            "rent": ["rent", "flat rent"],
            "electricity": ["electricity", "power bill"],
            "mobile_bill": ["recharge", "jio", "airtel"],
            "subscription": ["netflix", "spotify", "prime", "chatgpt"],
            "medical": ["doctor", "hospital", "medicine"],
            "education": ["fees", "tuition", "course"],
            "shopping": ["amazon", "flipkart", "shopping"],
            "entertainment": ["movie", "cinema"],
            "pet_supplies": ["pet", "dog", "cat"]
        }

    # -------------------------
    def _keyword_match(self, text: str):
        text = text.lower()
        for category, keywords in self.keyword_rules.items():
            for kw in keywords:
                if kw in text:
                    return {
                        "category": category,
                        "confidence": 0.95,
                        "method": "keyword",
                        "needs_user_confirmation": False,
                        "alternatives": []
                    }
        return None

    # -------------------------
    def categorize(self, text: str, threshold: float = 0.45):

        keyword_result = self._keyword_match(text)
        if keyword_result:
            return keyword_result

        embedding = self.embedder.encode(text)

        scores = {
            category: cosine_similarity([embedding], [centroid])[0][0]
            for category, centroid in self.category_centroids.items()
        }

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_category, best_score = sorted_scores[0]

        if best_score < threshold:
            return {
                "category": "other",
                "confidence": round(float(best_score), 3),
                "method": "semantic_low_confidence",
                "alternatives": [c for c, _ in sorted_scores[:3]],
                "needs_user_confirmation": True
            }

        return {
            "category": best_category,
            "confidence": round(float(best_score), 3),
            "method": "semantic",
            "alternatives": [c for c, _ in sorted_scores[1:3]],
            "needs_user_confirmation": False
        }
