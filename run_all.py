import os
import multiprocessing
import uvicorn

def run_revenue():
    uvicorn.run("registries.revenue_service:app", host="127.0.0.1", port=8001)

def run_academic():
    uvicorn.run("registries.academic_service:app", host="127.0.0.1", port=8002)

def run_gateway():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("gateway.gateway_service:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_revenue)
    p2 = multiprocessing.Process(target=run_academic)
    p3 = multiprocessing.Process(target=run_gateway)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
