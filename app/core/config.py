from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    APP_URL: str

    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE: int

    MONGO_DB_URL: str
    MONGO_DB_NAME: str

    OPENAI_API_KEY: str
    OPENAI_API_BASE: str
    COHERE_API_KEY: str

    GENERATION_PROVIDER: str
    EMBEDDING_PROVIDER: str

    GENERATION_MODEL: str
    EMBEDDING_MODEL: str
    EMBEDDING_SIZE: int

    DEFAULT_INPUT_MAX_CHARS: int
    DEFAULT_MAX_OUTPUT_TOKENS: int
    DEFAULT_GENERATION_TEMPERATURE: float

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        validate_assignment=True,
    )


def get_settings() -> Settings:
    return Settings()
