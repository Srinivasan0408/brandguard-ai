import uvicorn
import os
import sys

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting BrandGuard AI Backend on http://127.0.0.1:{port} ...")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=port, reload=True)
