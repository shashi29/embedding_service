from typing import Dict, Optional
import asyncio
from collections import deque
import numpy as np
from src.utils.logger import get_logger
from src.services.cache_service import CacheService
from src.services.request_tracker import RequestTracker
from src.services.metrics_service import MetricsService
from src.models.pydantic_models import EmbeddingRequest, Priority

class WorkerService:
    def __init__(self, cache_service: CacheService, request_tracker: RequestTracker):
        self.cache_service = cache_service
        self.request_tracker = request_tracker
        self.logger = get_logger()
        self.metrics_service = MetricsService()
        
        # Separate queues for different priorities
        self.queues: Dict[Priority, deque] = {
            Priority.HIGH: deque(),
            Priority.MEDIUM: deque(),
            Priority.LOW: deque()
        }
        
        # Start the worker
        asyncio.create_task(self._process_queue())
    
    async def queue_request(self, request_id: str, request: EmbeddingRequest):
        self.queues[request.priority].append((request_id, request))
        await self.request_tracker.update_queue_position(request_id)
        await self.metrics_service.track_request_start(request_id, request.priority.value)
        self.logger.info(f"Queued request {request_id} with priority {request.priority}")
    
    async def process_text(self, text: str) -> list[float]:
        """Simulate embedding generation"""
        await asyncio.sleep(1)  # Simulate processing time
        return list(np.random.random(384).tolist())
    
    async def _process_queue(self):
        while True:
            request_id = None
            request = None
            
            # Process high priority first, then medium, then low
            for priority in Priority:
                if self.queues[priority]:
                    request_id, request = self.queues[priority].popleft()
                    break
            
            if request_id and request:
                try:
                    # Check cache first
                    cached_result = await self.cache_service.get(request.text)
                    if cached_result:
                        await self.request_tracker.complete_request(request_id, cached_result, True)
                        await self.metrics_service.track_request_complete(request_id, True)
                        continue

                    # Process the request
                    embedding = await self.process_text(request.text)
                    
                    # Cache the result
                    await self.cache_service.set(request.text, embedding)
                    
                    # Update request status
                    await self.request_tracker.complete_request(request_id, embedding, False)
                    await self.metrics_service.track_request_complete(request_id, False)
                    
                    self.logger.info(f"Processed request {request_id}")
                except Exception as e:
                    self.logger.error(f"Error processing request {request_id}: {str(e)}")
                    await self.request_tracker.fail_request(request_id, str(e))
                    await self.metrics_service.track_request_failed(request_id)
            
            await asyncio.sleep(1)  # Prevent CPU spinning