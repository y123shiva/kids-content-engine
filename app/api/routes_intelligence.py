from fastapi import APIRouter
from app.intelligence.dataset_report import analyze_script
import json

router = APIRouter()

@router.post("/analyze-script")
def analyze(script: dict):
    return analyze_script(script)
