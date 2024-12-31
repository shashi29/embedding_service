from typing import Dict, Optional
from src.models.pydantic_models import StatusResponse, ResultResponse
from src.utils.logger import get_logger

class RequestTracker:
    def __init__(self):
        self.requests: Dict[str, Dict] = {}
        self.logger = get_logger()
    
    async def update_queue_position(self, request_id: str):
        self.requests[request_id] = {
            "status": "pending",
            "queue_position": len(self.requests) + 1
        }
    
    async def complete_request(self, request_id: str, embedding: list[float], cache_hit: bool):
        self.requests[request_id] = {
            "status": "completed",
            "embedding": embedding,
            "cache_hit": cache_hit,
            "queue_position": None
        }
    
    async def fail_request(self, request_id: str, error: str):
        self.requests[request_id] = {
            "status": "failed",
            "error": error,
            "queue_position": None
        }
    
    async def get_status(self, request_id: str) -> Optional[StatusResponse]:
        if request_id not in self.requests:
            return None
            
        request = self.requests[request_id]
        return StatusResponse(
            request_id=request_id,
            status=request["status"],
            cache_hit=request.get("cache_hit", False),
            queue_position=request.get("queue_position"),
            error=request.get("error")
        )
    
    async def get_result(self, request_id: str) -> Optional[ResultResponse]:
        if request_id not in self.requests:
            return None
            
        request = self.requests[request_id]
        if request["status"] != "completed":
            return ResultResponse(
                request_id=request_id,
                error="Result not ready" if request["status"] == "pending" else request.get("error")
            )
            
        return ResultResponse(
            request_id=request_id,
            embedding=request["embedding"],
            cache_hit=request["cache_hit"]
        )