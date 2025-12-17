from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Self Healer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Neo4j Config
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Vector DB Config
    CHROMA_DB_DIR: str = "./chroma_db"
    
    # Repo Storage
    REPO_STORAGE_PATH: str = "./temp_repos"

    class Config:
        env_file = ".env"

settings = Settings()
