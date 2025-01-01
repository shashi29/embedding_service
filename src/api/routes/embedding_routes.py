from fastapi import APIRouter, HTTPException, Depends
from src.models.pydantic_models import (
    EmbeddingRequest, 
    EmbeddingResponse, 
    StatusResponse, 
    ResultResponse,
    SyncEmbeddingRequest,
    SyncEmbeddingResponse
)
from src.services.worker import WorkerService
from src.services.cache_service import CacheService
from src.services.request_tracker import RequestTracker
from src.services.metrics_service import MetricsService
from src.utils.logger import get_logger
import uuid

router = APIRouter()
logger = get_logger()

# Service instances
cache_service = CacheService()
request_tracker = RequestTracker()
metrics_service = MetricsService()
worker_service = WorkerService(cache_service, request_tracker)

@router.post("/submit", response_model=EmbeddingResponse)
async def submit_embedding(request: EmbeddingRequest):
    request_id = str(uuid.uuid4())
    
    # Track the start of the request
    await metrics_service.track_request_start(request_id, request.priority.value)
    
    # Check cache first
    cached_result = await cache_service.get(request.text)
    if cached_result:
        await request_tracker.complete_request(request_id, cached_result, True)
        await metrics_service.track_request_complete(request_id, True)
        return EmbeddingResponse(request_id=request_id, status="completed")
    
    # Queue the request
    await worker_service.queue_request(request_id, request)
    return EmbeddingResponse(request_id=request_id)

@router.get("/status/{request_id}", response_model=StatusResponse)
async def get_status(request_id: str):
    status = await request_tracker.get_status(request_id)
    if not status:
        raise HTTPException(status_code=404, detail="Request not found")
    return status

@router.get("/result/{request_id}", response_model=ResultResponse)
async def get_result(request_id: str):
    result = await request_tracker.get_result(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

@router.post("/embed_sync", response_model=SyncEmbeddingResponse)
async def embed_sync(request: SyncEmbeddingRequest):
    request_id = str(uuid.uuid4())
    await metrics_service.track_request_start(request_id, "sync")
    
    try:
        if request.use_cache:
            cached_result = await cache_service.get(request.text)
            if cached_result:
                await metrics_service.track_request_complete(request_id, True)
                return SyncEmbeddingResponse(
                    embedding=cached_result,
                    cache_hit=True
                )
        
        # Process immediately
        embedding = await worker_service.process_text(request.text)
        
        # Cache the result
        if request.use_cache:
            await cache_service.set(request.text, embedding)
        
        await metrics_service.track_request_complete(request_id, False)
        return SyncEmbeddingResponse(
            embedding=embedding,
            cache_hit=False
        )
    except Exception as e:
        await metrics_service.track_request_failed(request_id)
        raise HTTPException(status_code=500, detail=str(e))