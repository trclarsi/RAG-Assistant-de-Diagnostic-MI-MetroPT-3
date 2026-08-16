from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_model: str = "claude-sonnet-5"
    embedding_model: str = "text-embedding-3-large"

    vector_store_backend: str = "pgvector"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "rag"
    postgres_user: str = "rag"
    postgres_password: str = "changeme"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "changeme"

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5

    log_level: str = "INFO"
    environment: str = "dev"


settings = Settings()
