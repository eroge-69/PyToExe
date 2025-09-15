# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# local db helper
from db import init_db, save_progress

# Initialize DB file
init_db()

app = FastAPI(title="AI Learning Support Tool")

# Allow CORS for testing from file or different host
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    age: int
    condition: str
    language: str
    preference: str

class SaveRequest(BaseModel):
    name: str = None
    age: int = None
    condition: str
    recommendation: str

@app.post("/analyze")
async def analyze_child(req: AnalyzeRequest):
    # Simple rule-based placeholder logic
    condition_key = req.condition.lower().strip()
    recommendations = {
        "dyslexia": "Phonics-based reading stories with visual aids",
        "dysgraphia": "Tracing games and typing exercises",
        "dyscalculia": "Visual math games with step-by-step hints",
        "apd": "Audio discrimination and sequencing exercises",
        "lpd": "Language comprehension and vocabulary games",
        "nvld": "Nonverbal cue interpretation games and visual supports",
        "visual_processing": "Visual memory and spatial reasoning exercises"
    }
    suggestion = recommendations.get(condition_key, "General cognitive exercises and practice")
    return {
        "recommendation": suggestion,
        "language": req.language,
        "preference": req.preference
    }

@app.post("/save")
async def save(req: SaveRequest):
    try:
        record = save_progress(req.name, req.age, req.condition, req.recommendation)
        return {
            "id": record.id,
            "name": record.name,
            "age": record.age,
            "condition": record.condition,
            "recommendation": record.recommendation,
            "created_at": record.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
