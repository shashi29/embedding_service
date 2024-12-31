from fastapi import APIRouter
from src.services.metrics_service import MetricsService

router = APIRouter()
metrics_service = MetricsService()

@router.get("/metrics")
async def get_metrics():
    return await metrics_service.get_metrics()

@router.post("/metrics/reset")
async def reset_metrics():
    await metrics_service.reset_metrics()
    return {"status": "Metrics reset successfully"}