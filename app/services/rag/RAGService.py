from typing import List, Optional
from services.llm.IProvider import IProvider as LLMProvider
from services.vectordb.IProvider import IProvider as VectorDBProvider
from services.llm.Templates import rag
from schemas.data import RetrievedDocument
import json

class RAGService:
    def __init__(self, vector_db: VectorDBProvider, generator: LLMProvider, embedder: LLMProvider):
        self.vector_db = vector_db
        self.generator = generator
        self.embedder = embedder

    def _create_collection_name(self, collection_name: str) -> str:
        return f"nlp_{collection_name}".strip()

    async def index_documents(self, project_id: str, texts: List[str], metadata: List[dict], chunk_ids: List[int], do_reset: bool = False) -> bool:
        collection_name = self._create_collection_name(project_id)
        vectors = [self.embedder.embed_text(text=text, document_type='document') for text in texts]

        if not self.vector_db.is_collection_exists(collection_name=collection_name):
            self.vector_db.create_collection(
                collection_name=collection_name,
                embedding_size=self.embedder.embedding_size,
                do_reset=do_reset
            )

        self.vector_db.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunk_ids
        )

        return True

    async def get_collection_info(self, project_id: str) -> dict:
        collection_name = self._create_collection_name(project_id)
        collection = self.vector_db.get_collection(collection_name=collection_name)
        return json.loads(json.dumps(collection, default=lambda o: o.__dict__))

    async def search_documents(self, project_id: str, query: str, limit: int = 10) -> List[RetrievedDocument]:
        collection_name = self._create_collection_name(project_id)
        vector = self.embedder.embed_text(text=query, document_type='query')
        
        if not vector or len(vector) == 0:
            return []

        return self.vector_db.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

    async def answer_query(self, project_id: str, query: str, limit: int = 10) -> Optional[str]:
        retrieved_documents = await self.search_documents(project_id=project_id, query=query, limit=limit)
        
        if not retrieved_documents:
            return None

        system_prompt = rag.get_system_prompt(domain=project_id)
        document_prompt = "\n".join([
            rag.get_document_prompt(document_name=idx + 1, content=doc.text)
            for idx, doc in enumerate(retrieved_documents)
        ])
        footer_prompt = rag.get_footer_prompt(question=query)
        
        prompt = f"{document_prompt}\n{footer_prompt}"
        chat_history = [
            self.generator.construct_prompt(prompt=system_prompt, role="system"),
        ]

        return self.generator.generate_text(prompt=prompt, chat_history=chat_history)

    async def reset_collection(self, project_id: str) -> bool:
        collection_name = self._create_collection_name(project_id)
        return self.vector_db.delete_collection(collection_name=collection_name)
