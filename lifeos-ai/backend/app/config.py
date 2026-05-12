"""
Configuration management for LifeOS AI
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    """Application settings from environment variables"""
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    # App settings
    APP_NAME: str = "LifeOS AI"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./lifeos.db"  # Default SQLite, override with PostgreSQL
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Neo4j settings
    NEO4J_URL: str = "neo4j://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # ChromaDB settings
    CHROMADB_PATH: str = "./data/chromadb"
    
    # LLM settings
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_API_KEY: str = ""  # Set from environment
    
    # Sentiment analysis settings
    SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    
    # Bandit learning settings
    BANDIT_EPSILON: float = 0.1
    BANDIT_DECAY_RATE: float = 0.95
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
