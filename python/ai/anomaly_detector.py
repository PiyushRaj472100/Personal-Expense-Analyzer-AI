# python/ai/anomaly_detector.py
"""
Production-grade Behavior Anomaly Detection Module

Detects abnormal spending patterns using statistical analysis:
- Amount deviation from historical average
- Category spending deviation
- Frequency spikes
- Temporal patterns

All methods are fail-safe and backward compatible.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import math


class BehaviorAnomalyDetector:
    """
    Statistical anomaly detection for expense transactions.
    No ML models required - uses robust statistical methods.
    """

    def __init__(self):
        """Initialize detector (no heavy models loaded)"""
        pass

    def detect(
        self,
        *,
        amount: float,
        category: str,
        date: str,
        user_history: List[Dict],
        user_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Detect if a transaction is anomalous based on user's spending history.

        Args:
            amount: Transaction amount
            category: Transaction category
            date: Transaction date (YYYY-MM-DD)
            user_history: List of past transactions (dicts with 'amount', 'category', 'date')
            user_profile: Optional user profile (income, family_size, etc.)

        Returns:
            {
                "is_anomaly": bool,
                "score": float (0.0-1.0),
                "reason": str,
                "severity": "low" | "medium" | "high"
            }
        """
        try:
            # Fail-safe: If no history, not an anomaly
            if not user_history or len(user_history) < 3:
                return {
                    "is_anomaly": False,
                    "score": 0.0,
                    "reason": "Insufficient history for anomaly detection",
                    "severity": "low"
                }

            # Parse date
            try:
                tx_date = datetime.strptime(date, "%Y-%m-%d")
            except:
                tx_date = datetime.now()

            # Calculate anomaly scores
            amount_score, amount_reason = self._detect_amount_anomaly(
                amount, category, user_history, user_profile
            )
            category_score, category_reason = self._detect_category_anomaly(
                amount, category, user_history
            )
            frequency_score, frequency_reason = self._detect_frequency_anomaly(
                category, tx_date, user_history
            )

            # Weighted combination
            weights = {"amount": 0.5, "category": 0.3, "frequency": 0.2}
            combined_score = (
                amount_score * weights["amount"] +
                category_score * weights["category"] +
                frequency_score * weights["frequency"]
            )

            # Determine if anomaly (threshold: 0.6)
            is_anomaly = combined_score >= 0.6

            # Determine severity
            if combined_score >= 0.8:
                severity = "high"
            elif combined_score >= 0.6:
                severity = "medium"
            else:
                severity = "low"

            # Build reason string
            reasons = []
            if amount_score >= 0.5:
                reasons.append(amount_reason)
            if category_score >= 0.5:
                reasons.append(category_reason)
            if frequency_score >= 0.5:
                reasons.append(frequency_reason)

            reason = "; ".join(reasons) if reasons else "Normal spending pattern"

            return {
                "is_anomaly": is_anomaly,
                "score": round(combined_score, 3),
                "reason": reason,
                "severity": severity,
                "details": {
                    "amount_score": round(amount_score, 3),
                    "category_score": round(category_score, 3),
                    "frequency_score": round(frequency_score, 3)
                }
            }

        except Exception as e:
            # Fail-safe: Return non-anomaly on error
            return {
                "is_anomaly": False,
                "score": 0.0,
                "reason": f"Detection error: {str(e)}",
                "severity": "low"
            }

    def _detect_amount_anomaly(
        self,
        amount: float,
        category: str,
        history: List[Dict],
        user_profile: Optional[Dict] = None
    ) -> Tuple[float, str]:
        """
        Detect if amount is unusually high compared to historical average.

        Returns: (score 0.0-1.0, reason string)
        """
        try:
            # Filter by category
            category_txns = [t for t in history if t.get("category") == category]
            
            if len(category_txns) < 2:
                # Not enough data for this category
                # Compare against all transactions
                all_amounts = [t.get("amount", 0) for t in history if t.get("amount", 0) > 0]
                if len(all_amounts) < 2:
                    return 0.0, ""
                
                avg = statistics.mean(all_amounts)
                std = statistics.stdev(all_amounts) if len(all_amounts) > 1 else avg * 0.3
            else:
                # Category-specific analysis
                amounts = [t.get("amount", 0) for t in category_txns if t.get("amount", 0) > 0]
                avg = statistics.mean(amounts)
                std = statistics.stdev(amounts) if len(amounts) > 1 else avg * 0.3

            # Z-score calculation
            if std == 0:
                z_score = 0.0
            else:
                z_score = (amount - avg) / std

            # Convert z-score to anomaly score (0-1)
            # z > 2.5 = high anomaly, z > 1.5 = medium
            if z_score > 2.5:
                score = min(1.0, 0.7 + (z_score - 2.5) * 0.1)
                reason = f"Amount ({amount:.0f}) is {z_score:.1f}x standard deviations above {category} average ({avg:.0f})"
            elif z_score > 1.5:
                score = 0.5 + (z_score - 1.5) * 0.2
                reason = f"Amount ({amount:.0f}) is above average for {category} ({avg:.0f})"
            else:
                score = max(0.0, z_score * 0.3)
                reason = ""

            # Income-based check (if profile available)
            if user_profile and user_profile.get("annual_income"):
                monthly_income = user_profile["annual_income"] / 12
                if amount > monthly_income * 0.3:  # More than 30% of monthly income
                    score = max(score, 0.7)
                    reason = f"Amount ({amount:.0f}) is {amount/monthly_income*100:.1f}% of monthly income"

            return min(1.0, score), reason

        except Exception:
            return 0.0, ""

    def _detect_category_anomaly(
        self,
        amount: float,
        category: str,
        history: List[Dict]
    ) -> Tuple[float, str]:
        """
        Detect if category spending pattern is unusual.

        Returns: (score 0.0-1.0, reason string)
        """
        try:
            if len(history) < 5:
                return 0.0, ""

            # Calculate category spending ratio
            total_spending = sum(t.get("amount", 0) for t in history)
            category_spending = sum(
                t.get("amount", 0) for t in history 
                if t.get("category") == category
            )

            if total_spending == 0:
                return 0.0, ""

            category_ratio = category_spending / total_spending

            # This transaction's impact
            new_total = total_spending + amount
            new_category_total = category_spending + amount
            new_ratio = new_category_total / new_total if new_total > 0 else 0

            # Check if this transaction significantly changes category ratio
            ratio_change = abs(new_ratio - category_ratio)

            # Expected ratios by category (heuristics)
            expected_ratios = {
                "food & dining": 0.15,
                "food & groceries": 0.20,
                "transportation": 0.10,
                "entertainment": 0.05,
                "healthcare": 0.05,
                "housing": 0.30,
                "utilities": 0.08,
                "shopping": 0.10,
                "technology": 0.05,
                "other": 0.10
            }

            category_lower = category.lower()
            expected = expected_ratios.get(category_lower, 0.10)

            # Score based on deviation from expected
            if new_ratio > expected * 1.5:
                score = min(1.0, 0.6 + (new_ratio - expected * 1.5) * 2)
                reason = f"{category} spending ({new_ratio*100:.1f}%) exceeds typical ratio ({expected*100:.1f}%)"
            elif ratio_change > 0.15:
                score = 0.5 + ratio_change * 2
                reason = f"Significant change in {category} spending pattern"
            else:
                score = 0.0
                reason = ""

            return min(1.0, score), reason

        except Exception:
            return 0.0, ""

    def _detect_frequency_anomaly(
        self,
        category: str,
        date: datetime,
        history: List[Dict]
    ) -> Tuple[float, str]:
        """
        Detect if transaction frequency is unusually high.

        Returns: (score 0.0-1.0, reason string)
        """
        try:
            if len(history) < 5:
                return 0.0, ""

            # Count transactions in same category in last 7 days
            week_ago = date - timedelta(days=7)
            recent_same_category = [
                t for t in history
                if t.get("category") == category and
                datetime.strptime(t.get("date", date.strftime("%Y-%m-%d")), "%Y-%m-%d") >= week_ago
            ]

            # Count transactions in same category in previous 7 days (before week_ago)
            two_weeks_ago = date - timedelta(days=14)
            previous_same_category = [
                t for t in history
                if t.get("category") == category and
                two_weeks_ago <= datetime.strptime(t.get("date", date.strftime("%Y-%m-%d")), "%Y-%m-%d") < week_ago
            ]

            recent_count = len(recent_same_category)
            previous_count = len(previous_same_category)

            if previous_count == 0:
                # No baseline, check if recent count is high
                if recent_count >= 5:
                    return 0.6, f"High frequency: {recent_count} {category} transactions in last 7 days"
                return 0.0, ""

            # Frequency spike detection
            if previous_count > 0:
                frequency_ratio = recent_count / previous_count if previous_count > 0 else recent_count
                
                if frequency_ratio > 3.0:
                    score = min(1.0, 0.7 + (frequency_ratio - 3.0) * 0.1)
                    reason = f"Frequency spike: {recent_count} {category} transactions vs {previous_count} in previous week"
                elif frequency_ratio > 2.0:
                    score = 0.5 + (frequency_ratio - 2.0) * 0.2
                    reason = f"Increased frequency: {recent_count} {category} transactions in last 7 days"
                else:
                    score = 0.0
                    reason = ""

                return min(1.0, score), reason

            return 0.0, ""

        except Exception:
            return 0.0, ""
