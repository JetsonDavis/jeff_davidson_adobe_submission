"""
Development server runner for Social Media Marketing Dashboard.
Run this from the backend directory: python run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
