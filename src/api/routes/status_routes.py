from fastapi import APIRouter
from src.services.worker import WorkerService
from src.services.cache_service import CacheService
from src.services.metrics_service import MetricsService

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@router.get("/system-status")
async def system_status():
    metrics = await MetricsService().get_metrics()
    return {
        "status": "operational",
        **metrics
    }