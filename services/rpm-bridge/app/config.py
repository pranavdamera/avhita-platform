from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    clinic_ehr_url: str = "http://localhost:8001"

    model_config = {"env_file": ".env"}


settings = Settings()
