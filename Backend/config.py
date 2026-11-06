import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Project directory paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_CHROMA_PATH = PROJECT_ROOT / "chroma_db"
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """
    Centralized configuration for BIS SmartAssist Backend.
    Values can be overridden using environment variables or a .env file.
    """
    # Ollama LLM Configuration
    ollama_url: str = Field(default="http://localhost:11434", description="Base URL for Ollama daemon")
    ollama_model: str = Field(default="llama3.2:3b", description="Model name to run on Ollama")
    ollama_timeout: int = Field(default=60, description="Timeout in seconds for Ollama generation requests")

    # FastAPI Server Configuration
    api_host: str = Field(default="127.0.0.1", description="FastAPI bind host")
    api_port: int = Field(default=8000, description="FastAPI bind port")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        description="Comma-separated allowed origins for CORS"
    )

    # ChromaDB & RAG Configuration
    chroma_path: Path = Field(default=DEFAULT_CHROMA_PATH, description="Path to persistent ChromaDB directory")
    collection_name: str = Field(default="bis_smartassist", description="ChromaDB collection name")
    embedding_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="SentenceTransformer model for dense query embedding"
    )

    # Document Upload & Processing Limits
    max_file_size_mb: int = Field(default=10, description="Maximum allowed size per uploaded file in megabytes")
    max_files_count: int = Field(default=5, description="Maximum allowed number of files per request")
    allowed_extensions: List[str] = Field(
        default=[".pdf", ".png", ".jpg", ".jpeg"],
        description="Allowed file extensions for upload"
    )

    # OCR Configuration
    tesseract_cmd: Optional[str] = Field(
        default=None,
        description="Optional custom path to tesseract.exe binary"
    )
    tessdata_prefix: Optional[str] = Field(
        default=None,
        description="Optional path to tessdata folder containing language models"
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def ollama_generate_url(self) -> str:
        base = self.ollama_url.rstrip("/")
        if not base.endswith("/api/generate"):
            return f"{base}/api/generate"
        return base


# Global singleton settings instance
settings = Settings()

