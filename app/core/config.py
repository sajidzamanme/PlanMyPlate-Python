from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "PlanMyPlate"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    
    # Uploads
    UPLOAD_DIR: str = "uploads"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
