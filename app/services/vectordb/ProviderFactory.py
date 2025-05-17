class ProviderFactory:

    @staticmethod
    def create(provider: str):
        if provider == 'pinecone':
            from .Pinecone import Pinecone
            return Pinecone()
        elif provider == 'qdrant':
            from .Qdrant import Qdrant
            return Qdrant()
        else:
            raise Exception("Invalid vector database provider")