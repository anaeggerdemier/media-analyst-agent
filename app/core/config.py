from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    BQ_PROJECT_ID: str = ""
    BQ_CREDENTIALS_PATH: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
