from typing import Dict
import time
from collections import defaultdict
from src.utils.logger import get_logger

class MetricsService:
    def __init__(self):
        self.logger = get_logger()
        self.metrics = {
            "requests_total": 0,
            "requests_cached": 0,
            "requests_failed": 0,
            "processing_times": [],
            "cache_hit_rate": 0.0,
            "requests_by_priority": defaultdict(int),
            "average_queue_time": 0.0,
            "current_queue_size": 0
        }
        self.request_timestamps: Dict[str, float] = {}

    async def track_request_start(self, request_id: str, priority: str):
        self.metrics["requests_total"] += 1
        self.metrics["requests_by_priority"][priority] += 1
        self.request_timestamps[request_id] = time.time()
        self.metrics["current_queue_size"] += 1

    async def track_request_complete(self, request_id: str, cache_hit: bool):
        if request_id in self.request_timestamps:
            processing_time = time.time() - self.request_timestamps[request_id]
            self.metrics["processing_times"].append(processing_time)
            
            if len(self.metrics["processing_times"]) > 1000:
                self.metrics["processing_times"] = self.metrics["processing_times"][-1000:]
            
            if cache_hit:
                self.metrics["requests_cached"] += 1

            self.metrics["cache_hit_rate"] = (
                self.metrics["requests_cached"] / self.metrics["requests_total"]
                if self.metrics["requests_total"] > 0 else 0.0
            )
            
            self.metrics["current_queue_size"] = max(0, self.metrics["current_queue_size"] - 1)
            del self.request_timestamps[request_id]

    async def track_request_failed(self, request_id: str):
        self.metrics["requests_failed"] += 1
        self.metrics["current_queue_size"] = max(0, self.metrics["current_queue_size"] - 1)
        if request_id in self.request_timestamps:
            del self.request_timestamps[request_id]

    async def get_metrics(self):
        return {
            **self.metrics,
            "average_processing_time": (
                sum(self.metrics["processing_times"]) / len(self.metrics["processing_times"])
                if self.metrics["processing_times"] else 0.0
            )
        }

    # async def reset_metrics(self):
    #     self.__init__()