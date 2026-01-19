# backend/database.py

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

# This file is inside backend/, so load backend/.env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

# --------------------------------------------------
# MongoDB Configuration
# --------------------------------------------------

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "smart_expense_analyzer")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not found in backend/.env")

# --------------------------------------------------
# MongoDB Client (singleton)
# --------------------------------------------------

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# --------------------------------------------------
# Collections
# --------------------------------------------------

users_col = db["users"]
profiles_col = db["profiles"]
transactions_col = db["transactions"]
alerts_col = db["alerts"]
ai_feedback_col = db["ai_feedback"]

# 🔥 NEW: User-defined category learning
# Stores custom categories taught by users
user_categories_col = db["user_categories"]
