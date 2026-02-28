import logging
import psycopg2
from psycopg2 import pool
import sqlite3
from config import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            if config.DB_TYPE == "postgresql":
                cls._initialize_pg_pool()
            else:
                logger.info("Using SQLite for local database.")
            cls.initialize_schema()
        return cls._instance

    @classmethod
    def _initialize_pg_pool(cls):
        try:
            cls._pool = pool.SimpleConnectionPool(
                1, 10,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            logger.info("PostgreSQL connection pool initialized.")
        except Exception as e:
            logger.error(f"Error initializing PG pool: {e}. Falling back to SQLite.")
            config.DB_TYPE = "sqlite"

    def get_connection(self):
        if config.DB_TYPE == "postgresql" and self._pool:
            return self._pool.getconn()
        else:
            conn = sqlite3.connect("crypto_local.db")
            conn.row_factory = sqlite3.Row
            return conn

    def release_connection(self, conn):
        if config.DB_TYPE == "postgresql" and self._pool:
            self._pool.putconn(conn)
        else:
            conn.close()

    @classmethod
    def initialize_schema(cls):
        # SQL-agnostic table creation (mostly)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS crypto_market (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT UNIQUE,
            symbol TEXT,
            name TEXT,
            current_price FLOAT,
            market_cap BIGINT,
            total_volume BIGINT,
            price_change_24h FLOAT,
            market_cap_rank INTEGER,
            volatility_score FLOAT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        # PostgreSQL specific adjustments handled via replacement or generic SQL
        if config.DB_TYPE == "postgresql":
            create_table_sql = create_table_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")

        conn = None
        try:
            db = DatabaseManager()
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(create_table_sql)
            
            # Indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_coin_id ON crypto_market (coin_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_extracted_at ON crypto_market (extracted_at);")
            
            conn.commit()
            logger.info("Database schema initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
        finally:
            if conn:
                db.release_connection(conn)

    def get_placeholder(self):
        return "%s" if config.DB_TYPE == "postgresql" else "?"

db_manager = DatabaseManager()
