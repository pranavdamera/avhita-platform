from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://avhita:avhita@localhost:5432/avhita"

    model_config = {"env_file": ".env"}


settings = Settings()
