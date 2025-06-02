from .BaseController import BaseController
from models import DataChunk
from services.vectordb.IProvider import IProvider as vector_db
from services.llm.IProvider import IProvider as llm
from services.rag.RAGService import RAGService


class NlpController(BaseController):
    def __init__(self, vector_db: vector_db, generator: llm, embedder: llm):
        super().__init__()
        self.rag_service = RAGService(vector_db, generator, embedder)

    async def index_data(self, project_id: str, chunks: list[DataChunk], chunk_ids: list[int], do_reset: bool = False):
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        return await self.rag_service.index_documents(project_id, texts, metadata, chunk_ids, do_reset)

    async def get_vector_collection(self, project_id: str):
        return await self.rag_service.get_collection_info(project_id)

    async def search_vector_collection(self, project_id: str, query: str, limit: int = 10):
        return await self.rag_service.search_documents(project_id, query, limit)

    async def answer_query(self, project_id: str, query: str, limit: int = 10):
        return await self.rag_service.answer_query(project_id, query, limit)

    async def reset_vector_collection(self, project_id: str):
        return await self.rag_service.reset_collection(project_id)
