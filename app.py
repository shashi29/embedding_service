from fastapi import FastAPI, HTTPException, Depends
from src.services.cache_service import Cache
from src.models.pydantic_models import EmbeddingRequestModel, EmbeddingResponseModel, DetailedStatusResponse, MetricsResponse
from src.services.worker import EmbeddingWorker
from src.services.metrics_service import ServiceMetrics
from src.services.request_tracker import RequestTracker
from src.utils.logger import setup_logger
from src.utils.constants import load_constants
import yaml
import os

app = FastAPI(title="Embedding Service API")

logger = setup_logger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

config = load_config()
constants = load_constants(config)

cache = Cache(config)
metrics = ServiceMetrics(history_size=config['metrics']['history_size'])
request_tracker = RequestTracker()
worker = EmbeddingWorker(model_name=config['model']['name'], cache=cache, metrics=metrics, request_tracker=request_tracker)
worker.start()

@app.post("/submit", response_model=str)
async def submit_embedding_request(request: EmbeddingRequestModel):
    request_id = worker.submit_request(request.text, request.priority)
    return {
        "request_id": request_id,
        "message": "Request submitted successfully"
    }

@app.get("/status/{request_id}", response_model=DetailedStatusResponse)
async def check_status(request_id: str):
    request_info = request_tracker.get_request_info(request_id)
    if not request_info:
        raise HTTPException(status_code=404, detail="Request not found")
    return DetailedStatusResponse(**request_info)

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    return MetricsResponse(**metrics.get_metrics())

@app.post("/embed_sync", response_model=EmbeddingResponseModel)
async def embed_sync(request: EmbeddingRequestModel):
    try:
        embedding, cached, processing_time = worker.get_embedding_sync(request.text, request.priority)
        return EmbeddingResponseModel(
            embedding=embedding,
            cached=cached,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error in synchronous embedding: {e}")
        return EmbeddingResponseModel(error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config['server']['host'], port=config['server']['port'])