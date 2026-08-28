import os
import hashlib
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import jwt

from registries.revenue_service import get_tax_record
from registries.academic_service import get_student_record

app = FastAPI(title="Interoperability Gateway")

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

    # 1. ABAC: Validate Purpose and Active Consent
    if consent.get("purpose") != "NSP_SCHOLARSHIP_2026" or not consent.get("active", False):
        raise HTTPException(status_code=403, detail="Consent denied, expired, or purpose mismatch.")

    # 2. Ephemeral Fetch from Registries
    try:
        rev_resp = get_tax_record(citizen_id)
        acad_resp = get_student_record(citizen_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Registry Error: {str(e)}")

    # 3. Cryptographic Verification of JWS Signatures
    try:
        rev_payload = jwt.decode(rev_resp["signed_jws"], REV_SECRET, algorithms=["HS256"])["data"]
        acad_payload = jwt.decode(acad_resp["signed_jws"], ACAD_SECRET, algorithms=["HS256"])["data"]
    except Exception:
        raise HTTPException(status_code=401, detail="Cryptographic verification failed.")

    # 4. Semantic Normalization & Data Minimization (Zero-Knowledge Output)
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

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(base_dir, "frontend", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Interoperability Gateway Active. Frontend file missing.</h1>"
