from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx
import jwt
import hashlib
from datetime import datetime

app = FastAPI(title="Interoperability Gateway")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REV_SECRET = "dept_revenue_secret_key"
ACAD_SECRET = "dept_academic_secret_key"

@app.post("/api/v1/scholarship-check")
async def verify_scholarship(request: dict):
    citizen_id = request.get("citizen_id")
    consent = request.get("consent", {})

    # 1. ABAC: Purpose Limitation Check (DPDP Act 2023)
    if consent.get("purpose") != "NSP_SCHOLARSHIP_2026" or not consent.get("active", False):
        raise HTTPException(status_code=403, detail="Consent denied, expired, or purpose mismatch.")

    # 2. Ephemeral Fetch from Mock Registries
    try:
        async with httpx.AsyncClient() as client:
            rev_resp = await client.get(f"http://127.0.0.1:8001/tax/v1/assessment/{citizen_id}")
            acad_resp = await client.get(f"http://127.0.0.1:8002/board/v2/students/{citizen_id}")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Upstream Department Service unreachable.")

    if rev_resp.status_code != 200 or acad_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Upstream verification failed.")

    # 3. Cryptographic Verification of JWS
    try:
        rev_payload = jwt.decode(rev_resp.json()["signed_jws"], REV_SECRET, algorithms=["HS256"])["data"]
        acad_payload = jwt.decode(acad_resp.json()["signed_jws"], ACAD_SECRET, algorithms=["HS256"])["data"]
    except Exception:
        raise HTTPException(status_code=401, detail="Cryptographic signature verification failed.")

    # 4. Semantic Normalization & Data Minimization (Zero-Knowledge Boolean)
    income_valid = rev_payload["gross_annual_income"] < 250000
    marks_valid = acad_payload["marks_percentage"] >= 75.0
    is_eligible = income_valid and marks_valid

    # 5. Tamper-evident Audit Hash
    audit_string = f"{citizen_id}:{datetime.utcnow().isoformat()}:{is_eligible}"
    audit_hash = hashlib.sha256(audit_string.encode()).hexdigest()

    return {
        "citizen_id": citizen_id,
        "verification_result": {
            "income_criteria_met": income_valid,
            "merit_criteria_met": marks_valid,
            "overall_eligible": is_eligible
        },
        "audit_proof": f"SHA256:{audit_hash}"
    }

# Serve interactive dashboard UI directly
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("frontend/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
