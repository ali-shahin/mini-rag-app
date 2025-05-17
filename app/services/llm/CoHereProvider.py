from .IProvider import IProvider
import cohere
from core.config import get_settings
import logging


class CoHereProvider(IProvider):
    def __init__(self):
        self.api_key = get_settings().COHERE_API_KEY
        self.default_input_max_chars = get_settings().DEFAULT_INPUT_MAX_CHARS
        self.default_max_output_tokens = get_settings().DEFAULT_MAX_OUTPUT_TOKENS
        self.default_generation_temperature = get_settings().DEFAULT_GENERATION_TEMPERATURE

        self.generation_model = None
        self.embedding_model = None
        self.embedding_size = None
        self.client = cohere.ClientV2(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model: str):
        self.generation_model = model

    def set_embedding_model(self, model: str, embedding_size: int):
        self.embedding_model = model
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list, max_tokens: int, temperature: float = 0) -> str:
        if not self.client:
            self.logger.error('CoHere client is not initialized')
            return None

        max_tokens = max_tokens or self.default_max_output_tokens
        temperature = temperature or self.default_generation_temperature

        chat_history.append(self.construct_prompt(prompt, "USER"))

        response = self.client.chat(
            model=self.generation_model,
            chat_history=chat_history,
            message=self.handle_prompt(prompt),
            max_tokens=max_tokens,
            temperature=temperature
        )

        if not response or not response.text:
            self.logger.error('CoHere response is empty')
            return None

        return response.text

    def embed_text(self, text: str, document_type: str = None) -> str:
        if not self.client:
            self.logger.error('CoHere client is not initialized')
            return None

        input_type = {
            "query": "search_query",
            "image": "image",
            "classification": "classification",
        }.get(document_type, "search_document")

        response = self.client.embed(
            texts=[self.handle_prompt(text)],
            model=self.embedding_model,
            input_type=input_type,
            embedding_types=["float"]
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error('CoHere response is empty')
            return None

        return response.embeddings.float[0]

    def construct_prompt(self, prompt: str, role: str) -> str:
        return {"role": role, "text": self.handle_prompt(prompt)}

    def handle_prompt(self, prompt: str) -> str:
        return prompt[:self.default_input_max_chars].strip()

