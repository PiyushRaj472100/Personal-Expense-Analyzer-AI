# python/ai/anomaly.py

import pickle
import numpy as np


class BehaviorAnomalyDetector:
    def __init__(self):
        with open("python/ai/behavior_anomaly_model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def detect(self, *, amount_norm, emotion_score, confidence):
        """
        ML-based behavioral anomaly detection
        """

        features = np.array([[
            amount_norm,
            emotion_score,
            confidence
        ]])

        score = float(self.model.decision_function(features)[0])
        is_anomaly = self.model.predict(features)[0] == -1

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 3)
        }
