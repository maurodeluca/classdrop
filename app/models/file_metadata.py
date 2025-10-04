from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class FileMetadata(BaseModel):
    file_id: UUID
    filename: str = Field(..., min_length=1)
    upload_timestamp: datetime
    size_in_bytes: int = Field(..., ge=0)
