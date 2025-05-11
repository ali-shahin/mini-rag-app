from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=0)
    asset_config: dict = Field(default={})
    asset_pushed_at: datetime = Field(default_factory=datetime.now)

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    class Settings:
        collection_name = "assets"
        indexes = [
            {"key": {"asset_project_id": 1}, "unique": False},
            {"key": {"asset_project_id": 1, "asset_name": 1}, "unique": True}
        ]
