"""AI Analyst router."""
from fastapi import APIRouter
from models.schemas import AIExplainRequest, AIResponse
from services.llm_service import explain_anomaly

router = APIRouter()

@router.post("/explain", response_model=AIResponse)
async def explain(req: AIExplainRequest):
    text = explain_anomaly(
        variable=req.variable, lat=req.lat, lon=req.lon,
        year=req.year, value=req.value, anomaly=req.anomaly,
        question=req.question,
    )
    return {"explanation": text, "cached": False}
