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

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        validate_assignment=True,
    )


def get_settings() -> Settings:
    return Settings()
