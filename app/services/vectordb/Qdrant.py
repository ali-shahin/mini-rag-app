from .IProvider import IProvider
from core.config import get_settings
from qdrant_client import QdrantClient, models
import logging
from schemas.data import RetrievedDocument

class Qdrant(IProvider):
    def __init__(self):
        
        # TODO: handel db path
        self.db_path = get_settings().QDRANT_DB_PATH
        _distance_method = get_settings().QDRANT_DISTANCE_METHOD
        self.client = None

        if _distance_method == 'cosine':
            self.distance = models.Distance.COSINE
        elif _distance_method == 'euclidean':
            self.distance = models.Distance.EUCLIDEAN
        else:
            self.distance = models.Distance.DOT

        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(self.db_path)
        self.logger.info("Connected to QdrantDB")
    
    def disconnect(self):
        self.client.close()
        self.logger.info("Disconnected from QdrantDB")

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_collections(self):
        return self.client.get_collections()

    def get_collection(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            self.delete_collection(collection_name=collection_name)

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=self.distance
            )
        )

        self.logger.info(f"Collection {collection_name} created")

        return self.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.client.collection_exists(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict=None, record_id: str=None, document_type: str=None):
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return
        
        if not vector or not isinstance(vector, list):
            self.logger.error("Invalid vector provided")
            return

        try:
            return self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={
                            'text': text,
                            'metadata': metadata,
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error during upsert: {e}")
            return
    
    def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: dict=None, record_ids: list=None, document_types: list=None, batch_size: int=100):
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return
        
        metadata = metadata or [None] * len(texts)
        record_ids = record_ids or [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            try:
                if not all((batch_texts, batch_vectors)):
                    self.logger.error("Text or vector batch is empty")
                    continue

                self.client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                            id=record_id,
                            vector=vector,
                            payload={
                                'text': text,
                                'metadata': metadata,
                            }
                        )
                        for text, vector, metadata, record_id in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids)
                        if text is not None and vector is not None
                    ]
                )
            except Exception as e:
                self.logger.error(f"Error during batch upsert: {e}")

        return len(texts)
        
    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return

        if not vector or not isinstance(vector, list):
            self.logger.error("Invalid vector provided")
            return

        try:
            result = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )

            if not result or len(result) == 0:
                return []

            return [RetrievedDocument(**{'score': item.score, 'text': item.payload['text']}) for item in result]
        except Exception as e:
            self.logger.error(f"Error during search: {e}")
            return