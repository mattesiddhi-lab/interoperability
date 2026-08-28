from fastapi import FastAPI
import jwt
import uvicorn

app = FastAPI(title="Revenue Department API")

SECRET_SIGNING_KEY = "dept_revenue_secret_key"

MOCK_REVENUE_DB = {
    "CITIZEN_101": {"gross_annual_income": 180000, "status": "ACTIVE"},
    "CITIZEN_102": {"gross_annual_income": 450000, "status": "ACTIVE"}
}

@app.get("/tax/v1/assessment/{citizen_id}")
def get_tax_data(citizen_id: str):
    record = MOCK_REVENUE_DB.get(citizen_id, {"gross_annual_income": 999999, "status": "NOT_FOUND"})
    
    # Sign payload with JWS (JSON Web Signature) to guarantee authenticity
    signed_jwt = jwt.encode({"data": record, "iss": "REVENUE_DEPT"}, SECRET_SIGNING_KEY, algorithm="HS256")
    return {"department": "Revenue Dept", "signed_jws": signed_jwt}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
