from typing import Dict, Type, TypeVar, Any
from core.config import get_settings, Settings
from services.file.FileService import FileService
from services.document.DocumentService import DocumentService
from services.rag.RAGService import RAGService
from services.llm.IProvider import IProvider as LLMProvider
from services.vectordb.IProvider import IProvider as VectorDBProvider
from services.llm.ProviderFactory import ProviderFactory as LLMProviderFactory
from services.vectordb.ProviderFactory import ProviderFactory as VectorDBProviderFactory

T = TypeVar('T')

class Container:
    """Dependency Injection Container"""
    _instances: Dict[Type, Any] = {}
    _settings: Settings = None

    @classmethod
    def get_settings(cls) -> Settings:
        if not cls._settings:
            cls._settings = get_settings()
        return cls._settings

    @classmethod
    def get_file_service(cls) -> FileService:
        if FileService not in cls._instances:
            cls._instances[FileService] = FileService(cls.get_settings())
        return cls._instances[FileService]

    @classmethod
    def get_document_service(cls) -> DocumentService:
        if DocumentService not in cls._instances:
            cls._instances[DocumentService] = DocumentService()
        return cls._instances[DocumentService]

    @classmethod
    def get_llm_generation_provider(cls) -> LLMProvider:
        if 'generation_provider' not in cls._instances:
            settings = cls.get_settings()
            provider = LLMProviderFactory.create(settings.GENERATION_PROVIDER)
            provider.set_generation_model(settings.GENERATION_MODEL)
            cls._instances['generation_provider'] = provider
        return cls._instances['generation_provider']

    @classmethod
    def get_llm_embedding_provider(cls) -> LLMProvider:
        if 'embedding_provider' not in cls._instances:
            settings = cls.get_settings()
            provider = LLMProviderFactory.create(settings.EMBEDDING_PROVIDER)
            provider.set_embedding_model(settings.EMBEDDING_MODEL, settings.EMBEDDING_SIZE)
            cls._instances['embedding_provider'] = provider
        return cls._instances['embedding_provider']

    @classmethod
    def get_vector_db_provider(cls) -> VectorDBProvider:
        if VectorDBProvider not in cls._instances:
            settings = cls.get_settings()
            provider = VectorDBProviderFactory.create(settings.VECTOR_DB_PROVIDER)
            provider.connect()
            cls._instances[VectorDBProvider] = provider
        return cls._instances[VectorDBProvider]

    @classmethod
    def get_rag_service(cls) -> RAGService:
        if RAGService not in cls._instances:
            cls._instances[RAGService] = RAGService(
                cls.get_vector_db_provider(),
                cls.get_llm_generation_provider(),
                cls.get_llm_embedding_provider()
            )
        return cls._instances[RAGService]

    @classmethod
    def reset(cls) -> None:
        """Reset all instances (useful for testing)"""
        cls._instances = {}
        cls._settings = None
