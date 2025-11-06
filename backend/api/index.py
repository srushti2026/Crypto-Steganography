"""
Vercel Serverless Function Entry Point for VeilForge Steganography API
This file adapts the enhanced_app.py FastAPI application for Vercel's serverless environment.

Vercel expects a simple handler function that returns the FastAPI app instance.
All imports and dependencies must be properly configured for serverless execution.
"""

import os
import sys
from pathlib import Path

# Configure paths for Vercel serverless environment
# In Vercel, the source files are in the project root, not in the api folder
current_dir = Path(__file__).parent  # /api directory
parent_dir = current_dir.parent      # project root directory

# Add parent directory to Python path for module imports
sys.path.insert(0, str(parent_dir))

# Set working directory to parent for file operations
os.chdir(parent_dir)

# Load environment variables (for local development)
# In production, Vercel provides environment variables directly
try:
    from env_loader import load_env_file, validate_required_env_vars
    load_env_file()
    validate_required_env_vars()
except ImportError:
    print("⚠️ Environment loader not available - using system environment variables")

# Environment configuration for Vercel deployment
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('TEMP_DIR', '/tmp')

try:
    # Import the main FastAPI application from the parent directory
    from app import app
    
    # Configure the app for serverless environment
    # Remove static file mounting as Vercel handles static files separately
    app.mount_static_disabled = True
    
    print("✅ Successfully imported FastAPI app for Vercel deployment")
    
except ImportError as e:
    print(f"❌ Failed to import FastAPI app: {e}")
    # Create a minimal fallback app if import fails
    from fastapi import FastAPI
    
    app = FastAPI(title="VeilForge API - Import Error", version="1.0.0")
    
    @app.get("/api/health")
    async def health_check():
        return {"status": "error", "message": f"Import error: {str(e)}"}

# Export the app instance for Vercel
# This is the main entry point that Vercel will use
handler = app