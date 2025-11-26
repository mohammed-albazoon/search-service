from pydantic import BaseModel
from typing import Optional

class MessageRecord(BaseModel):
    id: str
    title: Optional[str] = None
    body: Optional[str] = None
    created_at: Optional[str] = None  # whatever schema remote gives; keep flexible

class SearchResult(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[MessageRecord]
