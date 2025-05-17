from .IProvider import IProvider


class Pinecone(IProvider):

    def __init__(self):
        pass    

    def connect(self):
        pass

    def disconnect(self):
        pass

    def is_collection_exists(self, collection_name: str) -> bool:
        pass

    def list_collections(self) -> list:
        pass

    def get_collection(self, collection_name: str) -> dict:
        pass

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        pass

    def delete_collection(self, collection_name: str):
        pass

    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict=None, record_id: str=None, document_type: str=None):
        pass

    def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: dict=None, record_ids: list=None, document_types: list=None, batch_size: int=100):
        pass

    def search_by_vector(self, collection_name: str, vector: list, limit: int) -> list:
        pass