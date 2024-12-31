import threading
import statistics
from collections import defaultdict
from datetime import datetime
import psutil

class ServiceMetrics:
    def __init__(self, history_size: int = 100):
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.processing_times = []
        self.errors = 0
        self.queue_lengths_history = []
        self.requests_by_priority = defaultdict(int)
        self.lock = threading.Lock()
        self.max_history = history_size

    def add_request(self, priority: str):
        with self.lock:
            self.request_count += 1
            self.requests_by_priority[priority] += 1

    def add_processing_time(self, duration: float):
        with self.lock:
            self.processing_times.append(duration)
            if len(self.processing_times) > self.max_history:
                self.processing_times.pop(0)

    def add_cache_hit(self):
        with self.lock:
            self.cache_hits += 1

    def add_cache_miss(self):
        with self.lock:
            self.cache_misses += 1

    def add_error(self):
        with self.lock:
            self.errors += 1

    def add_queue_length(self, length: int):
        with self.lock:
            self.queue_lengths_history.append(length)
            if len(self.queue_lengths_history) > self.max_history:
                self.queue_lengths_history.pop(0)

    def get_metrics(self) -> dict:
        with self.lock:
            processing_times = self.processing_times[-self.max_history:]
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0
            p95_processing_time = statistics.quantiles(processing_times, n=20)[-1] if len(processing_times) >= 20 else 0
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "total_requests": self.request_count,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_ratio": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
                "average_processing_time_ms": round(avg_processing_time * 1000, 2),
                "p95_processing_time_ms": round(p95_processing_time * 1000, 2),
                "total_errors": self.errors,
                "error_rate": self.errors / self.request_count if self.request_count > 0 else 0,
                "requests_by_priority": dict(self.requests_by_priority),
                "current_queue_length": self.queue_lengths_history[-1] if self.queue_lengths_history else 0,
                "average_queue_length": statistics.mean(self.queue_lengths_history) if self.queue_lengths_history else 0,
                "system_metrics": {
                    "cpu_percent": process.cpu_percent(),
                    "memory_usage_mb": memory_info.rss / (1024 * 1024),
                    "memory_percent": process.memory_percent(),
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                }
            }

    def reset_metrics(self):
        with self.lock:
            self.request_count = 0
            self.cache_hits = 0
            self.cache_misses = 0
            self.processing_times = []
            self.errors = 0
            self.queue_lengths_history = []
            self.requests_by_priority = defaultdict(int)