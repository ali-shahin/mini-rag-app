from pydantic import BaseModel
from typing import Optional


class DataDocumentRequest(BaseModel):
    file_name: Optional[str] = None
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 20
    do_reset: Optional[int] = 0

class RetrievedDocument(BaseModel):
    text: str
    score: float