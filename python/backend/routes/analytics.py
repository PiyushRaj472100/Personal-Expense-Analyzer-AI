from fastapi import APIRouter, HTTPException, Query, Depends, Header
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
from collections import defaultdict
import os
from dotenv import load_dotenv

from ..database import users_col, transactions_col
from ai.tips_engine import TipsEngine

# ---------------- CONFIG ---------------- #

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET not set in environment")

analytics_router = APIRouter()
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

# ---------------- HELPERS ---------------- #

def get_date_range(period: str):
    now = datetime.utcnow()

    if period == "weekly":
        return now - timedelta(days=7)
    elif period == "yearly":
        return now - timedelta(days=365)
    else:  # monthly
        return now.replace(day=1)

# ---------------- ROUTE ---------------- #

@analytics_router.get("/")
def analytics(
    period: str = Query("monthly", enum=["weekly", "monthly", "yearly"]),
    user=Depends(get_current_user)
):
    """
    Analytics endpoint:
    - category analysis
    - time trends
    - source analysis
    - AI summary (lightweight)
    """

    start_date = get_date_range(period).strftime("%Y-%m-%d")

    txns = list(transactions_col.find({
        "user_id": str(user["_id"]),
        "date": {"$gte": start_date}
    }))

    if not txns:
        return {
            "message": "No transactions found for this period",
            "data": {}
        }

    # ---------------- CATEGORY ANALYSIS ---------------- #
    category_totals = defaultdict(float)
    for t in txns:
        category_totals[t.get("category", "other")] += t.get("amount", 0)

    category_analysis = [
        {"category": k, "amount": round(v, 2)}
        for k, v in category_totals.items()
    ]

    # ---------------- SOURCE ANALYSIS ---------------- #
    source_totals = defaultdict(float)
    for t in txns:
        source_totals[t.get("source", "manual")] += t.get("amount", 0)

    source_analysis = [
        {"source": k, "amount": round(v, 2)}
        for k, v in source_totals.items()
    ]

    # ---------------- TIME TREND ---------------- #
    time_trend = defaultdict(float)
    for t in txns:
        time_trend[t["date"]] += t.get("amount", 0)

    time_trend_data = [
        {"date": k, "amount": round(v, 2)}
        for k, v in sorted(time_trend.items())
    ]

    # ---------------- USER PROFILE ---------------- #
    from ..database import profiles_col
    profile = profiles_col.find_one({"user_id": str(user["_id"])})
    if not profile:
        profile = {}
        if user.get("annual_income"):
            profile["annual_income"] = user.get("annual_income")
    
    user_profile = {
        "annual_income": profile.get("annual_income", user.get("annual_income", 0)),
        "family_members": profile.get("family_members", 1),
        "city": profile.get("city", ""),
        "has_pets": profile.get("has_pets", False),
        "family_size": profile.get("family_members", 1)
    }
    
    # Calculate monthly values
    monthly_income = user_profile["annual_income"] / 12 if user_profile["annual_income"] else 0
    total_spending = sum(category_totals.values())

    # ---------------- AI SUMMARY (ENHANCED) ---------------- #
    ai_summary = tips_engine.generate(
        user_profile=user_profile,
        transaction_history=txns,
        monthly_expense=total_spending,
        monthly_income=monthly_income
    )

    return {
        "period": period,
        "category_analysis": category_analysis,
        "source_analysis": source_analysis,
        "time_trend": time_trend_data,
        "ai_summary": ai_summary
    }
