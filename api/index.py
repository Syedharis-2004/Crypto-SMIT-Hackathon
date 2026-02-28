from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from analysis import CryptoAnalysis
import os

app = FastAPI(title="Crypto Intel API")
analysis = CryptoAnalysis()

# Serve static files from the root static directory
# Vercel's relative paths start from the project root
static_path = os.path.join(os.path.dirname(__file__), "..", "static")

@app.get("/")
async def read_index():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "Dashboard index not found"}

@app.get("/api/market-data")
async def get_market_data():
    df = analysis.get_all_data()
    if df.empty:
        return {"error": "No data available"}
    return df.to_dict(orient="records")

@app.get("/api/summary")
async def get_summary():
    df = analysis.get_all_data()
    if df.empty:
        return {"error": "No data available"}
    
    total_market_cap = float(df['market_cap'].sum())
    highest_gainer = df.iloc[df['price_change_24h'].idxmax()].to_dict()
    most_volatile = df.iloc[df['volatility_score'].idxmax()].to_dict()
    avg_price = float(df['current_price'].mean())
    
    return {
        "total_market_cap": total_market_cap,
        "highest_gainer": highest_gainer,
        "most_volatile": most_volatile,
        "avg_price": avg_price,
        "last_updated": df['extracted_at'].max()
    }

@app.get("/api/search")
async def search_coin(q: str):
    df = analysis.get_all_data()
    if df.empty:
        return {"error": "No data available"}
    
    q = q.lower()
    result = df[
        (df['name'].str.lower().str.contains(q, na=False)) | 
        (df['symbol'].str.lower().str.contains(q, na=False))
    ]
    
    if result.empty:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    return result.to_dict(orient="records")

# Static files should be served via vercel.json for better performance, 
# but keeping this as a fallback if needed for certain assets
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
