"""
Configuration management for HTPA.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class GroqConfig:
    """Groq API configuration."""
    api_key: str
    model: str = "llama-3.3-70b-versatile"
    
    @classmethod
    def from_env(cls) -> Optional["GroqConfig"]:
        """Load config from environment variables."""
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        return cls(
            api_key=api_key,
            model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        )


@dataclass  
class AppConfig:
    """Main application configuration."""
    groq: Optional[GroqConfig] = None
    log_dir: str = "logs/decisions"
    data_dir: str = "data"
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load full application config."""
        load_dotenv()
        return cls(
            groq=GroqConfig.from_env(),
            log_dir=os.getenv("LOG_DIR", "logs/decisions"),
            data_dir=os.getenv("DATA_DIR", "data")
        )


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create the global config."""
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config


def set_groq_key(api_key: str, model: str = "llama-3.1-70b-versatile"):
    """Manually set Groq API key (useful for UI)."""
    global _config
    if _config is None:
        _config = AppConfig.load()
    _config.groq = GroqConfig(api_key=api_key, model=model)
