# How to Test Anomaly Popup

## 🎯 Quick Steps to Trigger Anomaly Popup

### Prerequisites:
1. You need **at least 3 existing transactions** in your account (to establish spending patterns)
2. The backend server must be running
3. You must be logged in

---

## Method 1: Create High-Amount Transaction (Easiest)

### Steps:

1. **Add 3-5 Normal Transactions First:**
   - Go to Transactions page
   - Add some regular transactions like:
     - "Grocery Shopping" - ₹500 - Food & Groceries
     - "Coffee" - ₹150 - Food & Dining
     - "Bus Ticket" - ₹50 - Transportation
     - "Netflix Subscription" - ₹799 - Entertainment

2. **Then Add an Unusually High Amount:**
   - Add a transaction with an **exceptionally high amount** compared to your category average
   - Example: If your previous "Food & Groceries" transactions were ₹500-1000, add:
     - Title: "Premium Groceries"
     - Amount: **₹15,000** (or much higher than your average)
     - Category: Food & Groceries (or same category as your normal transactions)
     - Date: Today's date

3. **Check Dashboard:**
   - Navigate to Dashboard
   - The popup should appear automatically if anomaly is detected with **high severity**

---

## Method 2: Create Multiple Transactions in Same Category (Frequency Spike)

### Steps:

1. **Have 2-3 transactions in a category** (e.g., "Entertainment")

2. **Add 5+ transactions in the same category within 7 days:**
   - Add multiple "Entertainment" transactions quickly
   - This triggers a frequency spike detection
   - Example:
     - Day 1: "Movie Ticket" - ₹500 - Entertainment
     - Day 1: "Concert" - ₹2000 - Entertainment
     - Day 1: "Game Purchase" - ₹1500 - Entertainment
     - Day 2: "Theme Park" - ₹3000 - Entertainment
     - Day 2: "Bowling" - ₹800 - Entertainment

3. **Check Dashboard:**
   - The popup should appear showing frequency anomaly

---

## Method 3: Set High Income and Create Large Transaction

### Steps:

1. **Set your annual income in Profile:**
   - Go to Profile page
   - Set Annual Income to a reasonable amount (e.g., ₹6,00,000)
   - This means monthly income = ₹50,000

2. **Add a transaction > 30% of monthly income:**
   - Add transaction with amount > ₹15,000 (30% of ₹50,000)
   - This will trigger income-based anomaly detection
   - Example:
     - Title: "Emergency Purchase"
     - Amount: **₹20,000**
     - Category: Any category

3. **Check Dashboard:**
   - High-severity anomaly should be detected

---

## 🚨 What Makes an Anomaly "Urgent" (Triggers Popup)?

The popup appears for **high-severity anomalies** created in the **last 7 days**:
- **Severity**: "high" (score >= 0.8)
- **Created**: Within the last 7 days
- **Not dismissed**: You haven't dismissed it in this browser session

---

## 📊 Understanding Anomaly Scores

### Anomaly Detection Checks:

1. **Amount Anomaly:**
   - Compares amount to historical average for that category
   - Z-score > 2.5 = High anomaly
   - Z-score > 1.5 = Medium anomaly

2. **Category Anomaly:**
   - Checks if category spending ratio changed significantly
   - Ratio change > 15% triggers anomaly

3. **Frequency Anomaly:**
   - Compares transaction frequency (last 7 days vs previous 7 days)
   - 3x increase = High anomaly
   - 2x increase = Medium anomaly

**Combined Score:**
- Score >= 0.8 → **High Severity** → Triggers popup
- Score >= 0.6 → Medium Severity → Shows in anomalies section but no popup

---

## 🧪 Quick Test Scenario (Recommended)

1. **Add 3 normal transactions:**
   ```
   Transaction 1: "Grocery" - ₹1000 - Food & Groceries
   Transaction 2: "Restaurant" - ₹500 - Food & Dining  
   Transaction 3: "Uber" - ₹200 - Transportation
   ```

2. **Wait a moment, then add anomaly:**
   ```
   Transaction 4: "Luxury Shopping" - ₹50,000 - Shopping
   ```

3. **Go to Dashboard:**
   - Popup should appear immediately
   - Shows: "URGENT: Unusual spending detected..."

---

## 🔄 If Popup Doesn't Appear

### Troubleshooting:

1. **Clear session storage:**
   ```javascript
   // Open browser console (F12) and run:
   sessionStorage.removeItem('anomaly_popup_dismissed');
   // Then refresh the dashboard
   ```

2. **Check if anomaly was created:**
   - Look at Dashboard anomalies section
   - Check if transaction has red anomaly badge (⚠️) in Transactions page

3. **Verify anomaly severity:**
   - Anomaly must be **"high"** severity, not "medium" or "low"
   - Only high-severity anomalies trigger the popup

4. **Check anomaly date:**
   - Anomaly must be created within last 7 days
   - Older anomalies won't trigger popup

5. **Reload Dashboard:**
   - Refresh the page (F5 or Ctrl+R)
   - Or navigate away and back to Dashboard

---

## 🎨 What the Popup Shows

When triggered, the popup displays:
- ⚠️ **Red alert icon** and "Urgent Financial Alert" title
- **Top 3 urgent anomalies** with:
  - Category name
  - Amount (formatted in ₹)
  - Reason for anomaly
- **Two buttons:**
  - "I'll Review Later" (dismisses)
  - "View Details" (goes to Transactions page)

---

## 💡 Pro Tips

1. **For easier testing:**
   - Create transactions with amounts 5-10x higher than your average
   - Use the same category to make comparison obvious

2. **To see it again:**
   - Clear sessionStorage: `sessionStorage.removeItem('anomaly_popup_dismissed')`
   - Or wait 1 hour (auto-reset)

3. **Check anomaly badge:**
   - Transactions with anomalies show ⚠️ badge in Transactions table
   - Red = High severity, Yellow = Medium severity

4. **View all anomalies:**
   - Dashboard shows all anomalies in the "Spending Anomalies" section
   - Popup only shows urgent (high-severity) ones

---

## ✅ Success Indicators

You'll know it's working when:
- ✅ Popup appears automatically on Dashboard load
- ✅ Red badge (⚠️) shows on anomalous transaction
- ✅ "Spending Anomalies" section appears on Dashboard
- ✅ Anomaly details show correct reason and severity

---

Happy Testing! 🚀
