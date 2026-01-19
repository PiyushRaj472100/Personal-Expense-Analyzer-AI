# python/ai/adaptive_categorizer.py
"""
Adaptive Categorizer - Uses user feedback for real-time learning
Extends SemanticCategorizer with user-specific keyword learning
"""

import os
import sys
from typing import Dict, List, Optional

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai.categorizer import SemanticCategorizer


class AdaptiveCategorizer(SemanticCategorizer):
    """
    Adaptive categorizer that learns from user feedback.
    Loads user-specific keywords from MongoDB and uses them for categorization.
    """
    
    def __init__(self):
        super().__init__()
        # Will be set when we have database access
        self.user_keywords_cache = {}
        self._db_initialized = False
    
    def _init_db(self):
        """Initialize database connection for loading user keywords"""
        if self._db_initialized:
            return
        
        try:
            from backend.database import user_categories_col
            self.user_categories_col = user_categories_col
            self._db_initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize database for adaptive learning: {e}")
            self._db_initialized = False
    
    def _load_user_keywords(self, user_id: str) -> Dict[str, List[str]]:
        """
        Load user-specific learned keywords from MongoDB.
        Returns dict mapping category -> list of keywords
        """
        if not self._db_initialized:
            self._init_db()
        
        if not self._db_initialized:
            return {}
        
        # Check cache first
        if user_id in self.user_keywords_cache:
            return self.user_keywords_cache[user_id]
        
        try:
            # Load all user categories
            user_categories = list(self.user_categories_col.find({"user_id": user_id}))
            
            # Build keyword map
            learned_keywords = {}
            for uc in user_categories:
                category = uc.get("category", "").lower()
                keywords = uc.get("keywords", [])
                if category and keywords:
                    learned_keywords[category] = [kw.lower() for kw in keywords if kw]
            
            # Cache for this session
            self.user_keywords_cache[user_id] = learned_keywords
            return learned_keywords
            
        except Exception as e:
            print(f"Error loading user keywords: {e}")
            return {}
    
    def _clear_user_cache(self, user_id: Optional[str] = None):
        """Clear cache for a specific user or all users"""
        if user_id:
            self.user_keywords_cache.pop(user_id, None)
        else:
            self.user_keywords_cache.clear()
    
    def categorize(self, text: str, user_id: Optional[str] = None, threshold: float = 0.45):
        """
        Categorize text with adaptive learning.
        Uses both static keywords and user-learned keywords.
        
        Args:
            text: Transaction text to categorize
            user_id: Optional user ID to load user-specific keywords
            threshold: Confidence threshold
        """
        # Load user keywords if user_id provided
        user_keywords = {}
        if user_id:
            user_keywords = self._load_user_keywords(user_id)
        
        # Check user-learned keywords first (higher priority)
        if user_keywords:
            text_lower = text.lower()
            for category, keywords in user_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        return {
                            "category": category,
                            "confidence": 0.98,  # High confidence for learned keywords
                            "method": "learned_keyword",
                            "needs_user_confirmation": False,
                            "alternatives": [],
                            "learned": True  # Flag to indicate this was learned
                        }
        
        # Fall back to parent class (static keywords + semantic)
        return super().categorize(text, threshold)
    
    def get_user_keywords(self, user_id: str) -> Dict[str, List[str]]:
        """Get all learned keywords for a user"""
        return self._load_user_keywords(user_id)
    
    def refresh_user_keywords(self, user_id: str):
        """Refresh cached keywords for a user (call after new feedback)"""
        self._clear_user_cache(user_id)
