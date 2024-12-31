from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EmbeddingRequest(BaseModel):
    text: str
    priority: Priority = Field(default=Priority.MEDIUM)

class EmbeddingResponse(BaseModel):
    request_id: str
    status: str = "pending"

class StatusResponse(BaseModel):
    request_id: str
    status: str
    cache_hit: bool = False
    queue_position: Optional[int] = None
    error: Optional[str] = None

class ResultResponse(BaseModel):
    request_id: str
    embedding: Optional[List[float]] = None
    cache_hit: bool = False
    error: Optional[str] = None

class SyncEmbeddingRequest(BaseModel):
    text: str
    use_cache: bool = True

class SyncEmbeddingResponse(BaseModel):
    embedding: List[float]
    cache_hit: bool = False