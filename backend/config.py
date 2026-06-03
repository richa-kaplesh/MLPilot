from pydantic_settings import BaseSettings
from typing import List
import ast

class Settings(BaseSettings):
    # Groq
    groq_api_keys: str  # comma separated
    groq_model_name: str = "llama3-70b-8192"
    groq_max_retries: int = 3
    groq_rate_limit_retry_delay: float = 1.0
    groq_cache_enabled: bool = True

    # PostgreSQL
    database_url: str

    # ChromaDB
    chroma_persist_directory: str = "./chromadb"

    # MLflow
    mlflow_tracking_uri: str = "./mlruns"

    # AWS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-south-1"

    # App
    environment: str = "development"
    port: int = 8000
    secret_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_groq_api_keys(self) -> List[str]:
        return [key.strip() for key in self.groq_api_keys.split(",")]


settings = Settings()