# Complete Setup Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** and npm installed
3. **MongoDB** installed and running (or MongoDB Atlas connection string)

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to project root
cd Smart_Personal_Expense_Analyzer

# Go to python directory
cd python

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Navigate to backend
cd backend

# Create .env file with your configuration
# Windows (PowerShell):
@"
MONGO_URI=mongodb://localhost:27017/
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGO=HS256
"@ | Out-File -FilePath .env -Encoding utf8

# Mac/Linux:
cat > .env << EOF
MONGO_URI=mongodb://localhost:27017/
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGO=HS256
EOF

# Run the backend server
python main.py
```

The backend will run on `http://localhost:5000`

### 2. Frontend Setup

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd Smart_Personal_Expense_Analyzer/frontend

# Install dependencies
npm install

# (Optional) Create .env file if backend is not on default port
# Windows:
@"
VITE_API_URL=http://localhost:5000
"@ | Out-File -FilePath .env -Encoding utf8

# Mac/Linux:
echo "VITE_API_URL=http://localhost:5000" > .env

# Start development server
npm run dev
```

The frontend will run on `http://localhost:3000`

### 3. Access the Application

1. Open your browser and go to: `http://localhost:3000`
2. Create a new account or login
3. Start adding transactions!

## Troubleshooting

### Backend Issues

**Issue: Module not found errors**
- Make sure you're running from the `python/backend/` directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Issue: MongoDB connection error**
- Make sure MongoDB is running: `mongod` or check MongoDB service
- Verify MONGO_URI in `.env` file is correct
- For MongoDB Atlas, use the connection string format: `mongodb+srv://`

**Issue: JWT_SECRET error**
- Make sure `.env` file exists in `python/backend/` directory
- Verify JWT_SECRET is set in `.env`

### Frontend Issues

**Issue: Cannot connect to backend**
- Make sure backend is running on port 5000
- Check browser console for CORS errors
- Verify `VITE_API_URL` in frontend `.env` matches backend URL

**Issue: npm install fails**
- Try deleting `node_modules` and `package-lock.json`, then run `npm install` again
- Make sure you're using Node.js 18+

**Issue: Port already in use**
- Change the port in `vite.config.js` or kill the process using port 3000

## Project Structure Summary

```
Smart_Personal_Expense_Analyzer/
├── python/                  # Backend Python code
│   ├── backend/            # FastAPI backend
│   │   ├── main.py        # Run this to start backend
│   │   ├── .env           # Create this with MongoDB URI and JWT secret
│   │   └── routes/        # API endpoints
│   └── ai/                # AI modules
├── frontend/              # React frontend
│   ├── src/              # Source code
│   ├── package.json      # Dependencies
│   └── .env              # Optional: API URL config
└── requirements.txt       # Python dependencies
```

## API Endpoints

Once backend is running, check:
- API: http://localhost:5000
- API Docs: http://localhost:5000/docs (Interactive Swagger UI)
- Health Check: http://localhost:5000/api/health

## Production Deployment

For production:
1. Change `JWT_SECRET` to a strong random string
2. Update CORS origins in `backend/main.py` to your frontend domain
3. Use environment variables for all sensitive data
4. Build frontend: `npm run build` in frontend directory
5. Serve static files or use a hosting service

## Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Verify all prerequisites are installed
3. Ensure MongoDB is running
4. Check that ports 3000 and 5000 are available

