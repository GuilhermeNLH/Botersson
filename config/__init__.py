"""Botersson – shared configuration loader."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load .env from repository root (two levels up from this file)
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


def _load_yaml() -> dict:
    cfg_path = _ROOT / "config" / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path) as fh:
            return yaml.safe_load(fh) or {}
    return {}


_yaml = _load_yaml()


class BotConfig:
    TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GUILD_ID: int | None = int(os.getenv("DISCORD_GUILD_ID", "0")) or None
    PREFIX: str = _yaml.get("bot", {}).get("prefix", "!")
    DESCRIPTION: str = _yaml.get("bot", {}).get("description", "Botersson")
    ACTIVITY: str = _yaml.get("bot", {}).get("activity", "Researching... 🔬")


class OllamaConfig:
    HOST: str = os.getenv("OLLAMA_HOST", _yaml.get("ollama", {}).get("host", "http://localhost:11434"))
    MODEL: str = os.getenv("OLLAMA_MODEL", _yaml.get("ollama", {}).get("model", "llama3.2"))
    TIMEOUT: int = _yaml.get("ollama", {}).get("timeout", 120)
    FALLBACK_MODELS: list[str] = _yaml.get("ollama", {}).get("fallback_models", ["mistral", "phi3", "llama3"])


class ExcelConfig:
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(_ROOT / "data")))
    FILENAME: str = os.getenv("EXCEL_FILENAME", _yaml.get("excel", {}).get("filename", "research_data.xlsx"))
    SHEETS: list[dict] = _yaml.get("excel", {}).get("sheets", [])

    @classmethod
    def workbook_path(cls) -> Path:
        return cls.DATA_DIR / cls.FILENAME


class WebConfig:
    HOST: str = os.getenv("WEB_HOST", _yaml.get("web", {}).get("host", "0.0.0.0"))
    PORT: int = int(os.getenv("WEB_PORT", str(_yaml.get("web", {}).get("port", 5000))))
    SECRET_KEY: str = os.getenv("WEB_SECRET_KEY", "change-me")
    DEBUG: bool = _yaml.get("web", {}).get("debug", False)


class ScrapingConfig:
    TIMEOUT: int = _yaml.get("scraping", {}).get("timeout", 30)
    MAX_RETRIES: int = _yaml.get("scraping", {}).get("max_retries", 3)
    DELAY: float = _yaml.get("scraping", {}).get("delay_between_requests", 1.5)
    ROTATE_UA: bool = _yaml.get("scraping", {}).get("user_agent_rotation", True)


class SearchConfig:
    MAX_RESULTS: int = _yaml.get("search", {}).get("max_results", 10)


class SchedulerConfig:
    ENABLED: bool = _yaml.get("scheduler", {}).get("enabled", True)
    DAILY_HOUR: int = _yaml.get("scheduler", {}).get("daily_summary_hour", 8)
