"""
Vercel serverless function entry point for Lisa AI Backend
"""
import sys
from pathlib import Path

# Add parent directory to path to import from main app
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

# Export the FastAPI app for Vercel
handler = app
