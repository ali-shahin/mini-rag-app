class ProviderFactory:

    @staticmethod
    def create(provider: str):
        if provider == 'pinecone':
            from .Pinecone import Pinecone
            return Pinecone()
        elif provider == 'weaviate':
            raise Exception("Weaviate is not supported yet")    
        elif provider == 'qdrant':
            from .Qdrant import Qdrant
            return Qdrant()
        else:
            raise Exception("Invalid vector database provider")