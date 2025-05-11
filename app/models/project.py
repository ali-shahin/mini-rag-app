from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId


class Project(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        return value

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    class Settings:
        collection_name = "projects"
        indexes = [
            {"key": {"project_id": 1}, "unique": True}
        ]
