from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import v33lite

app = FastAPI()
security = HTTPBasic()

# Basic Auth setup
USERNAME = "user"
PASSWORD = "pass123"

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    home: str
    away: str

class Prediction(BaseModel):
    prob_TM5: float
    prob_TB1: float

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

@app.post("/predict", response_model=Prediction)
async def predict(match: MatchRequest, user: str = Depends(get_current_user)):
    try:
        # Placeholder for actual line data fetch
        line_data = {"home": match.home, "away": match.away}
        p_tm5, p_tb1 = v33lite.predict(line_data)
        return Prediction(prob_TM5=p_tm5, prob_TB1=p_tb1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
