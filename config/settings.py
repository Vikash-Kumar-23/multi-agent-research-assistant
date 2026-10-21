from functools import lru_cache
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    tavily_api_key: str = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    max_search_results: int = Field(default=5, ge=1, le=20)
    max_sources_to_read: int = Field(default=5, ge=1, le=20)
    max_chars_per_source: int = Field(default=12000, ge=1000, le=50000)
    request_timeout: int = Field(default=15, ge=3, le=60)
    max_report_tokens: int = Field(default=4000, ge=500, le=16000)
    temperature: float = Field(default=0.2, ge=0, le=2)

    @classmethod
    def from_env(cls) -> "Settings":
        values = {"max_search_results": os.getenv("MAX_SEARCH_RESULTS", 5),
                  "max_sources_to_read": os.getenv("MAX_SOURCES_TO_READ", 5),
                  "max_chars_per_source": os.getenv("MAX_CHARS_PER_SOURCE", 12000),
                  "request_timeout": os.getenv("REQUEST_TIMEOUT", 15),
                  "max_report_tokens": os.getenv("MAX_REPORT_TOKENS", 4000),
                  "temperature": os.getenv("TEMPERATURE", 0.2)}
        return cls(**values)

    @property
    def missing_keys(self) -> list[str]:
        return [name for name, value in (("GEMINI_API_KEY", self.gemini_api_key), ("TAVILY_API_KEY", self.tavily_api_key)) if not value or "your_" in value]

    def validate_credentials(self) -> None:
        missing = self.missing_keys
        if missing:
            raise RuntimeError("Missing required configuration: " + ", ".join(missing) + ". Add them to the project-root .env file.")


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
