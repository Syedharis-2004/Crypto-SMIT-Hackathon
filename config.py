import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "crypto_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # Default to sqlite for local runs
    
    COINGECKO_API_URL = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3/coins/markets")
    ETL_INTERVAL_MINUTES = int(os.getenv("ETL_INTERVAL_MINUTES", 5))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

config = Config()
