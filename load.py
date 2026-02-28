import logging
from database import db_manager
from config import config

logger = logging.getLogger(__name__)

class DataLoader:
    def load(self, df):
        if df is None or df.empty:
            logger.warning("No data to load.")
            return
        
        placeholder = db_manager.get_placeholder()
        
        # PostgreSQL uses %s, SQLite uses ?
        # The query below is compatible with both for the core INSERT part
        upsert_query = f"""
        INSERT INTO crypto_market (
            coin_id, symbol, name, current_price, market_cap, 
            total_volume, price_change_24h, market_cap_rank, 
            volatility_score, extracted_at
        )
        VALUES ({', '.join([placeholder]*10)})
        ON CONFLICT (coin_id) DO UPDATE SET
            symbol = EXCLUDED.symbol,
            name = EXCLUDED.name,
            current_price = EXCLUDED.current_price,
            market_cap = EXCLUDED.market_cap,
            total_volume = EXCLUDED.total_volume,
            price_change_24h = EXCLUDED.price_change_24h,
            market_cap_rank = EXCLUDED.market_cap_rank,
            volatility_score = EXCLUDED.volatility_score,
            extracted_at = EXCLUDED.extracted_at;
        """
        
        conn = None
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            # Prepare data for batch insert
            # SQLite compatibility: Convert timestamps to string
            if config.DB_TYPE == "sqlite":
                df['extracted_at'] = df['extracted_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            data_list = [tuple(x) for x in df.to_numpy()]
            cur.executemany(upsert_query, data_list)
            conn.commit()
            logger.info(f"Successfully loaded {len(df)} records into the database.")
        except Exception as e:
            logger.error(f"Error during loading: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                db_manager.release_connection(conn)
