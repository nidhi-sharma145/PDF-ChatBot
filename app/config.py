import os
from dotenv import load_dotenv

# Load environment variables from .env file and override cached variables
load_dotenv(override=True)

class Settings:
    """Application settings loader."""
    @property
    def API_PROVIDER(self) -> str:
        # Load dotenv on demand to keep values fresh
        load_dotenv(override=True)
        return os.getenv("API_PROVIDER", "gemini").lower().strip()

    @property
    def GEMINI_API_KEY(self) -> str:
        load_dotenv(override=True)
        return os.getenv("GEMINI_API_KEY", "").strip()

    @property
    def GROQ_API_KEY(self) -> str:
        load_dotenv(override=True)
        return os.getenv("GROQ_API_KEY", "").strip()

    @property
    def HOST(self) -> str:
        return os.getenv("HOST", "127.0.0.1")

    @property
    def PORT(self) -> int:
        return int(os.getenv("PORT", "8000"))

    @property
    def api_key(self) -> str:
        """Returns the active API key based on the provider selection."""
        if self.API_PROVIDER == "gemini":
            return self.GEMINI_API_KEY
        elif self.API_PROVIDER == "groq":
            return self.GROQ_API_KEY
        return ""

settings = Settings()
