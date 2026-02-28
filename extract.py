import requests
import json
import logging
from datetime import datetime
import os
from config import config

logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self):
        self.api_url = config.COINGECKO_API_URL
        self.params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": "false"
        }
        self.raw_data_dir = "raw_data"
        if not os.path.exists(self.raw_data_dir):
            os.makedirs(self.raw_data_dir)

    def fetch_data(self):
        try:
            logger.info("Fetching data from CoinGecko API...")
            response = requests.get(self.api_url, params=self.params)
            response.raise_for_status()
            data = response.json()
            
            # Save raw data locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.raw_data_dir, f"crypto_data_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(data, f)
            
            logger.info(f"Successfully fetched {len(data)} coins and saved to {filename}")
            return data
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.error("Rate limit exceeded (429).")
            else:
                logger.error(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None

if __name__ == "__main__":
    extractor = DataExtractor()
    extractor.fetch_data()
