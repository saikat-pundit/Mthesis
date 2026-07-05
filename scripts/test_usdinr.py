# script/test_usdinr.py
import requests
import csv
from io import StringIO
from datetime import datetime

def fetch_usdinr_data(start_date, end_date):
    url = f"https://www.nseindia.com/api/historicalOR/rbi-reference-rate-stats?from={start_date}&to={end_date}&csv=true"
    
    headers = {
        'Accept': 'text/csv,application/json,text/plain, */*',
        'Accept-Encoding': 'identity',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.nseindia.com',
        'Referer': 'https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0'
    }
    
    try:
        print(f"Fetching USDINR from {start_date} to {end_date}...")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code != 200:
            print(f"Response: {response.text[:500]}")
            return {}
        
        # Parse CSV response
        usdinr_data = {}
        csv_reader = csv.DictReader(StringIO(response.text))
        
        print(f"CSV headers: {csv_reader.fieldnames}")
        
        for row in csv_reader:
            date_str = row.get('Trade Date', '').strip()
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                    date_key = date_obj.strftime('%d%m%Y')
                    usdinr_value = row.get('1 USD ', '0').strip()
                    if usdinr_value:
                        usdinr_data[date_key] = float(usdinr_value)
                        print(f"Date: {date_key}, USDINR: {usdinr_value}")
                except Exception as e:
                    print(f"Date parsing error for {date_str}: {e}")
                    continue
        
        return usdinr_data
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    start_date = "01-06-2026"
    end_date = "05-07-2026"
    
    print("=== Testing USDINR Data Fetch ===")
    usdinr_data = fetch_usdinr_data(start_date, end_date)
    
    print(f"\nTotal USDINR records: {len(usdinr_data)}")
    for date, value in usdinr_data.items():
        print(f"Date: {date}, USDINR: {value}")

if __name__ == "__main__":
    main()
