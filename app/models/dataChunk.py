from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    _id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="id")
    chunk_text: str
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId

    class Config:
        allow_population_by_field_name = True
