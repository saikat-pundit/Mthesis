import pandas as pd
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES_MAP = {
    "3M": "DGS3MO",
    "2Y": "DGS2",
    "5Y": "DGS5",
    "10Y": "DGS10",
    "30Y": "DGS30"
}

def fetch_historical_series(series_id, start_date, end_date):
    """Fetch historical data for a series between dates."""
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date
    }
    
    all_data = []
    offset = 0
    
    while True:
        params["offset"] = offset
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code != 200:
            print(f"❌ Error fetching {series_id}: {response.status_code}")
            break
        
        data = response.json()
        observations = data.get("observations", [])
        
        if not observations:
            break
        
        for obs in observations:
            date = obs["date"]
            value = obs["value"]
            if value != ".":
                all_data.append({"date": date, "tenure": series_id, "value": float(value)})
        
        # Check if we have all data
        if len(observations) < 1000:  # FRED returns max 1000 per request
            break
        
        offset += 1000
        time.sleep(0.5)  # Be nice to the API
    
    return all_data

def build_historical_csv():
    """Fetch all historical data from 2019-01-01 to present."""
    start_date = "2019-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📅 Fetching historical data from {start_date} to {end_date}")
    
    # Collect data for all tenors
    all_data = []
    for tenure, series_id in SERIES_MAP.items():
        print(f"⏳ Fetching {tenure} ({series_id})...")
        series_data = fetch_historical_series(series_id, start_date, end_date)
        print(f"✅ Got {len(series_data)} data points for {tenure}")
        all_data.extend(series_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    if df.empty:
        print("❌ No data fetched!")
        return None
    
    # Pivot to wide format
    df_pivot = df.pivot(index="date", columns="tenure", values="value").reset_index()
    
    # Sort by date
    df_pivot = df_pivot.sort_values("date")
    
    # Reorder columns
    df_pivot = df_pivot[["date", "3M", "2Y", "5Y", "10Y", "30Y"]]
    
    # Remove rows where all yields are NaN
    df_pivot = df_pivot.dropna(subset=["3M", "2Y", "5Y", "10Y", "30Y"], how="all")
    
    # Save to CSV
    filename = "data/yield_history.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df_pivot.to_csv(filename, index=False)
    print(f"✅ Saved {len(df_pivot)} rows to {filename}")
    
    # Show stats
    print(f"\n📊 Data range: {df_pivot['date'].min()} to {df_pivot['date'].max()}")
    print(f"📊 Total trading days: {len(df_pivot)}")
    print("\n📈 Latest data:")
    print(df_pivot.tail())
    
    return df_pivot

if __name__ == "__main__":
    build_historical_csv()
