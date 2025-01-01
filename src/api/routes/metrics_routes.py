from fastapi import APIRouter
from src.services.metrics_service import MetricsService

router = APIRouter()
metrics_service = MetricsService()

@router.get("/metrics")
async def get_metrics():
    """Get current metrics"""
    metrics = await metrics_service.get_metrics()
    return {
        "metrics": metrics,
        "metadata": {
            "timestamp": metrics_service.last_reset_time,
            "uptime_seconds": metrics_service.get_uptime_seconds()
        }
    }

@router.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics"""
    await metrics_service.reset_metrics()
    return {"status": "success", "message": "Metrics reset successfully"}