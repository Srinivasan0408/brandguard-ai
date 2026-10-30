import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "BrandGuard AI"
    APP_VERSION: str = "3.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "brandguard-ai-round3-insecure-dev-secret-key-32chars")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Supabase (optional for demo / fallback to local SQLite)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # LLM Settings (optional - fallback to deterministic engine)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "none")  # 'openai', 'gemini', 'none'
    
    # Local Storage
    DATABASE_FILE: str = os.getenv("DATABASE_FILE", "brandguard.db")
    MAX_UPLOAD_SIZE_BYTES: int = 2 * 1024 * 1024  # 2MB max for text files

    @property
    def has_supabase(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)
        
    @property
    def has_llm(self) -> bool:
        return bool(self.OPENAI_API_KEY or self.GEMINI_API_KEY)

settings = Settings()
