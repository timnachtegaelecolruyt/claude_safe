"""Tests for configuration management."""

from unittest.mock import patch
import pytest
from projects.deep_research.config import Config


class TestConfig:
    def test_defaults(self) -> None:
        """Test that Config loads with sensible defaults."""
        with patch.dict("os.environ", {}, clear=True):
            cfg = Config()

        assert cfg.ollama_base_url == "http://172.29.208.1:11434/v1"
        assert cfg.ollama_api_key == "ollama-local"
        assert cfg.ollama_model == "llama3.2"
        assert cfg.max_results == 10
        assert cfg.output_dir == "outputs"
        assert cfg.enabled_sources == ["arxiv", "web", "news", "semantic_scholar", "hackernews"]

    def test_env_overrides(self) -> None:
        """Test that environment variables override defaults."""
        env = {
            "OLLAMA_BASE_URL": "http://custom:1234/v1",
            "OLLAMA_API_KEY": "my-key",
            "OLLAMA_MODEL": "mistral",
            "MAX_RESULTS": "25",
            "OUTPUT_DIR": "/tmp/reports",
            "ENABLED_SOURCES": "arxiv,web",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = Config()

        assert cfg.ollama_base_url == "http://custom:1234/v1"
        assert cfg.ollama_api_key == "my-key"
        assert cfg.ollama_model == "mistral"
        assert cfg.max_results == 25
        assert cfg.output_dir == "/tmp/reports"
        assert cfg.enabled_sources == ["arxiv", "web"]

    def test_missing_ollama_url_raises(self) -> None:
        """Test that empty OLLAMA_BASE_URL raises ValueError."""
        with patch.dict("os.environ", {"OLLAMA_BASE_URL": ""}, clear=True):
            with pytest.raises(ValueError, match="OLLAMA_BASE_URL is required"):
                Config()

    def test_default_date_from_format(self) -> None:
        """Test that default_date_from is a valid YYYY-MM-DD string."""
        with patch.dict("os.environ", {}, clear=True):
            cfg = Config()

        # Should be YYYY-MM-DD format
        parts = cfg.default_date_from.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # year
        assert len(parts[1]) == 2  # month
        assert len(parts[2]) == 2  # day
