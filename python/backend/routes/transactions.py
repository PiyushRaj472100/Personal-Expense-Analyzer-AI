from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import jwt
import re
import os
from bson import ObjectId
from dotenv import load_dotenv

from ..database import (
    transactions_col,
    users_col,
    profiles_col,
    alerts_col,
    ai_feedback_col,
    user_categories_col
)
from ..services.ai_service import AIService

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

transactions_router = APIRouter()
ai_service = AIService()

# --------------------------------------------------
# AUTH
# --------------------------------------------------
def get_current_user(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise Exception()

        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user = users_col.find_one({"_id": ObjectId(payload["user_id"])})

        if not user:
            raise Exception()

        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

# --------------------------------------------------
# SCHEMAS
# --------------------------------------------------
class TransactionCreate(BaseModel):
    title: str
    amount: float
    date: str
    source: str = "manual"
    category: Optional[str] = None

class SMSInput(BaseModel):
    message: str

# --------------------------------------------------
# SMS PARSER
# --------------------------------------------------
def parse_sms(message: str):
    amount = None
    merchant = None

    amt_match = re.search(r"(INR|₹)\s*([\d,]+\.?\d*)", message, re.I)
    if amt_match:
        amount = float(amt_match.group(2).replace(",", ""))

    merchant_match = re.search(r"(?:at|to)\s+([A-Za-z0-9\s&]+)", message)
    if merchant_match:
        merchant = merchant_match.group(1).strip()

    return amount, merchant

# --------------------------------------------------
# ROUTES
# --------------------------------------------------

# ✅ FIXED: FRONTEND EXPECTS { transactions: [...] }
@transactions_router.get("/")
def get_transactions(user=Depends(get_current_user)):
    data = list(
        transactions_col.find(
            {"user_id": str(user["_id"])},
            {"ai_analysis": 0}  # remove heavy field
        )
    )

    for tx in data:
        tx["_id"] = str(tx["_id"])

    return {
        "transactions": data
    }

# --------------------------------------------------
# ADD TRANSACTION
# --------------------------------------------------
@transactions_router.post("/add")
def add_transaction(data: TransactionCreate, user=Depends(get_current_user)):
    user_id = str(user["_id"])
    
    # Fetch user history for anomaly detection
    history = list(transactions_col.find(
        {"user_id": user_id},
        {"amount": 1, "category": 1, "date": 1, "_id": 0}
    ))
    
    # Fetch user profile
    profile = profiles_col.find_one({"user_id": user_id})
    if not profile:
        # Fallback to user document
        profile = {}
        if user.get("annual_income"):
            profile["annual_income"] = user.get("annual_income")
    
    # Build user profile dict
    user_profile = {
        "annual_income": profile.get("annual_income", user.get("annual_income", 0)),
        "family_members": profile.get("family_members", 1),
        "city": profile.get("city", ""),
        "has_pets": profile.get("has_pets", False),
        "family_size": profile.get("family_members", 1)
    }

    # AI Analysis with full context (including user_id for adaptive learning)
    ai_result = ai_service.analyze_transaction(
        text=data.title,
        amount=data.amount,
        category=data.category,  # Pass user-provided category if available
        date=data.date,
        user_profile=user_profile,
        history=history,
        user_id=user_id
    )

    ai_category = ai_result["category"]["category"]
    
    # Determine final category
    # If user provided category, use it (user input takes priority)
    user_category = data.category.lower().strip() if data.category else None
    user_selected_category = user_category if user_category else None
    
    # Use user category if provided, otherwise use AI category
    final_category = user_selected_category if user_selected_category else ai_category
    
    # Track if user corrected AI or selected a category manually
    user_corrected = user_selected_category and user_selected_category != ai_category.lower()

    # Check for anomaly
    anomaly_result = ai_result.get("anomaly", {})
    is_anomaly = anomaly_result.get("is_anomaly", False)
    anomaly_severity = anomaly_result.get("severity", "low")

    transaction = {
        "user_id": user_id,
        "title": data.title,
        "raw_text": data.title,
        "amount": data.amount,
        "category": final_category,
        "needs_user_confirmation": ai_result["category"]["needs_user_confirmation"],
        "ai_analysis": ai_result,
        "is_anomaly": is_anomaly,
        "anomaly_severity": anomaly_severity,
        "date": data.date,
        "source": data.source,
        "created_at": datetime.utcnow()
    }

    result = transactions_col.insert_one(transaction)
    transaction_id = str(result.inserted_id)

    # Store anomaly in MongoDB if detected
    if is_anomaly and anomaly_severity in ["medium", "high"]:
        anomalies_col = transactions_col.database["anomalies"]
        anomalies_col.insert_one({
            "user_id": user_id,
            "transaction_id": transaction_id,
            "amount": data.amount,
            "category": final_category,
            "anomaly_score": anomaly_result.get("score", 0.0),
            "severity": anomaly_severity,
            "reason": anomaly_result.get("reason", ""),
            "date": data.date,
            "created_at": datetime.utcnow()
        })
        
        # Create alert for high-severity anomalies
        if anomaly_severity == "high":
            alerts_col.insert_one({
                "user_id": user_id,
                "type": "anomaly",
                "message": f"⚠️ Anomaly detected: {anomaly_result.get('reason', 'Unusual spending pattern')}",
                "transaction_id": transaction_id,
                "created_at": datetime.utcnow()
            })

    # 🔁 Store feedback if user manually selected a category (learning)
    if user_selected_category:
        feedback_doc = {
            "user_id": user_id,
            "text": data.title,
            "ai_category": ai_category,
            "user_category": final_category,
            "confidence": ai_result["category"]["confidence"],
            "created_at": datetime.utcnow()
        }
        ai_feedback_col.insert_one(feedback_doc)
        
        # Store custom category for keyword learning
        if user_category and user_category != "other":
            user_categories_col.update_one(
                {
                    "user_id": user_id,
                    "category": final_category
                },
                {
                    "$addToSet": {"keywords": data.title.lower()},
                    "$set": {
                        "user_id": user_id,
                        "category": final_category,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Clear cache so next transaction uses updated keywords
            if hasattr(ai_service.categorizer, 'refresh_user_keywords'):
                ai_service.categorizer.refresh_user_keywords(user_id)

    # Build response with alert if anomaly detected
    response = {
        "message": "Transaction added",
        "transaction_id": transaction_id,
        "ai_analysis": ai_result
    }
    
    if is_anomaly and anomaly_severity in ["medium", "high"]:
        response["alert"] = f"⚠️ Anomaly detected: {anomaly_result.get('reason', 'Unusual spending pattern')}"

    return response

# --------------------------------------------------
# ADD FROM SMS
# --------------------------------------------------
@transactions_router.post("/from-sms")
def add_from_sms(data: SMSInput, user=Depends(get_current_user)):
    user_id = str(user["_id"])
    
    amount, merchant = parse_sms(data.message)
    if not amount:
        raise HTTPException(status_code=400, detail="Amount not found")

    title = merchant or "Unknown"
    tx_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Fetch user history and profile
    history = list(transactions_col.find(
        {"user_id": user_id},
        {"amount": 1, "category": 1, "date": 1, "_id": 0}
    ))
    
    profile = profiles_col.find_one({"user_id": user_id})
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

    # AI Analysis with full context (including user_id for adaptive learning)
    ai_result = ai_service.analyze_transaction(
        text=title,
        amount=amount,
        date=tx_date,
        user_profile=user_profile,
        history=history,
        user_id=user_id
    )

    anomaly_result = ai_result.get("anomaly", {})
    is_anomaly = anomaly_result.get("is_anomaly", False)
    anomaly_severity = anomaly_result.get("severity", "low")

    transaction = {
        "user_id": user_id,
        "title": title,
        "raw_text": data.message,
        "amount": amount,
        "category": ai_result["category"]["category"],
        "needs_user_confirmation": ai_result["category"]["needs_user_confirmation"],
        "ai_analysis": ai_result,
        "is_anomaly": is_anomaly,
        "anomaly_severity": anomaly_severity,
        "date": tx_date,
        "source": "sms",
        "created_at": datetime.utcnow()
    }

    result = transactions_col.insert_one(transaction)
    transaction_id = str(result.inserted_id)

    # Store anomaly if detected
    if is_anomaly and anomaly_severity in ["medium", "high"]:
        anomalies_col = transactions_col.database["anomalies"]
        anomalies_col.insert_one({
            "user_id": user_id,
            "transaction_id": transaction_id,
            "amount": amount,
            "category": ai_result["category"]["category"],
            "anomaly_score": anomaly_result.get("score", 0.0),
            "severity": anomaly_severity,
            "reason": anomaly_result.get("reason", ""),
            "date": tx_date,
            "created_at": datetime.utcnow()
        })
        
        if anomaly_severity == "high":
            alerts_col.insert_one({
                "user_id": user_id,
                "type": "anomaly",
                "message": f"⚠️ Anomaly detected: {anomaly_result.get('reason', 'Unusual spending pattern')}",
                "transaction_id": transaction_id,
                "created_at": datetime.utcnow()
            })

    response = {
        "message": "Transaction added from SMS",
        "transaction_id": transaction_id,
        "ai_analysis": ai_result
    }
    
    if is_anomaly and anomaly_severity in ["medium", "high"]:
        response["alert"] = f"⚠️ Anomaly detected: {anomaly_result.get('reason', 'Unusual spending pattern')}"

    return response