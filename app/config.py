import os
from dotenv import load_dotenv

# Load environment variables from .env file and override cached variables
load_dotenv(override=True)

class Settings:
    """Application settings loader."""
    def __init__(self):
        self._api_provider = None

    @property
    def API_PROVIDER(self) -> str:
        if self._api_provider is not None:
            return self._api_provider
        load_dotenv(override=True)
        return os.getenv("API_PROVIDER", "gemini").lower().strip()

    @API_PROVIDER.setter
    def API_PROVIDER(self, value: str):
        self._api_provider = value.lower().strip()

    @property
    def OLLAMA_BASE_URL(self) -> str:
        load_dotenv(override=True)
        return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()

    @property
    def OLLAMA_MODEL(self) -> str:
        load_dotenv(override=True)
        return os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip()

    @property
    def HOST(self) -> str:
        return os.getenv("HOST", "127.0.0.1")

    @property
    def PORT(self) -> int:
        return int(os.getenv("PORT", "8000"))

settings = Settings()

