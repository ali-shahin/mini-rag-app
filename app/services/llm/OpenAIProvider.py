from .IProvider import IProvider
from openai import OpenAI
from core.config import get_settings
import logging


class OpenAIProvider(IProvider):
    def __init__(self):
        self.api_key = get_settings().OPENAI_API_KEY
        self.base_url = get_settings().OPENAI_BASE_URL

        self.default_input_max_chars = get_settings().DEFAULT_INPUT_MAX_CHARS
        self.default_max_output_tokens = get_settings().DEFAULT_MAX_OUTPUT_TOKENS
        self.default_generation_temperature = get_settings().DEFAULT_GENERATION_TEMPERATURE

        self.generation_model = None
        self.embedding_model = None
        self.embedding_size = None

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url or None)

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model: str):
        self.generation_model = model

    def set_embedding_model(self, model: str, embedding_size: int):
        self.embedding_model = model
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list, max_tokens: int = None, temperature: float = 0) -> str:
        if not self.client:
            self.logger.error('OpenAI client is not initialized')
            return None

        max_tokens = max_tokens or self.default_max_output_tokens
        temperature = temperature or self.default_generation_temperature

        chat_history.append(self.construct_prompt(prompt, "user"))

        response = self.client.chat.completions.create(
            model=self.generation_model,
            messages=chat_history,
            max_tokens=max_tokens,
            temperature=temperature
        )

        if not response or not response.choices or not response.choices[0].message:
            self.logger.error('OpenAI response is empty')
            return None

        return response.choices[0].message.content

    def embed_text(self, text: str, document_type: str = None) -> str:
        if not self.client:
            self.logger.error('OpenAI client is not initialized')
            return None

        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )

        if not response or not response.data or not response.data[0].embedding:
            self.logger.error('OpenAI response is empty')
            return None

        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str) -> str:
        return {
            "role": role,
            "content": self.handle_prompt(prompt)
        }

    def handle_prompt(self, prompt: str) -> str:
        return prompt[:self.default_input_max_chars].strip()
