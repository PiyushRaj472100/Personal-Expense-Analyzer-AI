# python/ai/context_engine.py

class ContextEngine:
    def __init__(self):
        pass

    def evaluate(self, *, amount, category, intent, emotion,
                 emotion_score, user_profile, history):
        """
        Returns judgment-based evaluation
        """

        reasons = []
        risk_level = "low"

        income = user_profile.get("annual_income", 0)
        family_size = user_profile.get("family_size", 1)
        city_tier = user_profile.get("city_tier", 2)

        avg_spend = history.get("avg_category_spend", 0)
        trend = history.get("trend", "stable")

        # -------- BASELINE EXPECTATION -------- #
        if income > 0:
            expected_limit = (income / 12) * 0.1  # 10% heuristic
        else:
            expected_limit = avg_spend

        # Adjust by family size
        expected_limit *= max(1, family_size / 2)

        # Adjust by city tier
        if city_tier == 1:
            expected_limit *= 1.2
        elif city_tier == 3:
            expected_limit *= 0.85

        # -------- JUDGMENT LOGIC -------- #
        if amount > expected_limit * 1.4:
            risk_level = "high"
            reasons.append(
                f"{category} spend is unusually high for your profile"
            )

        if emotion_score < -0.4:
            reasons.append(
                "Negative emotion detected during this spending"
            )

        if trend == "up":
            reasons.append(
                f"{category} spending trend is increasing"
            )

        if risk_level == "low" and reasons:
            risk_level = "medium"

        return {
            "risk_level": risk_level,
            "reasons": reasons,
            "expected_limit": round(expected_limit, 2)
        }
