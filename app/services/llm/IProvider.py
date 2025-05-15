from abc import ABC, abstractmethod


class IProvider(ABC):

    @abstractmethod
    def set_generation_model(self, model: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model: str, embedding_size: int):
        pass

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list, max_tokens: int, temperature: float = 0) -> str:
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str) -> str:
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str) -> str:
        pass
