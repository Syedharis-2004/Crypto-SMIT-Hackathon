from etl_pipeline import ETLPipeline
import logging
from config import config

logging.basicConfig(level=config.LOG_LEVEL)

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run_etl()
