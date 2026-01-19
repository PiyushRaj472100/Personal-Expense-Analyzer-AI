# CORS Fix Guide - Smart Expense Analyzer

## Issue
Frontend (localhost:3001) cannot connect to Backend (localhost:8000) due to CORS errors.

## Solution Steps

### 1. Stop and Restart Backend Server

**Important:** You MUST restart the backend server after CORS configuration changes.

**Option A: Using the new run script (Recommended)**
```bash
cd python/backend
python run_server.py
```

**Option B: Using uvicorn directly**
```bash
cd python/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Option C: If running from python directory**
```bash
cd python
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verify Backend is Running

Open your browser and go to:
- http://localhost:8000/api/health
- Should return: `{"status": "healthy"}`

If this doesn't work, the backend is not running properly.

### 3. Test CORS Configuration

Open browser console and run:
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

If you see CORS errors, the server needs to be restarted.

### 4. Check Frontend API URL

Make sure your frontend is using the correct API URL:
- Check `frontend/src/services/api.js`
- Should have: `const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';`

### 5. Verify Port Numbers

- **Backend:** Should run on port **8000** (default)
- **Frontend:** Can run on **3000**, **3001**, or **5173** (Vite default)

All these ports are now whitelisted in CORS configuration.

### 6. Common Issues and Fixes

#### Issue: "Connection refused"
**Fix:** Backend server is not running. Start it using step 1.

#### Issue: CORS errors still appear after restart
**Fix:** 
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Make sure you restarted the backend server (not just reloaded)

#### Issue: "401 Unauthorized" errors
**Fix:** This is not a CORS issue. You need to:
1. Log in through the frontend
2. Check that JWT token is being stored in localStorage
3. Verify JWT_SECRET in backend/.env matches

#### Issue: Frontend port is different (e.g., 5000)
**Fix:** Add your port to CORS origins in `python/backend/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5000",  # Add your port here
    # ... other origins
],
```

Then restart the backend server.

### 7. Development Setup Checklist

- [ ] Backend server is running on port 8000
- [ ] Backend .env file exists with MONGO_URI and JWT_SECRET
- [ ] MongoDB is running (if using local MongoDB)
- [ ] Frontend is running (npm run dev or similar)
- [ ] Frontend can access http://localhost:8000/api/health
- [ ] User is logged in (check localStorage for 'token')

### 8. Testing the Fix

1. Start backend: `cd python/backend && python run_server.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser to frontend URL (usually http://localhost:3001)
4. Log in if needed
5. Navigate to Dashboard
6. Check browser console - should NOT see CORS errors

## If Issues Persist

1. **Check backend logs** - Look for any error messages when starting the server
2. **Check frontend console** - Look for specific error messages
3. **Verify MongoDB connection** - Backend needs MongoDB to be accessible
4. **Check firewall/antivirus** - May be blocking localhost connections
5. **Try different browser** - Rule out browser-specific issues

## Production Notes

For production deployment, update CORS origins in `main.py` to only allow your production frontend URL:
```python
allow_origins=[
    "https://your-production-domain.com",
    # Remove localhost origins
],
```
