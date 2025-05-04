from pydantic import BaseModel
from typing import Optional


class DataProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0
