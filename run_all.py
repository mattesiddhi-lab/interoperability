import os
import sys
import threading
import uvicorn

# Set root directory in Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from registries.revenue_service import app as revenue_app
from registries.academic_service import app as academic_app
from gateway.gateway_service import app as gateway_app

def start_revenue():
    uvicorn.run(revenue_app, host="127.0.0.1", port=8001, log_level="warning")

def start_academic():
    uvicorn.run(academic_app, host="127.0.0.1", port=8002, log_level="warning")

if __name__ == "__main__":
    # Start internal registries in background daemon threads
    t1 = threading.Thread(target=start_revenue, daemon=True)
    t2 = threading.Thread(target=start_academic, daemon=True)
    t1.start()
    t2.start()

    # Bind gateway to Render's public PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(gateway_app, host="0.0.0.0", port=port)
