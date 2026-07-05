# script/test_nifty.py
import requests
import csv
from io import StringIO
from datetime import datetime

def fetch_index_data_csv(index_type, start_date, end_date):
    session = requests.Session()
    
    # Initial request to get cookies
    try:
        session.get('https://www.nseindia.com', headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0'
        }, timeout=10)
    except:
        pass
    
    # Request CSV directly
    url = f"https://www.nseindia.com/api/historicalOR/indicesHistory?indexType={index_type}&from={start_date}&to={end_date}&csv=true"
    headers = {
        'Accept': 'text/csv,application/json,text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.nseindia.com',
        'Referer': 'https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0'
    }
    try:
        print(f"Fetching {index_type} from {start_date} to {end_date}...")
        response = session.get(url, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text[:500]}")
            return {}
        
        # Parse CSV response
        index_data = {}
        csv_reader = csv.DictReader(StringIO(response.text))
        for row in csv_reader:
            date_str = row.get('EOD_TIMESTAMP', '')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                    date_key = date_obj.strftime('%d%m%Y')
                    index_data[date_key] = row.get('EOD_CLOSE_INDEX_VAL', 0)
                except:
                    continue
        
        print(f"Data received: {len(index_data)} records")
        return index_data
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    start_date = "01-07-2026"
    end_date = "05-07-2026"
    
    print("=== Testing NIFTY 50 ===")
    nifty_data = fetch_index_data_csv('NIFTY%2050', start_date, end_date)
    for date, close in nifty_data.items():
        print(f"Date: {date}, Close: {close}")
    
    print("\n=== Testing BANK NIFTY ===")
    banknifty_data = fetch_index_data_csv('NIFTY%20BANK', start_date, end_date)
    for date, close in banknifty_data.items():
        print(f"Date: {date}, Close: {close}")

if __name__ == "__main__":
    main()
