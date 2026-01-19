from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
import os
from dotenv import load_dotenv

from ..database import users_col, transactions_col, alerts_col, profiles_col
from ai.tips_engine import TipsEngine

# ---------------- CONFIG ---------------- #
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET not set in environment")

dashboard_router = APIRouter()
tips_engine = TipsEngine()   # ✅ singleton

# ---------------- AUTH ---------------- #
def get_current_user(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid auth scheme")

        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user = users_col.find_one({"_id": ObjectId(payload["user_id"])})

        if not user:
            raise Exception("User not found")

        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------- ROUTES ---------------- #
@dashboard_router.get("/")
def dashboard(user=Depends(get_current_user)):
    """
    Dashboard overview – lightweight & fast with anomalies and enhanced tips
    """
    try:
        user_id = str(user["_id"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

    # ---------------- INCOME ---------------- #
    annual_income = user.get("annual_income", 0)
    monthly_income = annual_income / 12 if annual_income else 0

    # ---------------- USER PROFILE ---------------- #
    profile = profiles_col.find_one({"user_id": user_id})
    if not profile:
        profile = {}
        if user.get("annual_income"):
            profile["annual_income"] = user.get("annual_income")
    
    user_profile = {
        "user_id": user_id,
        "annual_income": profile.get("annual_income", user.get("annual_income", 0)),
        "family_members": profile.get("family_members", 1),
        "city": profile.get("city", ""),
        "has_pets": profile.get("has_pets", False),
        "family_size": profile.get("family_members", 1)
    }

    # ---------------- TRANSACTIONS ---------------- #
    all_txns = list(transactions_col.find({
        "user_id": user_id
    }))

    total_expense = sum(t.get("amount", 0) for t in all_txns)

    savings = monthly_income - total_expense
    savings_percentage = (
        (savings / monthly_income) * 100 if monthly_income > 0 else 0
    )

    health_score = calculate_health_score(
        savings_percentage, total_expense, monthly_income, user_profile, all_txns
    )

    # ---------------- CATEGORY BREAKDOWN ---------------- #
    category_data = {}
    for t in all_txns:
        cat = t.get("category", "other")
        category_data[cat] = category_data.get(cat, 0) + t.get("amount", 0)

    top_categories = [
        {"name": k, "amount": round(v, 2)}
        for k, v in sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    # ---------------- RECENT TRANSACTIONS ---------------- #
    recent_transactions = list(
        transactions_col.find({"user_id": user_id})
        .sort("date", -1)
        .limit(5)
    )

    for t in recent_transactions:
        t["_id"] = str(t["_id"])
        # Ensure anomaly fields are present
        if "is_anomaly" not in t:
            t["is_anomaly"] = False
        if "anomaly_severity" not in t:
            t["anomaly_severity"] = "low"

    # ---------------- ANOMALIES ---------------- #
    anomalies_col = transactions_col.database["anomalies"]
    
    # Get all anomalies for this user
    all_anomalies = list(
        anomalies_col.find({"user_id": user_id})
        .sort("created_at", -1)
    )
    
    # Get recent anomalies (last 5)
    recent_anomalies = all_anomalies[:5]
    
    anomalies = []
    for anomaly in recent_anomalies:
        anomalies.append({
            "transaction_id": anomaly.get("transaction_id"),
            "amount": anomaly.get("amount", 0),
            "category": anomaly.get("category", ""),
            "severity": anomaly.get("severity", "medium"),
            "reason": anomaly.get("reason", ""),
            "score": anomaly.get("anomaly_score", 0.0),
            "date": anomaly.get("date", ""),
            "created_at": anomaly.get("created_at", datetime.now()).isoformat() if anomaly.get("created_at") else None
        })
        anomaly["_id"] = str(anomaly["_id"])
    
    # Count unread anomalies (created in last 7 days, medium/high severity)
    week_ago = datetime.now() - timedelta(days=7)
    unread_anomalies_count = sum(
        1 for a in all_anomalies
        if a.get("created_at", datetime.now()) >= week_ago
        and a.get("severity") in ["medium", "high"]
    )
    
    # Get high-severity anomalies for urgent notifications
    urgent_anomalies = [
        a for a in all_anomalies
        if a.get("severity") == "high"
        and a.get("created_at", datetime.now()) >= week_ago
    ]

    # ---------------- ALERTS ---------------- #
    recent_alerts = list(
        alerts_col.find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(3)
    )

    alerts = [
        {
            "type": alert.get("type", "warning"),
            "message": alert.get("message", "")
        }
        for alert in recent_alerts
    ]

    # ---------------- AI TIPS (ENHANCED) ---------------- #
    # Calculate monthly expense
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    recent_txns = [
        t for t in all_txns
        if datetime.strptime(t.get("date", now.strftime("%Y-%m-%d")), "%Y-%m-%d") >= month_ago
    ]
    monthly_expense = sum(t.get("amount", 0) for t in recent_txns)

    # Generate enhanced tips with anomaly context
    tips = tips_engine.generate(
        user_profile=user_profile,
        transaction_history=all_txns,
        monthly_expense=monthly_expense,
        monthly_income=monthly_income
    )
    
    # Add anomaly-specific tips to the tips array
    if urgent_anomalies:
        for urgent in urgent_anomalies[:2]:  # Top 2 urgent anomalies
            tips.insert(0, {
                "message": f"🚨 URGENT: {urgent.get('reason', 'Unusual spending detected')} - ₹{urgent.get('amount', 0):,.0f} in {urgent.get('category', 'unknown')}. This requires immediate attention to maintain financial stability.",
                "severity": "high",
                "category": "warning",
                "is_anomaly_tip": True
            })

    return {
        "income": round(monthly_income, 2),
        "expenses": round(total_expense, 2),
        "savings": round(savings, 2),
        "savings_percentage": round(savings_percentage, 2),
        "health_score": health_score,
        "top_categories": top_categories,
        "recent_transactions": recent_transactions,
        "anomalies": anomalies,
        "unread_anomalies_count": unread_anomalies_count,
        "urgent_anomalies": [
            {
                "category": a.get("category", ""),
                "amount": a.get("amount", 0),
                "reason": a.get("reason", ""),
                "date": a.get("date", "")
            }
            for a in urgent_anomalies[:3]
        ],
        "alerts": alerts,
        "tips": tips,
        "user_profile": user_profile
    }

# ---------------- HELPERS ---------------- #
def calculate_health_score(savings_percentage, total_expense, monthly_income, user_profile, all_txns):
    """
    Financial health score (0–100) - Considers user profile and family context
    """
    score = 0
    family_size = user_profile.get("family_size", 1)
    
    # Adjust expectations based on family size
    # Single person: higher savings expected
    # Family: more expenses expected, adjust thresholds
    if family_size == 1:
        savings_thresholds = [30, 20, 10, 0]  # Higher expectations
        expense_thresholds = [50, 70, 90]
    elif family_size <= 3:
        savings_thresholds = [25, 15, 8, 0]  # Moderate expectations
        expense_thresholds = [60, 80, 95]
    else:  # 4+ members
        savings_thresholds = [20, 10, 5, 0]  # More lenient
        expense_thresholds = [70, 85, 98]

    # 1. Savings Discipline (40 points)
    if savings_percentage >= savings_thresholds[0]:
        score += 40
    elif savings_percentage >= savings_thresholds[1]:
        score += 30
    elif savings_percentage >= savings_thresholds[2]:
        score += 20
    elif savings_percentage >= savings_thresholds[3]:
        score += 10
    else:
        # Negative savings - penalty
        score += max(0, 10 + int(savings_percentage))

    # 2. Spending Discipline (30 points)
    if monthly_income > 0:
        expense_ratio = (total_expense / monthly_income) * 100
        if expense_ratio <= expense_thresholds[0]:
            score += 30
        elif expense_ratio <= expense_thresholds[1]:
            score += 20
        elif expense_ratio <= expense_thresholds[2]:
            score += 10
        else:
            # Spending exceeds income significantly
            score += max(0, 10 - int((expense_ratio - 100) / 10))

    # 3. Expense Consistency (15 points)
    # Check for recent anomalies
    anomalies_col = transactions_col.database["anomalies"]
    user_id = str(user_profile.get("user_id", ""))
    if user_id:
        recent_anomalies_count = anomalies_col.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": datetime.now() - timedelta(days=30)}
        })
        if recent_anomalies_count == 0:
            score += 15
        elif recent_anomalies_count <= 2:
            score += 10
        elif recent_anomalies_count <= 5:
            score += 5

    # 4. Category Balance (15 points)
    # Check if spending is distributed or concentrated
    if len(all_txns) >= 5:
        category_data = {}
        for t in all_txns:
            cat = t.get("category", "other")
            category_data[cat] = category_data.get(cat, 0) + t.get("amount", 0)
        
        if total_expense > 0:
            # Calculate diversity (more categories = better balance)
            category_count = len(category_data)
            max_category_ratio = max([v / total_expense for v in category_data.values()]) if category_data else 1
            
            # Reward diverse spending, penalize over-concentration
            if category_count >= 5 and max_category_ratio < 0.5:
                score += 15
            elif category_count >= 3 and max_category_ratio < 0.7:
                score += 10
            elif category_count >= 2:
                score += 5

    return min(max(0, score), 100)
