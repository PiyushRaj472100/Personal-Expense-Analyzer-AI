# backend/main.py

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.routes.auth import auth_router
from backend.routes.profile import profile_router
from backend.routes.transactions import transactions_router
from backend.routes.dashboard import dashboard_router
from backend.routes.analytics import analytics_router
from backend.routes.feedback import feedback_router

app = FastAPI(title="Smart Expense Analyzer API")

# CORS Middleware - MUST be added before routers
# Note: When allow_credentials=True, cannot use "*" for origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global exception handler to ensure CORS headers are always sent
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are sent even on errors"""
    print(f"Error occurred: {str(exc)}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if os.getenv("DEBUG", "False").lower() == "true" else "An error occurred"
        },
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers"""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        }
    )

# ✅ ROUTERS (MATCH FRONTEND)
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["AI Feedback"])


@app.get("/")
def root():
    return {
        "message": "Smart Expense Analyzer API Running",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle OPTIONS requests for CORS preflight"""
    return {"message": "OK"}
