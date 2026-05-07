from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class OutboxPayloadSchema(BaseModel):
    event_id: str
    action: str = Field(default="ENRICH_USER_SHARES_DATA")
    username: str
    email: str
    shares_broker: str


class OutboxDLQPayloadSchema(BaseModel):
    event_id: str
    original_topic: str
    failed_payload: Dict[str, Any]
    error_message: str
    created_at: datetime
    retry_count: int
    failed_at: datetime = Field(default_factory=datetime.now)