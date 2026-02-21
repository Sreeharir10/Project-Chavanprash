from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Self Healer"  # Project name
    VERSION: str = "1.0.0"              # API version
    API_V1_STR: str = "/api/v1"        # API prefix

    # Neo4j Config
    NEO4J_URI: str = "bolt://localhost:7687"   # Neo4j connection URI
    NEO4J_USER: str = "neo4j"                  # Neo4j username
    NEO4J_PASSWORD: str = "password"           # Neo4j password

    # Vector DB Config
    CHROMA_DB_DIR: str = "./chroma_db"         # ChromaDB persistent directory

    # Repo Storage
    REPO_STORAGE_PATH: str = "./temp_repos"    # Temp folder for cloned repos

    # Optionally add TEMP_DIR for custom ingestion
    TEMP_DIR: Optional[str] = None              # Custom temp dir for ingestion (overrides REPO_STORAGE_PATH)

    class Config:
        env_file = ".env"

settings = Settings()
