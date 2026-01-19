# Adaptive Learning System - How It Works

## ✅ **ISSUE IDENTIFIED**

Your model **WAS learning**, but the categorizer **wasn't using** the learned data! 

I've now implemented **real-time adaptive learning** that actually uses your feedback.

---

## 🔄 **How Adaptive Learning Works Now**

### **Before (The Problem):**
1. ✅ User selects category → Feedback stored in MongoDB
2. ❌ Categorizer **never loaded** this feedback
3. ❌ Next transaction → Still uses old static keywords

### **After (The Fix):**
1. ✅ User selects category → Feedback stored in MongoDB
2. ✅ **Categorizer loads user keywords in real-time**
3. ✅ Next transaction → **Uses learned keywords!**

---

## 🎯 **How to Test Adaptive Learning**

### **Step 1: Add a Transaction with Manual Category Selection**

1. Go to Transactions page
2. Click "Add Transaction"
3. Fill in:
   - Title: "chocolates at dinner"
   - Amount: ₹500
   - **Category: Select "Food & Dining"** (manually select from dropdown)
   - Date: Today
4. Click "Add"

**What happens:**
- Transaction is saved
- Feedback is stored: "chocolates at dinner" → "Food & Dining"
- Keywords are learned: "chocolates at dinner" → "dining" category

### **Step 2: Add Another Transaction (Auto-detect should learn!)**

1. Add a new transaction:
   - Title: "chocolates" (or "chocolates at night")
   - Amount: ₹300
   - **Category: Leave empty or select "Auto-detect"**
   - Date: Today
2. Click "Add"

**Expected Result:**
- AI should now categorize it as **"Food & Dining"** (or "dining")
- Method should show: **"learned_keyword"**
- Confidence: **98%** (high confidence for learned keywords)

---

## 📊 **Category Name Mapping**

**Frontend Categories** → **Backend Categories:**
- "Food & Dining" → `"food & dining"` (stored in DB)
- "Food & Groceries" → `"food & groceries"`
- "Transportation" → `"transportation"`
- "Other" → `"other"` (requires custom category name)

**Note:** Category names are normalized to lowercase for matching.

---

## 🔍 **How It Learns**

### **Learning Mechanism:**

1. **When you manually select a category:**
   - Title: "chocolates at dinner"
   - Category: "Food & Dining"
   - System learns: "chocolates at dinner" → "food & dining"

2. **Keywords are extracted:**
   - The entire title is added as a keyword
   - Partial matches also work (e.g., "chocolates" matches "chocolates at dinner")

3. **Priority System:**
   - **Learned keywords** have **HIGHEST priority** (checked first)
   - Static keywords (like "restaurant", "zomato") come second
   - Semantic matching comes last

### **Example Learning Sequence:**

```
Transaction 1:
  Title: "chocolates at dinner"
  Category: "Food & Dining" (manual selection)
  → Learns: "chocolates at dinner" → "food & dining"

Transaction 2:
  Title: "chocolates"
  Category: Auto-detect
  → Should match: "chocolates" (partial match)
  → Result: "food & dining" (learned!)
```

---

## 🧪 **Testing Checklist**

### **Test 1: Basic Learning**
- [ ] Add transaction with manual category selection
- [ ] Add another transaction with similar text (auto-detect)
- [ ] Verify it uses the learned category

### **Test 2: Multiple Keywords**
- [ ] Add 3 transactions with same keyword but different variations
- [ ] All should learn the same category
- [ ] New transactions should match all variations

### **Test 3: Category Correction**
- [ ] Let AI categorize incorrectly
- [ ] Manually correct it
- [ ] Add similar transaction → Should use corrected category

---

## 🔧 **Technical Details**

### **Files Changed:**

1. **`python/ai/adaptive_categorizer.py`** (NEW)
   - Extends `SemanticCategorizer`
   - Loads user keywords from MongoDB
   - Uses learned keywords with highest priority

2. **`python/backend/services/ai_service.py`**
   - Uses `AdaptiveCategorizer` instead of `SemanticCategorizer`
   - Passes `user_id` to categorizer

3. **`python/backend/routes/transactions.py`**
   - Stores feedback for ALL manual category selections
   - Refreshes cache after storing feedback

### **Data Storage:**

**MongoDB Collection: `user_categories`**
```javascript
{
  "user_id": "user123",
  "category": "food & dining",
  "keywords": ["chocolates at dinner", "chocolates", "chocolates at night"],
  "updated_at": ISODate("2024-01-15T...")
}
```

---

## ⚠️ **Important Notes**

1. **Learning is User-Specific:**
   - Each user has their own learned keywords
   - Keywords are not shared between users

2. **Real-Time Learning:**
   - Keywords are loaded **every time** you categorize
   - Cache is refreshed after storing new feedback
   - No need to restart server

3. **Priority Order:**
   1. **Learned keywords** (user-specific) - Highest priority
   2. Static keywords (hardcoded) - Medium priority
   3. Semantic matching (embeddings) - Fallback

4. **Category Name Matching:**
   - Frontend: "Food & Dining"
   - Backend: "food & dining" (lowercase)
   - Matching is case-insensitive

---

## 🐛 **Troubleshooting**

### **Issue: Learning doesn't work**

**Check:**
1. Did you **manually select** a category (not auto-detect)?
2. Is the category **not "Other"** (custom categories also work)?
3. Did you check the **next transaction** (not the same one)?
4. Is MongoDB accessible?

**Debug:**
```javascript
// Check if keywords are stored (MongoDB):
db.user_categories.find({user_id: "your_user_id"})

// Should show:
{
  "category": "food & dining",
  "keywords": ["chocolates at dinner", ...]
}
```

### **Issue: Still categorizes incorrectly**

**Possible reasons:**
1. Title doesn't match learned keywords (exact or partial)
2. Category name mismatch (check case-insensitive matching)
3. Cache not refreshed (restart backend server)

---

## ✅ **Success Indicators**

You'll know it's working when:
- ✅ Adding similar transaction → Uses learned category
- ✅ Method shows: "learned_keyword" (instead of "keyword" or "semantic")
- ✅ Confidence: 98% (high for learned keywords)
- ✅ Category matches your previous manual selection

---

## 🚀 **Next Steps**

1. **Restart backend server** (to load AdaptiveCategorizer)
2. **Add transaction with manual category** ("chocolates" → "Food & Dining")
3. **Add another transaction** (auto-detect "chocolates")
4. **Verify it learned!** (should categorize as "Food & Dining")

---

**The system is now learning from your feedback in real-time!** 🎉
