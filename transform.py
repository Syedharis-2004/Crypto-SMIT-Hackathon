import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataTransformer:
    def transform(self, raw_data):
        if not raw_data:
            logger.warning("No data to transform.")
            return None
        
        try:
            df = pd.DataFrame(raw_data)
            
            # Filter necessary columns
            cols = [
                'id', 'symbol', 'name', 'current_price', 'market_cap', 
                'total_volume', 'price_change_24h', 'market_cap_rank'
            ]
            df = df[cols]
            
            # Rename 'id' to 'coin_id' to match schema
            df.rename(columns={'id': 'coin_id'}, inplace=True)
            
            # Handle nulls
            df.dropna(subset=['coin_id', 'current_price'], inplace=True)
            
            # Feature engineering: volatility_score = abs(price_change_24h) * total_volume
            df['volatility_score'] = df['price_change_24h'].abs() * df['total_volume']
            
            # Metadata
            df['extracted_at'] = datetime.now()
            
            # Ensure numeric types
            numeric_cols = ['current_price', 'market_cap', 'total_volume', 'price_change_24h', 'market_cap_rank', 'volatility_score']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            logger.info(f"Transformed data for {len(df)} coins.")
            return df
        except Exception as e:
            logger.error(f"Error during transformation: {e}")
            return None
