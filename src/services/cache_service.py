from typing import Optional, Dict, List
import time
from src.utils.logger import get_logger

class CacheService:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, tuple[List[float], float]] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.logger = get_logger()
    
    async def get(self, text: str) -> Optional[List[float]]:
        if text in self.cache:
            embedding, timestamp = self.cache[text]
            if time.time() - timestamp <= self.ttl:
                self.logger.info(f"Cache hit for text: {text[:50]}...")
                return embedding
            else:
                # Remove expired entry
                del self.cache[text]
        return None
    
    async def set(self, text: str, embedding: List[float]):
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_key]
        
        self.cache[text] = (embedding, time.time())
        self.logger.info(f"Cached embedding for text: {text[:50]}...")