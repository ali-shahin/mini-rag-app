from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId


class Project(BaseModel):
    _id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="id")
    project_id: str

    @field_validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("Project ID must be alphanumeric")

    class Config:
        allow_population_by_field_name = True
