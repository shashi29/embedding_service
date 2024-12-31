import redis
from redis import ConnectionPool
import json
import hashlib
from typing import Optional, List

class Cache:
    def __init__(self, config):
        pool = ConnectionPool(
            host=config['redis']['host'],
            port=config['redis']['port'],
            db=config['redis']['db']
        )
        self.redis_client = redis.Redis(connection_pool=pool)
        self.ttl = config['model']['cache_ttl']

    def _generate_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[List[float]]:
        key = self._generate_key(text)
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
        except Exception as e:
            print(f"Redis get error: {e}")
        return None

    def set(self, text: str, embedding: List[float]):
        key = self._generate_key(text)
        try:
            self.redis_client.setex(key, self.ttl, json.dumps(embedding))
        except Exception as e:
            print(f"Redis set error: {e}")