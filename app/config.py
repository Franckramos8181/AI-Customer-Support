from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    database_url: str = "sqlite:///./support.db"
    chroma_persist_dir: str = "./chroma_data"
    app_title: str = "AI Klantenservice Assistent"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
