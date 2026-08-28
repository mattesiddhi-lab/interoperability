import jwt

SECRET_KEY = "dept_revenue_secret_key"

MOCK_REVENUE_DB = {
    "CITIZEN_101": {"gross_annual_income": 180000, "status": "ASSESSED"},
    "CITIZEN_102": {"gross_annual_income": 450000, "status": "ASSESSED"}
}

def get_tax_record(citizen_id: str):
    record = MOCK_REVENUE_DB.get(citizen_id, {"gross_annual_income": 999999, "status": "NOT_FOUND"})
    signed_jwt = jwt.encode(
        payload={"data": record, "iss": "REVENUE_DEPT_MH"},
        key=SECRET_KEY,
        algorithm="HS256"
    )
    return {"department": "Revenue Dept", "signed_jws": signed_jwt}
