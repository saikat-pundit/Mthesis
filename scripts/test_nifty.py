import requests
import json
from datetime import datetime

def fetch_index_data(index_type, start_date, end_date):
    url = f"https://www.nseindia.com/api/historicalOR/indicesHistory?indexType={index_type}&from={start_date}&to={end_date}&csv=true"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.nseindia.com',
        'Priority': 'u=0, i',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0'
    }
    try:
        print(f"Fetching {index_type} from {start_date} to {end_date}...")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text[:200]}")
            return None
        data = response.json()
        print(f"Data received: {len(data.get('data', []))} records")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    start_date = "01-07-2026"
    end_date = "05-07-2026"
    
    print("=== Testing NIFTY 50 ===")
    nifty_data = fetch_index_data('NIFTY%2050', start_date, end_date)
    if nifty_data and nifty_data.get('data'):
        for item in nifty_data['data']:
            print(f"Date: {item.get('EOD_TIMESTAMP')}, Close: {item.get('EOD_CLOSE_INDEX_VAL')}")
    
    print("\n=== Testing BANK NIFTY ===")
    banknifty_data = fetch_index_data('NIFTY%20BANK', start_date, end_date)
    if banknifty_data and banknifty_data.get('data'):
        for item in banknifty_data['data']:
            print(f"Date: {item.get('EOD_TIMESTAMP')}, Close: {item.get('EOD_CLOSE_INDEX_VAL')}")

if __name__ == "__main__":
    main()
