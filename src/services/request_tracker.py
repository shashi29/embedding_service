from datetime import datetime
from typing import Dict, Optional
import threading
import logging

logger = logging.getLogger(__name__)

class RequestTracker:
    def __init__(self):
        self.requests = {}
        self.lock = threading.Lock()

    def add_request(self, request_id: str, text: str, priority: str):
        with self.lock:
            self.requests[request_id] = {
                "text": text,
                "priority": priority,
                "status": "submitted",
                "submit_time": datetime.now().isoformat(),
                "queue_enter_time": None,
                "processing_start_time": None,
                "completion_time": None,
                "cache_hit": None,
                "error": None
            }

    def update_status(self, request_id: str, status: str, **kwargs):
        with self.lock:
            if request_id in self.requests:
                self.requests[request_id]["status"] = status
                self.requests[request_id].update(kwargs)
            else:
                logger.warning(f"Attempted to update non-existent request: {request_id}")

    def get_request_info(self, request_id: str) -> Optional[dict]:
        with self.lock:
            request_info = self.requests.get(request_id)
            if request_info:
                request_info["text_preview"] = request_info["text"][:50] + "..."
                return request_info
            return None

    def cleanup_old_requests(self, max_age_hours: int = 24):
        with self.lock:
            current_time = datetime.now()
            to_remove = []
            for request_id, info in self.requests.items():
                submit_time = datetime.fromisoformat(info["submit_time"])
                if (current_time - submit_time).total_seconds() > max_age_hours * 3600:
                    to_remove.append(request_id)
            for request_id in to_remove:
                del self.requests[request_id]