import logging
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from extract import DataExtractor
from transform import DataTransformer
from load import DataLoader
from config import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()

    def run_etl(self):
        logger.info("Starting ETL cycle...")
        try:
            # 1. Extract
            raw_data = self.extractor.fetch_data()
            if not raw_data:
                logger.error("Failed to extract data.")
                return

            # 2. Transform
            df = self.transformer.transform(raw_data)
            if df is None or df.empty:
                logger.error("Failed to transform data.")
                return

            # 3. Load
            self.loader.load(df)
            logger.info("ETL cycle completed successfully.")
        except Exception as e:
            logger.error(f"Critical error in ETL pipeline: {e}", exc_info=True)

    def start_scheduler(self):
        scheduler = BlockingScheduler()
        # Run immediately on start
        self.run_etl()
        # Schedule periodic runs
        scheduler.add_job(self.run_etl, 'interval', minutes=config.ETL_INTERVAL_MINUTES)
        
        logger.info(f"Scheduler started. ETL will run every {config.ETL_INTERVAL_MINUTES} minutes.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.start_scheduler()
