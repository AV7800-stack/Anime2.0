import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str = os.getenv("MONGO_URI", os.getenv("MONGO_URL", "mongodb://localhost:27017"))
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-animeflix-prod")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()