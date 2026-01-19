# Project Structure

This document outlines the complete file structure of the Smart Personal Expense Analyzer project.

## Root Directory

```
Smart_Personal_Expense_Analyzer/
├── python/                    # All Python backend code
├── frontend/                  # React frontend application
├── README.md                  # Main project documentation
├── SETUP.md                   # Detailed setup instructions
├── PROJECT_STRUCTURE.md       # This file
└── requirements.txt           # Python dependencies (for reference)
```

## Python Backend (`python/`)

```
python/
├── backend/
│   ├── main.py               # FastAPI application entry point
│   ├── database.py           # MongoDB connection and collections
│   ├── db_test.py            # Database testing utilities
│   ├── .env                  # Environment variables (create this)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication endpoints (signup, login)
│   │   ├── transactions.py   # Transaction CRUD operations
│   │   ├── dashboard.py      # Dashboard data endpoint
│   │   ├── analytics.py      # Analytics and insights
│   │   └── profile.py        # User profile management
│   └── __pycache__/          # Python cache (auto-generated)
├── ai/
│   ├── __init__.py
│   ├── categorizer.py        # Expense categorization logic
│   ├── anomaly.py            # Anomaly detection algorithms
│   ├── tips_engine.py        # Financial tips generation
│   ├── sms_parser.py         # SMS transaction parser
│   └── train_models.ipynb    # Model training notebook (optional)
├── requirements.txt          # Python dependencies
└── README.md                 # Backend-specific documentation
```

## Frontend (`frontend/`)

```
frontend/
├── src/
│   ├── main.jsx              # React entry point
│   ├── App.jsx               # Main app component with routing
│   ├── index.css             # Global styles with TailwindCSS
│   ├── components/
│   │   └── Layout.jsx        # Main layout with sidebar navigation
│   ├── pages/
│   │   ├── Login.jsx         # Login page
│   │   ├── Signup.jsx        # Registration page
│   │   ├── Dashboard.jsx     # Dashboard page
│   │   ├── Transactions.jsx  # Transaction management page
│   │   ├── Analytics.jsx     # Analytics and charts page
│   │   └── Profile.jsx       # User profile settings page
│   ├── services/
│   │   └── api.js            # API service layer (Axios config)
│   └── context/
│       └── AuthContext.jsx   # Authentication context provider
├── index.html                # HTML template
├── package.json              # Node.js dependencies
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # TailwindCSS configuration
├── postcss.config.js         # PostCSS configuration
├── .eslintrc.cjs             # ESLint configuration
├── .gitignore                # Git ignore rules
├── .env.example              # Environment variables example
├── .env                      # Environment variables (create this)
└── README.md                 # Frontend-specific documentation
```

## Key Files Description

### Backend

- **`python/backend/main.py`**: FastAPI application, CORS setup, route registration
- **`python/backend/database.py`**: MongoDB connection and collection definitions
- **`python/backend/routes/auth.py`**: JWT-based authentication endpoints
- **`python/backend/routes/transactions.py`**: Transaction management with AI categorization
- **`python/backend/routes/dashboard.py`**: Dashboard data aggregation
- **`python/backend/routes/analytics.py`**: Analytics data with time-based filtering
- **`python/backend/routes/profile.py`**: User profile CRUD operations
- **`python/ai/categorizer.py`**: Rule-based expense categorization
- **`python/ai/anomaly.py`**: Spending anomaly detection
- **`python/ai/tips_engine.py`**: Personalized financial tips generation

### Frontend

- **`frontend/src/App.jsx`**: React Router setup with protected routes
- **`frontend/src/components/Layout.jsx`**: Responsive sidebar layout with navigation
- **`frontend/src/pages/Dashboard.jsx`**: Financial overview with stats and tips
- **`frontend/src/pages/Transactions.jsx`**: Transaction list, add, delete, SMS parser
- **`frontend/src/pages/Analytics.jsx`**: Charts and visualizations using Recharts
- **`frontend/src/pages/Profile.jsx`**: User profile management
- **`frontend/src/services/api.js`**: Centralized API client with interceptors
- **`frontend/src/context/AuthContext.jsx`**: Authentication state management

## Environment Variables

### Backend (`.env` in `python/backend/`)
```
MONGO_URI=mongodb://localhost:27017/
JWT_SECRET=your-secret-key
JWT_ALGO=HS256
```

### Frontend (`.env` in `frontend/`)
```
VITE_API_URL=http://localhost:5000
```

## Running the Application

1. **Backend**: Run from `python/backend/` directory
   ```bash
   python main.py
   ```

2. **Frontend**: Run from `frontend/` directory
   ```bash
   npm run dev
   ```

## Ports

- Backend API: `http://localhost:5000`
- Frontend: `http://localhost:3000`
- API Documentation: `http://localhost:5000/docs`

