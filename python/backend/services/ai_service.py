# backend/services/ai_service.py

import numpy as np
import sys
import os

# Add parent directory to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai.categorizer import SemanticCategorizer
from ai.adaptive_categorizer import AdaptiveCategorizer
from ai.anomaly_detector import BehaviorAnomalyDetector
from ai.tips_engine import TipsEngine


def to_python_type(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: to_python_type(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_python_type(v) for v in value]
    return value


class AIService:
    """
    Main AI Service - Orchestrates categorization, anomaly detection, and tips generation.
    All modules are fail-safe and backward compatible.
    """
    
    def __init__(self):
        # Use AdaptiveCategorizer for user-specific learning
        self.categorizer = AdaptiveCategorizer()
        self.anomaly_detector = BehaviorAnomalyDetector()
        self.tips_engine = TipsEngine()

    def analyze_transaction(
        self,
        *,
        text: str,
        amount: float | None = None,
        category: str | None = None,
        date: str | None = None,
        user_profile: dict | None = None,
        history: list | None = None,
        user_id: str | None = None
    ):
        """
        Analyze transaction with full AI pipeline:
        1. Category classification
        2. Anomaly detection (if history available)
        3. Tips generation (if profile/history available)
        
        All modules are optional and fail-safe.
        """
        try:
            # 1. Category classification (always runs, with adaptive learning if user_id provided)
            category_result = self.categorizer.categorize(text, user_id=user_id)
            
            # Use provided category if available, otherwise use AI result
            final_category = category or category_result.get("category", "other")
            
            # 2. Anomaly detection (optional, requires history)
            anomaly_result = {"is_anomaly": False, "score": 0.0, "reason": "", "severity": "low"}
            if history and len(history) >= 3 and amount and date:
                try:
                    anomaly_result = self.anomaly_detector.detect(
                        amount=amount,
                        category=final_category,
                        date=date,
                        user_history=history,
                        user_profile=user_profile or {}
                    )
                except Exception as e:
                    # Fail-safe: Continue without anomaly detection
                    pass
            
            # 3. Tips generation (optional, requires profile/history)
            tips = []
            if user_profile or history:
                try:
                    # Calculate monthly expense if history available
                    monthly_expense = None
                    monthly_income = None
                    
                    if history:
                        from datetime import datetime, timedelta
                        now = datetime.now()
                        month_ago = now - timedelta(days=30)
                        recent_txns = [
                            t for t in history
                            if datetime.strptime(t.get("date", now.strftime("%Y-%m-%d")), "%Y-%m-%d") >= month_ago
                        ]
                        monthly_expense = sum(t.get("amount", 0) for t in recent_txns)
                    
                    if user_profile and user_profile.get("annual_income"):
                        monthly_income = user_profile["annual_income"] / 12
                    
                    tips = self.tips_engine.generate(
                        user_profile=user_profile or {},
                        transaction_history=history or [],
                        anomaly_result=anomaly_result if anomaly_result.get("is_anomaly") else None,
                        category=final_category,
                        amount=amount,
                        monthly_expense=monthly_expense,
                        monthly_income=monthly_income
                    )
                except Exception as e:
                    # Fail-safe: Continue without tips
                    pass

            ai_result = {
                "category": category_result,
                "intent": {"intent": "unknown", "confidence": 0.0},
                "emotion": {"emotion": "neutral", "emotion_score": 0.0},
                "context": {"risk_level": "unknown", "reasons": []},
                "anomaly": anomaly_result,
                "tips": tips
            }

            return to_python_type(ai_result)
            
        except Exception as e:
            # Ultimate fail-safe: Return minimal result
            return {
                "category": {"category": "other", "confidence": 0.0, "method": "fallback"},
                "intent": {"intent": "unknown", "confidence": 0.0},
                "emotion": {"emotion": "neutral", "emotion_score": 0.0},
                "context": {"risk_level": "unknown", "reasons": []},
                "anomaly": {"is_anomaly": False, "score": 0.0, "reason": str(e), "severity": "low"},
                "tips": []
            }
