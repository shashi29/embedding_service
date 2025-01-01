from typing import Dict, Optional
import time
from collections import defaultdict
from src.utils.logger import get_logger

class MetricsService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = get_logger()
            self.last_reset_time = time.time()
            self._initialize_metrics()
            self._initialized = True

    def _initialize_metrics(self):
        """Initialize all metrics counters and trackers"""
        self.metrics = {
            "requests": {
                "total": 0,
                "cached": 0,
                "failed": 0,
                "by_priority": defaultdict(int),
                "in_progress": 0
            },
            "performance": {
                "processing_times": [],
                "average_processing_time": 0.0,
                "cache_hit_rate": 0.0,
                "current_queue_size": 0
            },
            "errors": defaultdict(int)
        }
        self.request_timestamps: Dict[str, float] = {}

    def get_uptime_seconds(self) -> float:
        """Get service uptime in seconds since last metrics reset"""
        return time.time() - self.last_reset_time

    async def track_request_start(self, request_id: str, priority: str):
        """Track the start of a new request"""
        self.metrics["requests"]["total"] += 1
        self.metrics["requests"]["by_priority"][priority] += 1
        self.metrics["requests"]["in_progress"] += 1
        self.request_timestamps[request_id] = time.time()
        self.metrics["performance"]["current_queue_size"] += 1

    async def track_request_complete(self, request_id: str, cache_hit: bool):
        """Track the completion of a request"""
        if request_id in self.request_timestamps:
            processing_time = time.time() - self.request_timestamps[request_id]
            self.metrics["performance"]["processing_times"].append(processing_time)
            
            # Keep only last 1000 processing times
            if len(self.metrics["performance"]["processing_times"]) > 1000:
                self.metrics["performance"]["processing_times"] = self.metrics["performance"]["processing_times"][-1000:]
            
            self.metrics["performance"]["average_processing_time"] = (
                sum(self.metrics["performance"]["processing_times"]) /
                len(self.metrics["performance"]["processing_times"])
            )
            
            if cache_hit:
                self.metrics["requests"]["cached"] += 1

            self.metrics["performance"]["cache_hit_rate"] = (
                self.metrics["requests"]["cached"] / self.metrics["requests"]["total"]
                if self.metrics["requests"]["total"] > 0 else 0.0
            )
            
            self.metrics["requests"]["in_progress"] = max(0, self.metrics["requests"]["in_progress"] - 1)
            self.metrics["performance"]["current_queue_size"] = max(
                0, self.metrics["performance"]["current_queue_size"] - 1
            )
            
            del self.request_timestamps[request_id]

    async def track_request_failed(self, request_id: str, error: str = "unknown"):
        """Track a failed request"""
        self.metrics["requests"]["failed"] += 1
        self.metrics["errors"][error] += 1
        self.metrics["requests"]["in_progress"] = max(0, self.metrics["requests"]["in_progress"] - 1)
        self.metrics["performance"]["current_queue_size"] = max(
            0, self.metrics["performance"]["current_queue_size"] - 1
        )
        
        if request_id in self.request_timestamps:
            del self.request_timestamps[request_id]

    async def get_metrics(self) -> dict:
        """Get current metrics"""
        return {
            **self.metrics,
            "uptime_seconds": self.get_uptime_seconds()
        }

    async def reset_metrics(self):
        """Reset all metrics"""
        self.last_reset_time = time.time()
        self._initialize_metrics()