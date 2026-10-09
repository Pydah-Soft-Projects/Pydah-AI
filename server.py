import sys
import os
import uvicorn

# Ensure src module is on Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import Config

if __name__ == "__main__":
    try:
        config = Config.load()
        print("=" * 60)
        print(" Starting AI Core Service API Server")
        print(f" Configured Model: {config.model}")
        print(" Endpoint: http://localhost:8000/api/v1/chat")
        print(" Swagger Docs: http://localhost:8000/docs")
        print("=" * 60)
    except Exception as e:
        print(f"Starting API Server with default configuration ({e})")

    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
