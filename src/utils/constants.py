DEFAULT_CONFIG = {
    "cache": {
        "max_size": 1000,
        "ttl": 3600  # 1 hour
    },
    "worker": {
        "batch_size": 10,
        "max_queue_size": 1000,
        "processing_timeout": 30
    },
    "api": {
        "max_text_length": 10000,
        "rate_limit": 100  # requests per minute
    }
}

# HTTP Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_500_INTERNAL_SERVER_ERROR = 500

# Cache Keys
CACHE_KEY_PREFIX = "embedding:"