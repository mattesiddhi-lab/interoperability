import jwt

SECRET_KEY = "dept_academic_secret_key"

MOCK_ACADEMIC_DB = {
    "CITIZEN_101": {"marks_percentage": 85.0, "result": "PASSED_WITH_HONORS"},
    "CITIZEN_102": {"marks_percentage": 62.0, "result": "FIRST_CLASS"}
}

def get_student_record(citizen_id: str):
    record = MOCK_ACADEMIC_DB.get(citizen_id, {"marks_percentage": 0.0, "result": "FAIL"})
    signed_jwt = jwt.encode(
        payload={"data": record, "iss": "ACADEMIC_BOARD_MH"},
        key=SECRET_KEY,
        algorithm="HS256"
    )
    return {"department": "Academic Board", "signed_jws": signed_jwt}
