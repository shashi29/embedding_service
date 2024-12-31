import time
import uuid
from queue import PriorityQueue
from src.services.cache_service import Cache
from src.models.pydantic_models import EmbeddingResponseModel
from src.utils.logger import setup_logger
from sentence_transformers import SentenceTransformer
import threading

logger = setup_logger(__name__)

class EmbeddingWorker:
    def __init__(self, model_name: str, cache: Cache, metrics, request_tracker):
        self.model = SentenceTransformer(model_name)
        self.cache = cache
        self.queue = PriorityQueue()
        self.running = True
        self.results = {}
        self.results_lock = threading.Lock()
        self.metrics = metrics
        self.request_tracker = request_tracker

    def submit_request(self, text: str, priority: str = "low") -> str:
        request_id = str(uuid.uuid4())
        priority_level = 1 if priority == "high" else 2
        self.queue.put((priority_level, request_id, text))
        return request_id

    def process_requests(self):
        while self.running:
            if not self.queue.empty():
                priority_level, request_id, text = self.queue.get()
                start_time = time.time()
                try:
                    cached_embedding = self.cache.get(text)
                    cached = bool(cached_embedding)
                    if not cached:
                        embedding = self.model.encode(text).tolist()
                        self.cache.set(text, embedding)
                    else:
                        embedding = cached_embedding
                    processing_time = time.time() - start_time
                    with self.results_lock:
                        self.results[request_id] = EmbeddingResponseModel(
                            embedding=embedding,
                            cached=cached,
                            processing_time=processing_time
                        )
                    self.request_tracker.update_status(
                        request_id,
                        "completed",
                        processing_time=processing_time,
                        cache_hit=cached
                    )
                    self.metrics.add_cache_hit() if cached else self.metrics.add_cache_miss()
                    self.metrics.add_processing_time(processing_time)
                except Exception as e:
                    logger.error(f"Error processing request {request_id}: {e}")
                    with self.results_lock:
                        self.results[request_id] = EmbeddingResponseModel(
                            error=str(e)
                        )
                    self.request_tracker.update_status(
                        request_id,
                        "error",
                        error=str(e)
                    )
                    self.metrics.add_error()
            else:
                time.sleep(1)

    def get_embedding_sync(self, text: str, priority: str):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        try:
            embedding = self.cache.get(text)
            cached = bool(embedding)
            if not cached:
                embedding = self.model.encode(text).tolist()
                self.cache.set(text, embedding)
            processing_time = time.time() - start_time
            self.request_tracker.add_request(request_id, text, priority)
            self.request_tracker.update_status(
                request_id,
                "completed",
                processing_time=processing_time,
                cache_hit=cached
            )
            self.metrics.add_cache_hit() if cached else self.metrics.add_cache_miss()
            self.metrics.add_processing_time(processing_time)
            return embedding, cached, processing_time
        except Exception as e:
            self.metrics.add_error()
            self.request_tracker.update_status(
                request_id,
                "error",
                error=str(e)
            )
            raise Exception(str(e))

    def start(self):
        self.thread = threading.Thread(target=self.process_requests)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()