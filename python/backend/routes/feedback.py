# backend/routes/feedback.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

from ..database import (
    transactions_col, 
    ai_feedback_col,
    user_categories_col
)
from .transactions import get_current_user   # ✅ FIXED RELATIVE IMPORT

feedback_router = APIRouter(prefix="/feedback", tags=["AI Feedback"])


# ---------------- SCHEMA ---------------- #

class FeedbackInput(BaseModel):
    transaction_id: str
    corrected_category: str | None = None
    corrected_intent: str | None = None
    corrected_emotion: str | None = None


# ---------------- ROUTE ---------------- #

@feedback_router.post("/")
def submit_feedback(
    data: FeedbackInput,
    user=Depends(get_current_user)
):
    """
    Store user feedback to improve AI predictions later
    """

    txn = transactions_col.find_one({
        "_id": ObjectId(data.transaction_id),
        "user_id": str(user["_id"])
    })

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    ai_analysis = txn.get("ai_analysis")
    if not ai_analysis:
        raise HTTPException(status_code=400, detail="No AI analysis found for this transaction")

    feedback_doc = {
        "user_id": str(user["_id"]),
        "transaction_id": data.transaction_id,
        "original_text": txn.get("title", ""),

        "ai_prediction": {
            "category": ai_analysis["category"].get("category"),
            "intent": ai_analysis["intent"].get("intent"),
            "emotion": ai_analysis["emotion"].get("emotion")
        },

        "user_correction": {
            "category": data.corrected_category,
            "intent": data.corrected_intent,
            "emotion": data.corrected_emotion
        },

        "confidence": {
            "category": ai_analysis["category"].get("confidence"),
            "intent": ai_analysis["intent"].get("confidence")
        },

        "created_at": datetime.utcnow()
    }

    ai_feedback_col.insert_one(feedback_doc)

    # 🔁 LEARNING: Store custom category for keyword expansion
    if data.corrected_category and data.corrected_category.lower() != "other":
        user_categories_col.update_one(
            {
                "user_id": str(user["_id"]),
                "category": data.corrected_category.lower()
            },
            {
                "$addToSet": {"keywords": txn.get("title", "").lower()},
                "$set": {
                    "user_id": str(user["_id"]),
                    "category": data.corrected_category.lower(),
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    return {
        "message": "Feedback recorded successfully",
        "status": "ok"
    }
