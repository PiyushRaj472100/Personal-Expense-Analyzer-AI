# Smart Personal Expense Analyzer

A comprehensive full-stack application for tracking and analyzing personal expenses with AI-powered insights.

## Project Structure

```
Smart_Personal_Expense_Analyzer/
├── python/                    # Backend Python code
│   ├── backend/               # FastAPI backend
│   │   ├── main.py           # Main application entry point
│   │   ├── database.py       # MongoDB connection
│   │   └── routes/           # API routes
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── transactions.py
│   │       ├── dashboard.py
│   │       ├── analytics.py
│   │       └── profile.py
│   └── ai/                   # AI modules
│       ├── categorizer.py    # Expense categorization
│       ├── anomaly.py        # Anomaly detection
│       ├── tips_engine.py    # Financial tips generation
│       └── sms_parser.py     # SMS parsing
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── context/         # React context
│   ├── package.json
│   └── vite.config.js
└── requirements.txt          # Python dependencies
```

## Features

### Backend (Python/FastAPI)
- ✅ User authentication (JWT-based)
- ✅ Transaction management
- ✅ AI-powered expense categorization
- ✅ Anomaly detection for unusual spending
- ✅ SMS transaction parser
- ✅ Financial health scoring
- ✅ Personalized financial tips
- ✅ Analytics and reporting

### Frontend (React)
- ✅ Modern, responsive UI with TailwindCSS
- ✅ Authentication pages (Login/Signup)
- ✅ Dashboard with financial overview
- ✅ Transaction management (Add/Delete/SMS Parser)
- ✅ Analytics with interactive charts
- ✅ User profile management
- ✅ Mobile-friendly design

## Setup Instructions

### Backend Setup

1. Navigate to the python directory:
```bash
cd python
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `python/backend/` directory:
```env
MONGO_URI=mongodb://localhost:27017/
JWT_SECRET=your-secret-key-here
JWT_ALGO=HS256
```

5. Make sure MongoDB is running and accessible at the URI specified in `.env`

6. Run the backend server:
```bash
cd backend
python main.py
```

Or using uvicorn:
```bash
cd backend
uvicorn main:app --reload --port 5000
```

The API will be available at `http://localhost:5000`
API documentation: `http://localhost:5000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create a `.env` file if backend is not on default port:
```env
VITE_API_URL=http://localhost:5000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. Start the backend server (port 5000)
2. Start the frontend development server (port 3000)
3. Open `http://localhost:3000` in your browser
4. Create an account or login
5. Start adding transactions and explore the analytics!

## API Endpoints

- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/dashboard/` - Get dashboard data
- `GET /api/transactions/` - Get all transactions
- `POST /api/transactions/add` - Add transaction
- `POST /api/transactions/from-sms` - Parse and add from SMS
- `DELETE /api/transactions/{id}` - Delete transaction
- `GET /api/analytics/?period={weekly|monthly|yearly}` - Get analytics
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/` - Update user profile

## Technologies Used

### Backend
- FastAPI
- MongoDB (PyMongo)
- JWT authentication
- Python AI/ML libraries

### Frontend
- React 18
- Vite
- TailwindCSS
- React Router
- Recharts
- Axios
- Lucide React

## Notes

- The backend must be running before starting the frontend
- Make sure MongoDB is properly configured and accessible
- JWT tokens expire after 7 days
- All transaction amounts are stored in the currency specified (default: INR/₹)

## License

This project is part of a portfolio project.

