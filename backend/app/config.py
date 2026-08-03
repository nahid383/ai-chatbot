"""
Centralized configuration, loaded from environment variables (.env file
locally, or platform-provided env vars on Railway).

Why centralize this: every other file imports `settings` from here instead
of calling os.getenv() everywhere. One source of truth, and pydantic
validates that required values actually exist at startup (fail fast).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str  # e.g. postgresql://user:pass@localhost:5432/swe23

    # --- AI ---
    GEMINI_API_KEY: str
    GEMINI_CHAT_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    # --- Auth ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- Storage ---
    UPLOAD_DIR: str = "./uploads"
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # --- RAG tuning ---
    CHUNK_SIZE: int = 800          # characters per chunk
    CHUNK_OVERLAP: int = 120       # characters of overlap between chunks
    RETRIEVAL_TOP_K: int = 5
    # ChromaDB returns cosine *distance* (0 = identical, 2 = opposite).
    # Anything above this is treated as "not relevant enough" -> refuse.
    MAX_RELEVANT_DISTANCE: float = 0.65

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
