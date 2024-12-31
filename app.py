from fastapi import FastAPI, HTTPException
from src.api.routes import embedding_routes, metrics_routes, status_routes
from src.utils.logger import setup_logger
from src.utils.config_loader import load_config

app = FastAPI(title="Embedding Service", version="1.0.0")

# Setup logging
logger = setup_logger()

# Load configuration
config = load_config()

# Include routers
app.include_router(embedding_routes.router, tags=["embeddings"])
app.include_router(metrics_routes.router, tags=["metrics"])
app.include_router(status_routes.router, tags=["status"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up embedding service")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down embedding service")