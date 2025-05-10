from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id", default_factory=ObjectId)
    chunk_text: str
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
