from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Supabase
    supabase_url:         str = ""
    supabase_anon_key:    str = ""
    supabase_service_key: str = ""

    # LLM (at least one required for AI Analyst feature)
    openai_api_key:     str = ""
    anthropic_api_key:  str = ""
    llm_provider:       str = "anthropic"   # "openai" or "anthropic"
    llm_model:          str = "claude-3-5-haiku-20241022"

    # Server
    backend_url:  str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8501"

    # Data directory (where .nc files are stored locally)
    data_dir: str = "./data"

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
