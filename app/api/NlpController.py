from .BaseController import BaseController
from models import DataChunk
from services.vectordb.IProvider import IProvider as vector_db
from services.llm.IProvider import IProvider as llm
import json

class NlpController (BaseController):
    def __init__(self, vector_db: vector_db, generator: llm, embedder: llm):
        super().__init__()

        self.vector_db = vector_db
        self.generator = generator
        self.embedder = embedder
    
    def create_collection_name(self, collection_name: str):
        return f"nlp_{collection_name}".strip()
    
    async def index_data(self, project_id: str, chunk: list[DataChunk], chunk_ids: list[int] ,do_reset: bool = False):
        
        collection_name=self.create_collection_name(collection_name=project_id)

        texts = [c.chunk_text for c in chunk]
        metadata = [c.chunk_metadata for c in chunk]
        vectors = [self.embedder.embed_text(text=text, document_type='document') for text in texts]        

        if not self.vector_db.is_collection_exists(collection_name=collection_name):
            self.vector_db.create_collection(collection_name=collection_name, embedding_size=self.embedder.embedding_size, do_reset=do_reset)

        self.vector_db.insert_many(collection_name=collection_name, texts=texts, vectors=vectors, metadata=metadata, record_ids=chunk_ids)

        return True        
    
    async def get_vector_collection(self, project_id: str):
        collection_name=self.create_collection_name(collection_name=project_id)
        collection = self.vector_db.get_collection(collection_name=collection_name)

        # convert dictionary to json
        return json.loads(json.dumps(collection, default=lambda o: o.__dict__))
    
    async def search_vector_collection(self, project_id: str, query: str, limit: int = 10):
        collection_name=self.create_collection_name(collection_name=project_id)

        vector = self.embedder.embed_text(text=query, document_type='query')
        if not vector or len(vector) == 0:
            return        

        result = self.vector_db.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)
        if not result or len(result) == 0:
            return

        # convert dictionary to json
        return json.loads(json.dumps(result, default=lambda o: o.__dict__))
    
    
    async def reset_vector_collection(self, project_id: str):
        collection_name=self.create_collection_name(collection_name=project_id)
        return self.vector_db.delete_collection(collection_name=collection_name)
    