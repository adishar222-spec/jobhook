import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-me")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/career_assistant")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    JWT_ACCESS_TOKEN_EXPIRES = 3600       # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 7 # 7 days
    # Job scraping
    SCRAPE_LIMIT = int(os.getenv("SCRAPE_LIMIT", 30))            # max jobs per platform
    SCRAPE_CACHE_TTL = int(os.getenv("SCRAPE_CACHE_TTL", 1800)) # cache TTL seconds (30 min)
    SCRAPE_HEADLESS = os.getenv("SCRAPE_HEADLESS", "true") == "true"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/career_assistant_test"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
