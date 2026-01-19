# python/ai/tips_engine.py
"""
Personalized AI Tips Engine

Generates contextual financial tips based on:
- Spending patterns
- User profile (income, city tier, family size, pets)
- Category ratios
- Anomaly detection results
- Historical trends

All tips are actionable and personalized.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics


class TipsEngine:
    """
    Production-grade tips generation engine.
    No external dependencies beyond standard library.
    """

    def __init__(self):
        pass

    def generate(
        self,
        *,
        user_profile: Dict,
        transaction_history: Optional[List[Dict]] = None,
        anomaly_result: Optional[Dict] = None,
        category: Optional[str] = None,
        amount: Optional[float] = None,
        monthly_expense: Optional[float] = None,
        monthly_income: Optional[float] = None
    ) -> List[Dict]:
        """
        Generate personalized financial tips.

        Args:
            user_profile: User profile dict (income, family_size, city, has_pets, etc.)
            transaction_history: List of past transactions
            anomaly_result: Anomaly detection result (if available)
            category: Current transaction category (if analyzing specific transaction)
            amount: Current transaction amount (if analyzing specific transaction)
            monthly_expense: Total monthly expenses
            monthly_income: Monthly income

        Returns:
            List of tip dicts:
            {
                "message": str,
                "severity": "low" | "medium" | "high",
                "category": "advice" | "warning" | "insight"
            }
        """
        tips = []

        try:
            # Calculate monthly income if not provided
            if not monthly_income and user_profile.get("annual_income"):
                monthly_income = user_profile["annual_income"] / 12

            # 1. Anomaly-based tips
            if anomaly_result and anomaly_result.get("is_anomaly"):
                tips.extend(self._generate_anomaly_tips(anomaly_result, category, amount))

            # 2. Spending pattern tips
            if transaction_history and len(transaction_history) >= 5:
                tips.extend(self._generate_pattern_tips(
                    transaction_history, user_profile, monthly_income
                ))

            # 3. Category-specific tips
            if category and transaction_history:
                tips.extend(self._generate_category_tips(
                    category, transaction_history, user_profile, monthly_income
                ))

            # 4. Income-to-expense ratio tips
            if monthly_income and monthly_expense:
                tips.extend(self._generate_ratio_tips(
                    monthly_income, monthly_expense, user_profile
                ))

            # 5. Profile-based lifestyle tips
            tips.extend(self._generate_lifestyle_tips(user_profile, transaction_history))

            # 6. Anomaly-based detailed tips (if anomalies exist)
            if transaction_history:
                tips.extend(self._generate_anomaly_detailed_tips(
                    transaction_history, user_profile, monthly_income
                ))

            # Remove duplicates and limit to top 8 for detailed display
            unique_tips = self._deduplicate_tips(tips)
            return unique_tips[:8]

        except Exception as e:
            # Fail-safe: Return empty list on error
            return []

    def _generate_anomaly_tips(
        self,
        anomaly_result: Dict,
        category: Optional[str],
        amount: Optional[float]
    ) -> List[Dict]:
        """Generate tips based on anomaly detection."""
        tips = []
        severity = anomaly_result.get("severity", "medium")
        reason = anomaly_result.get("reason", "")

        if severity == "high":
            tips.append({
                "message": f"⚠️ {reason}. Consider reviewing this expense.",
                "severity": "high",
                "category": "warning"
            })
        elif severity == "medium":
            tips.append({
                "message": f"📊 {reason}. Keep an eye on similar expenses.",
                "severity": "medium",
                "category": "advice"
            })

        return tips

    def _generate_pattern_tips(
        self,
        history: List[Dict],
        profile: Dict,
        monthly_income: Optional[float]
    ) -> List[Dict]:
        """Generate tips based on spending patterns."""
        tips = []

        try:
            # Calculate monthly spending
            now = datetime.now()
            month_ago = now - timedelta(days=30)
            
            recent_txns = [
                t for t in history
                if datetime.strptime(t.get("date", now.strftime("%Y-%m-%d")), "%Y-%m-%d") >= month_ago
            ]
            
            current_month_spend = sum(t.get("amount", 0) for t in recent_txns)

            # Previous month comparison
            two_months_ago = now - timedelta(days=60)
            previous_txns = [
                t for t in history
                if two_months_ago <= datetime.strptime(t.get("date", now.strftime("%Y-%m-%d")), "%Y-%m-%d") < month_ago
            ]
            previous_month_spend = sum(t.get("amount", 0) for t in previous_txns)

            if previous_month_spend > 0:
                change_pct = ((current_month_spend - previous_month_spend) / previous_month_spend) * 100
                
                if change_pct > 25:
                    tips.append({
                        "message": f"📈 Your spending increased by {change_pct:.0f}% this month. Review top categories to identify trends.",
                        "severity": "medium",
                        "category": "warning"
                    })
                elif change_pct < -20:
                    tips.append({
                        "message": f"✅ Great! Your spending decreased by {abs(change_pct):.0f}% this month. Keep it up!",
                        "severity": "low",
                        "category": "insight"
                    })

            # Income ratio check
            if monthly_income and current_month_spend > 0:
                expense_ratio = (current_month_spend / monthly_income) * 100
                
                if expense_ratio > 90:
                    tips.append({
                        "message": f"⚠️ Your expenses ({expense_ratio:.0f}% of income) are very high. Consider creating a budget.",
                        "severity": "high",
                        "category": "warning"
                    })
                elif expense_ratio > 70:
                    tips.append({
                        "message": f"💡 Your expenses are {expense_ratio:.0f}% of income. Aim to keep it below 70% for better savings.",
                        "severity": "medium",
                        "category": "advice"
                    })

        except Exception:
            pass

        return tips

    def _generate_category_tips(
        self,
        category: str,
        history: List[Dict],
        profile: Dict,
        monthly_income: Optional[float]
    ) -> List[Dict]:
        """Generate category-specific tips."""
        tips = []

        try:
            # Calculate category spending
            category_txns = [t for t in history if t.get("category", "").lower() == category.lower()]
            category_total = sum(t.get("amount", 0) for t in category_txns)
            total_spending = sum(t.get("amount", 0) for t in history)

            if total_spending == 0:
                return tips

            category_ratio = (category_total / total_spending) * 100

            # Category-specific thresholds
            category_thresholds = {
                "food & dining": 15,
                "food & groceries": 20,
                "transportation": 10,
                "entertainment": 5,
                "shopping": 10
            }

            threshold = category_thresholds.get(category.lower(), 10)

            if category_ratio > threshold * 1.5:
                tips.append({
                    "message": f"🍽️ Your {category} expense is {category_ratio:.1f}% of total spending (typical: {threshold}%). Consider setting a monthly cap.",
                    "severity": "medium",
                    "category": "advice"
                })

            # Income-based category check
            if monthly_income:
                category_to_income = (category_total / monthly_income) * 100
                
                if category_to_income > 35 and category.lower() in ["food & dining", "food & groceries"]:
                    tips.append({
                        "message": f"💰 {category} is {category_to_income:.0f}% of your monthly income. Meal planning could help reduce costs.",
                        "severity": "medium",
                        "category": "advice"
                    })

        except Exception:
            pass

        return tips

    def _generate_ratio_tips(
        self,
        monthly_income: float,
        monthly_expense: float,
        profile: Dict
    ) -> List[Dict]:
        """Generate tips based on income-to-expense ratio."""
        tips = []

        try:
            if monthly_income == 0:
                return tips

            expense_ratio = (monthly_expense / monthly_income) * 100
            savings_ratio = 100 - expense_ratio

            family_size = profile.get("family_size", 1)
            
            if savings_ratio < 0:
                if family_size >= 3:
                    tips.append({
                        "message": f"🚨 Critical Alert: You're spending {abs(savings_ratio):.0f}% more than your income. For a family of {family_size}, this is unsustainable. Immediate actions: 1) Review all recurring expenses and cancel non-essentials, 2) Create an emergency budget focusing on necessities only, 3) Look for ways to increase income or reduce major expenses, 4) Consider consulting a financial advisor. Your family's financial stability depends on this.",
                        "severity": "high",
                        "category": "warning"
                    })
                else:
                    tips.append({
                        "message": f"🚨 Critical Alert: You're spending {abs(savings_ratio):.0f}% more than your income. This is unsustainable. Immediate actions needed: 1) Review all expenses and identify cuts, 2) Create a strict budget, 3) Consider increasing income sources, 4) Build an emergency fund once you stabilize.",
                        "severity": "high",
                        "category": "warning"
                    })
            elif savings_ratio < 10:
                tips.append({
                    "message": f"⚠️ Savings rate is only {savings_ratio:.0f}%. Financial experts recommend saving at least 20% of income.",
                    "severity": "high",
                    "category": "warning"
                })
            elif savings_ratio < 20:
                tips.append({
                    "message": f"💡 Your savings rate is {savings_ratio:.0f}%. Try to increase it to 20%+ for better financial security.",
                    "severity": "medium",
                    "category": "advice"
                })
            elif savings_ratio >= 30:
                tips.append({
                    "message": f"🎉 Excellent! You're saving {savings_ratio:.0f}% of your income. This is above the recommended 20%.",
                    "severity": "low",
                    "category": "insight"
                })

        except Exception:
            pass

        return tips

    def _generate_lifestyle_tips(
        self,
        profile: Dict,
        history: Optional[List[Dict]]
    ) -> List[Dict]:
        """Generate lifestyle and profile-based tips."""
        tips = []

        try:
            family_size = profile.get("family_members", 1)
            has_pets = profile.get("has_pets", False)
            city = profile.get("city", "").lower()

            # Family size tips
            if family_size >= 4 and history:
                grocery_txns = [t for t in history if "grocery" in t.get("category", "").lower()]
                if len(grocery_txns) < 10:
                    tips.append({
                        "message": "👨‍👩‍👧‍👦 For a family of 4+, consider bulk buying and monthly grocery planning to optimize costs.",
                        "severity": "low",
                        "category": "advice"
                    })

            # Pet-related tips
            if has_pets:
                pet_txns = [t for t in (history or []) if "pet" in t.get("category", "").lower()]
                if len(pet_txns) > 0:
                    tips.append({
                        "message": "🐾 Pet expenses detected. Consider subscription plans for pet supplies to save on recurring costs.",
                        "severity": "low",
                        "category": "advice"
                    })

            # City tier tips (if available)
            if "mumbai" in city or "delhi" in city or "bangalore" in city:
                tips.append({
                    "message": "🏙️ Living in a metro city? Transportation and dining costs can be high. Use public transport and meal prep when possible.",
                    "severity": "low",
                    "category": "insight"
                })

        except Exception:
            pass

        return tips

    def _generate_anomaly_detailed_tips(
        self,
        history: List[Dict],
        profile: Dict,
        monthly_income: Optional[float]
    ) -> List[Dict]:
        """Generate detailed tips based on detected anomalies and family context."""
        tips = []
        
        try:
            family_size = profile.get("family_size", 1)
            
            # Analyze spending trends for anomalies
            now = datetime.now()
            month_ago = now - timedelta(days=30)
            two_months_ago = now - timedelta(days=60)
            
            recent_txns = [
                t for t in history
                if datetime.strptime(t.get("date", now.strftime("%Y-%m-%d")), "%Y-%m-%d") >= month_ago
            ]
            
            previous_txns = [
                t for t in history
                if two_months_ago <= datetime.strptime(t.get("date", now.strftime("%Y-%m-%d")), "%Y-%m-%d") < month_ago
            ]
            
            recent_total = sum(t.get("amount", 0) for t in recent_txns)
            previous_total = sum(t.get("amount", 0) for t in previous_txns)
            
            if previous_total > 0:
                change_pct = ((recent_total - previous_total) / previous_total) * 100
                
                if change_pct > 30:
                    # Significant increase
                    if family_size >= 3:
                        tips.append({
                            "message": f"📈 Your expenses increased by {change_pct:.0f}% this month. For a family of {family_size}, unexpected expenses can add up quickly. Review your top spending categories and identify areas where you can cut back without affecting quality of life. Consider creating a monthly budget that accounts for family needs.",
                            "severity": "high",
                            "category": "warning"
                        })
                    else:
                        tips.append({
                            "message": f"📈 Your expenses increased by {change_pct:.0f}% this month. This is a significant jump. Review your top spending categories and identify non-essential expenses. Creating a monthly budget can help you stay on track.",
                            "severity": "high",
                            "category": "warning"
                        })
                
                # Category-specific anomaly detection
                recent_categories = {}
                previous_categories = {}
                
                for t in recent_txns:
                    cat = t.get("category", "other")
                    recent_categories[cat] = recent_categories.get(cat, 0) + t.get("amount", 0)
                
                for t in previous_txns:
                    cat = t.get("category", "other")
                    previous_categories[cat] = previous_categories.get(cat, 0) + t.get("amount", 0)
                
                # Find categories with significant increases
                for cat, recent_amt in recent_categories.items():
                    prev_amt = previous_categories.get(cat, 0)
                    if prev_amt > 0:
                        cat_change = ((recent_amt - prev_amt) / prev_amt) * 100
                        
                        if cat_change > 50:  # More than 50% increase
                            # Family-aware category tips
                            if cat.lower() in ["food & groceries", "food & dining"] and family_size >= 3:
                                tips.append({
                                    "message": f"🍽️ {cat} expenses increased by {cat_change:.0f}% this month. For a family of {family_size}, meal planning and bulk buying can significantly reduce costs. Consider: 1) Creating a weekly meal plan, 2) Shopping at wholesale stores, 3) Cooking at home more often, 4) Buying seasonal produce. This could save {int(recent_amt * 0.15)}-{int(recent_amt * 0.25)} per month.",
                                    "severity": "medium",
                                    "category": "advice"
                                })
                            elif cat.lower() in ["transportation", "cab"]:
                                tips.append({
                                    "message": f"🚗 {cat} expenses jumped by {cat_change:.0f}% this month. Consider: 1) Using public transport for regular commutes, 2) Carpooling with colleagues, 3) Walking/cycling for short distances, 4) Planning errands in batches to reduce trips. Small changes can lead to big savings.",
                                    "severity": "medium",
                                    "category": "advice"
                                })
                            elif cat.lower() in ["entertainment", "shopping"]:
                                tips.append({
                                    "message": f"🎮 {cat} spending increased by {cat_change:.0f}% this month. While entertainment is important, especially for families, consider setting a monthly budget limit. Look for free or low-cost alternatives like community events, library activities, or family game nights at home.",
                                    "severity": "medium",
                                    "category": "advice"
                                })
                            else:
                                tips.append({
                                    "message": f"⚠️ {cat} expenses increased by {cat_change:.0f}% this month. Review recent transactions in this category to identify if this is a one-time expense or a new spending pattern. If it's recurring, consider finding alternatives or setting a budget cap.",
                                    "severity": "medium",
                                    "category": "warning"
                                })
                
        except Exception:
            pass
        
        return tips

    def _deduplicate_tips(self, tips: List[Dict]) -> List[Dict]:
        """Remove duplicate tips based on message similarity."""
        seen = set()
        unique = []
        
        for tip in tips:
            msg_key = tip["message"][:50]  # First 50 chars as key
            if msg_key not in seen:
                seen.add(msg_key)
                unique.append(tip)
        
        return unique
