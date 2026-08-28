from fastapi import FastAPI
import jwt
import uvicorn

app = FastAPI(title="Academic Examination Board API")

SECRET_SIGNING_KEY = "dept_academic_secret_key"

MOCK_ACADEMIC_DB = {
    "CITIZEN_101": {"marks_percentage": 85.0, "result": "PASSED_WITH_HONORS"},
    "CITIZEN_102": {"marks_percentage": 62.0, "result": "FIRST_CLASS"}
}

@app.get("/board/v2/students/{citizen_id}")
def get_student_data(citizen_id: str):
    record = MOCK_ACADEMIC_DB.get(citizen_id, {"marks_percentage": 0.0, "result": "FAIL"})
    
    signed_jwt = jwt.encode({"data": record, "iss": "ACADEMIC_BOARD"}, SECRET_SIGNING_KEY, algorithm="HS256")
    return {"department": "Academic Board", "signed_jws": signed_jwt}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
