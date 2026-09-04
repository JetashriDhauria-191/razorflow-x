import os
import sys
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.main import app
except (ImportError, ModuleNotFoundError):
    from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Razorflow X Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
