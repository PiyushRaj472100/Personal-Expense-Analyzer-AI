#!/usr/bin/env python3
"""
Server startup script for Smart Expense Analyzer API
Run this to start the FastAPI server with proper configuration
"""

import uvicorn
import os
import sys

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

if __name__ == "__main__":
    print("🚀 Starting Smart Expense Analyzer API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\n" + "="*50 + "\n")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",  # Allow connections from any IP
        port=8000,
        reload=True,  # Auto-reload on code changes
        reload_dirs=[BASE_DIR],  # Watch backend directory
        log_level="info"
    )
