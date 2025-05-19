from abc import ABC, abstractmethod
from schemas.data import RetrievedDocument

class IProvider(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_collections(self) -> list:
        pass

    @abstractmethod
    def get_collection(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict=None, record_id: str=None, document_type: str=None):
        pass

    @abstractmethod
    def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: dict=None, record_ids: list=None, document_types: list=None, batch_size: int=100):
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int) -> list[RetrievedDocument]:
        pass