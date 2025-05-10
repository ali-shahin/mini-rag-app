from core.config import get_settings


class BaseRepo:
    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_settings()

    def set_collection(self, collection_name: str):
        self.collection = self.db_client[collection_name]
