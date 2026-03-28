from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    BQ_PROJECT_ID: str = ""
    BQ_CREDENTIALS_PATH: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
