import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "ai_consultant.db"

load_dotenv(BASE_DIR / ".env")


@lru_cache
def settings() -> dict:
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        "app_env": os.getenv("APP_ENV", "development"),
        "database_url": os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}"),
        "secret_key": os.getenv("SECRET_KEY", "dev-secret"),
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://localhost:8000").split(","),
        "crawl_rate_limit_sec": float(os.getenv("CRAWL_RATE_LIMIT_SEC", "1.0")),
        "crawl_max_concurrency": int(os.getenv("CRAWL_MAX_CONCURRENCY", "3")),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "ui_host": os.getenv("UI_HOST", "0.0.0.0"),
        "ui_port": int(os.getenv("UI_PORT", "8501")),
    }
