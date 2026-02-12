"""Configuration management for the deep research automation tool."""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings loaded from environment variables."""

    def __init__(self) -> None:
        """Initialize configuration from environment."""
        # Ollama settings
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://172.29.208.1:11434/v1")
        self.ollama_api_key: str = os.getenv("OLLAMA_API_KEY", "ollama-local")
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")

        # General settings
        self.max_results: int = int(os.getenv("MAX_RESULTS", "10"))
        self.default_date_from: str = os.getenv("DEFAULT_DATE_FROM", self._get_default_date_from())
        self.output_dir: str = os.getenv("OUTPUT_DIR", "outputs")

        # Validate required settings
        if not self.ollama_base_url:
            raise ValueError("OLLAMA_BASE_URL is required. Please set it in your .env file or environment variables.")

    @staticmethod
    def _get_default_date_from() -> str:
        """Get default start date (1 year ago from today)."""
        one_year_ago = datetime.now() - timedelta(days=365)
        return one_year_ago.strftime("%Y-%m-%d")


# Global configuration instance
config = Config()
