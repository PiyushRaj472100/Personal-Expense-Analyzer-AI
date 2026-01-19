# Quick Start Guide - Fix CORS and Run Project

## 🚨 CRITICAL: Fix CORS Errors

### Step 1: Restart Backend Server (REQUIRED)

The CORS configuration has been updated. You **MUST** restart your backend server:

**Windows (PowerShell):**
```powershell
cd python\backend
python run_server.py
```

**Or using uvicorn:**
```powershell
cd python\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Mac/Linux:**
```bash
cd python/backend
python run_server.py
```

### Step 2: Verify Backend is Running

Open browser: http://localhost:8000/api/health

Should see: `{"status": "healthy"}`

### Step 3: Start Frontend

In a **new terminal window**:
```bash
cd frontend
npm run dev
```

### Step 4: Test the Connection

1. Open frontend in browser (usually http://localhost:3001)
2. Log in
3. Check browser console (F12) - should NOT see CORS errors
4. Dashboard should load data

## ✅ What Was Fixed

1. **CORS Configuration Updated**
   - Added support for ports 3000, 3001, 5173
   - Fixed allow_origins to work with credentials
   - Added OPTIONS handler for preflight requests

2. **Error Handling Improved**
   - Better error messages
   - CORS headers always sent

3. **Server Startup Script**
   - Created `run_server.py` for easy startup

## 📝 If Still Having Issues

1. **Make sure backend is actually running** - Check terminal for "Uvicorn running on..."
2. **Clear browser cache** - Ctrl+Shift+Delete or Cmd+Shift+Delete
3. **Hard refresh** - Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
4. **Check both servers are running** - Backend (8000) AND Frontend (3001)
5. **Verify MongoDB is running** (if using local MongoDB)

## 🔍 Troubleshooting

**Error: "Connection refused"**
→ Backend is not running. Start it with Step 1.

**Error: Still seeing CORS errors**
→ You didn't restart the backend. Stop it (Ctrl+C) and restart.

**Error: "401 Unauthorized"**
→ This is NOT a CORS issue. You need to log in first.

**Error: "Failed to fetch"**
→ Check if backend is accessible at http://localhost:8000/api/health

## 📞 Need More Help?

See `CORS_FIX_GUIDE.md` for detailed troubleshooting steps.
