from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    BQ_PROJECT_ID: str = ""
    BQ_CREDENTIALS_PATH: str = ""
    APP_VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
