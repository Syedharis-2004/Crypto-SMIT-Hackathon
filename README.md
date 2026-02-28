# Real-Time Crypto Analytics Platform

A production-ready ETL pipeline and real-time dashboard for cryptocurrency market analysis.

## Features

- **Live Data Extraction**: Fetches top 20 coins from CoinGecko API.
- **Robust ETL**: Extracts, transforms (cleans + feature engineering), and loads data every 5 minutes.
- **PostgreSQL Integration**: High-performance connection pooling and UPSERT logic.
- **Real-Time Dashboard**: Streamlit-based UI with KPI cards, Plotly charts, and auto-refresh.
- **Advanced Analysis**: Custom SQL-based insights for gainers, volume, and volatility.

## Tech Stack

- **Language**: Python 3.11+
- **Data**: Pandas, Requests
- **Database**: PostgreSQL, Psycopg2
- **Scheduler**: APScheduler
- **Frontend**: Streamlit, Plotly

## Project Structure

```text
crypto_analytics/
├── config.py           # Environment management
├── database.py         # DB setup & connection pooling
├── extract.py          # API data extraction
├── transform.py        # Data cleaning & engineering
├── load.py             # Data loading (UPSERT)
├── analysis.py         # Advanced SQL queries
├── etl_pipeline.py     # ETL Orchestrator (Scheduler)
├── dashboard.py        # Streamlit UI
├── requirements.txt    # Dependencies
└── .env.example        # Environment template
```

## Setup Instructions

### 1. Database Setup

- Install PostgreSQL.
- Create a database named `crypto_db`.
- Run the application; `database.py` will automatically initialize the schema and indexes.

### 2. Environment Configuration

- Copy `.env.example` to `.env`.
- Update your database credentials:
  ```env
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=crypto_db
  DB_USER=postgres
  DB_PASSWORD=your_password
  ```

### 3. Installation

```bash
pip install -r requirements.txt
```

### 4. Running the Platform

#### Start the ETL Pipeline (Terminal 1)

```bash
python etl_pipeline.py
```

_The pipeline will run immediately and then every 5 minutes._

#### Start the Dashboard (Terminal 2)

```bash
streamlit run dashboard.py
```

## Bonus Implementation Details

- **Volatility Score**: Calculated as `abs(24h_price_change) * volume`.
- **Atomic Operations**: Uses database transactions for safe loading.
- **Connection Pooling**: Optimized for high-concurrency dashboard reads.
