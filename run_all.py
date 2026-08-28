import os
import sys
import uvicorn

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gateway.gateway_service import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("gateway.gateway_service:app", host="0.0.0.0", port=port)
