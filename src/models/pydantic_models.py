from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional, List, Dict

class PriorityEnum(str, Enum):
    HIGH = "high"
    LOW = "low"

class EmbeddingRequestModel(BaseModel):
    text: str
    priority: PriorityEnum = PriorityEnum.LOW

    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        if len(v) > 10000:
            raise ValueError('Text is too long (max 10000 characters)')
        return v.strip()

class EmbeddingResponseModel(BaseModel):
    embedding: Optional[List[float]] = None
    error: Optional[str] = None
    cached: bool = False
    processing_time: Optional[float] = None

class DetailedStatusResponse(BaseModel):
    status: str
    submit_time: Optional[str]
    queue_enter_time: Optional[str]
    processing_start_time: Optional[str]
    completion_time: Optional[str]
    cache_hit: Optional[bool]
    error: Optional[str]
    text_preview: str
    priority: str
    time_in_queue: Optional[float]
    processing_duration: Optional[float]
    total_duration: Optional[float]

class MetricsResponse(BaseModel):
    total_requests: int
    cache_hits: int
    cache_misses: int
    cache_hit_ratio: float
    average_processing_time_ms: float
    p95_processing_time_ms: float
    total_errors: int
    error_rate: float
    requests_by_priority: Dict[str, int]
    current_queue_length: int
    average_queue_length: float
    system_metrics: Dict[str, float]