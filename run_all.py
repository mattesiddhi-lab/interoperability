import os
import uvicorn
from fastapi import FastAPI
from gateway.gateway_service import app as gateway_app
from registries.revenue_service import app as revenue_app
from registries.academic_service import app as academic_app

# Main unified production wrapper
app = FastAPI()

# Mount registries internally
app.mount("/sub/revenue", revenue_app)
app.mount("/sub/academic", academic_app)

# Mount main gateway at root
app.mount("", gateway_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("run_all:app", host="0.0.0.0", port=port)
