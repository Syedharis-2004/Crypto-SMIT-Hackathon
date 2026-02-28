import pandas as pd
import logging
from database import db_manager

logger = logging.getLogger(__name__)

class CryptoAnalysis:
    def get_top_gainers(self, n=5):
        placeholder = db_manager.get_placeholder()
        query = f"SELECT coin_id, symbol, name, price_change_24h FROM crypto_market ORDER BY price_change_24h DESC LIMIT {placeholder}"
        return self._run_query(query, (n,))

    def get_top_by_market_cap(self, n=5):
        placeholder = db_manager.get_placeholder()
        query = f"SELECT coin_id, symbol, name, market_cap FROM crypto_market ORDER BY market_cap DESC LIMIT {placeholder}"
        return self._run_query(query, (n,))

    def get_market_summary(self):
        query = "SELECT AVG(current_price) as avg_price, SUM(market_cap) as total_market_cap, AVG(market_cap) as avg_market_cap FROM crypto_market"
        return self._run_query(query)

    def get_volatility_ranking(self, n=5):
        placeholder = db_manager.get_placeholder()
        query = f"SELECT coin_id, symbol, name, volatility_score FROM crypto_market ORDER BY volatility_score DESC LIMIT {placeholder}"
        return self._run_query(query, (n,))

    def get_all_data(self):
        query = "SELECT * FROM crypto_market ORDER BY market_cap DESC"
        return self._run_query(query)

    def _run_query(self, query, params=None):
        conn = None
        try:
            conn = db_manager.get_connection()
            # Since we want it to be compatible with both
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            
            # For SQLiteRow or psycopg2 cursor
            if hasattr(cur, 'description'):
                cols = [desc[0] for desc in cur.description]
                data = cur.fetchall()
                return pd.DataFrame(data, columns=cols)
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error running query: {e}")
            return pd.DataFrame()
        finally:
            if conn:
                db_manager.release_connection(conn)

if __name__ == "__main__":
    analysis = CryptoAnalysis()
    print(analysis.get_top_gainers())
