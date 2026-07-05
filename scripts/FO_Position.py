import requests
import csv
from datetime import datetime, timedelta
import os
import sys
import time
import json

def generate_dates(start_date_str, end_date_str):
    start = datetime.strptime(start_date_str, "%d%m%Y")
    end = datetime.strptime(end_date_str, "%d%m%Y")
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%d%m%Y"))
        current += timedelta(days=1)
    return dates

def fetch_index_data(index_type, start_date, end_date):
    url = f"https://www.nseindia.com/api/historicalOR/indicesHistory?indexType={index_type}&from={start_date}&to={end_date}&csv=true"
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
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
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {}
        
        try:
            data = response.json()
            index_data = {}
            for item in data.get('data', []):
                date_str = item.get('EOD_TIMESTAMP', '')
                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                        date_key = date_obj.strftime('%d%m%Y')
                        index_data[date_key] = item.get('EOD_CLOSE_INDEX_VAL', 0)
                    except:
                        continue
            return index_data
        except json.JSONDecodeError:
            cleaned_text = response.text.replace('\x00', '')
            try:
                data = json.loads(cleaned_text)
                index_data = {}
                for item in data.get('data', []):
                    date_str = item.get('EOD_TIMESTAMP', '')
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                            date_key = date_obj.strftime('%d%m%Y')
                            index_data[date_key] = item.get('EOD_CLOSE_INDEX_VAL', 0)
                        except:
                            continue
                return index_data
            except:
                return {}
    except Exception as e:
        print(f"Error fetching {index_type}: {e}")
        return {}

def fetch_usdinr_data(start_date, end_date):
    url = f"https://www.nseindia.com/api/historicalOR/rbi-reference-rate-stats?from={start_date}&to={end_date}&csv=true"
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
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
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {}
        
        try:
            data = response.json()
            usdinr_data = {}
            for item in data.get('data', []):
                date_str = item.get('TRADE_DATE', '')
                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                        date_key = date_obj.strftime('%d%m%Y')
                        usdinr_data[date_key] = item.get('USDINR', 0)
                    except:
                        continue
            return usdinr_data
        except json.JSONDecodeError:
            cleaned_text = response.text.replace('\x00', '')
            try:
                data = json.loads(cleaned_text)
                usdinr_data = {}
                for item in data.get('data', []):
                    date_str = item.get('TRADE_DATE', '')
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                            date_key = date_obj.strftime('%d%m%Y')
                            usdinr_data[date_key] = item.get('USDINR', 0)
                        except:
                            continue
                return usdinr_data
            except:
                return {}
    except Exception as e:
        print(f"Error fetching USDINR: {e}")
        return {}

def fetch_vix_data(start_date, end_date):
    url = f"https://www.nseindia.com/api/historicalOR/vixhistory?from={start_date}&to={end_date}&csv=true"
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
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
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {}
        
        try:
            data = response.json()
            vix_data = {}
            for item in data.get('data', []):
                date_str = item.get('EOD_TIMESTAMP', '')
                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                        date_key = date_obj.strftime('%d%m%Y')
                        vix_data[date_key] = item.get('EOD_CLOSE_INDEX_VAL', 0)
                    except:
                        continue
            return vix_data
        except json.JSONDecodeError:
            cleaned_text = response.text.replace('\x00', '')
            try:
                data = json.loads(cleaned_text)
                vix_data = {}
                for item in data.get('data', []):
                    date_str = item.get('EOD_TIMESTAMP', '')
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                            date_key = date_obj.strftime('%d%m%Y')
                            vix_data[date_key] = item.get('EOD_CLOSE_INDEX_VAL', 0)
                        except:
                            continue
                return vix_data
            except:
                return {}
    except Exception as e:
        print(f"Error fetching VIX: {e}")
        return {}

def fetch_cash_market_data(start_date, end_date):
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
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
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {}
        
        try:
            data = response.json()
            cash_data = {}
            for item in data:
                date_str = item.get('date', '')
                category = item.get('category', '')
                if date_str and category:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                        date_key = date_obj.strftime('%d%m%Y')
                        if date_key not in cash_data:
                            cash_data[date_key] = {}
                        cash_data[date_key][category] = {
                            'buy': item.get('buyValue', 0),
                            'sell': item.get('sellValue', 0)
                        }
                    except:
                        continue
            return cash_data
        except json.JSONDecodeError:
            cleaned_text = response.text.replace('\x00', '')
            try:
                data = json.loads(cleaned_text)
                cash_data = {}
                for item in data:
                    date_str = item.get('date', '')
                    category = item.get('category', '')
                    if date_str and category:
                        try:
                            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                            date_key = date_obj.strftime('%d%m%Y')
                            if date_key not in cash_data:
                                cash_data[date_key] = {}
                            cash_data[date_key][category] = {
                                'buy': item.get('buyValue', 0),
                                'sell': item.get('sellValue', 0)
                            }
                        except:
                            continue
                return cash_data
            except:
                return {}
    except Exception as e:
        print(f"Error fetching cash market data: {e}")
        return {}

def fetch_and_process(date_str, nifty_data, banknifty_data, usdinr_data, vix_data, cash_data):
    url = f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{date_str}.csv"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            print(f"{date_str}: no data (holiday/weekend)")
            return None
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        if len(lines) < 3:
            print(f"{date_str}: no data (incomplete file)")
            return None
        # Skip first row (header with description)
        header_line = lines[1].strip()
        headers = [h.strip() for h in header_line.split(',')]
        # Remove last 2 columns from header
        headers = headers[:-2]
        # Add DATE, NIFTY50, BANK NIFTY, USDINR, VIX columns
        new_headers = ['DATE', 'NIFTY50', 'BANK NIFTY', 'USDINR', 'VIX'] + headers + ['CASH MARKET BUY', 'CASH MARKET SELL']
        
        nifty_close = nifty_data.get(date_str, '')
        banknifty_close = banknifty_data.get(date_str, '')
        usdinr = usdinr_data.get(date_str, '')
        vix = vix_data.get(date_str, '')
        
        rows = []
        for line in lines[2:]:
            if not line.strip():
                continue
            values = [v.strip() for v in line.split(',')]
            if len(values) != len(headers) + 2:
                continue
            # Skip if the row is TOTAL (last row)
            if values[0].upper() == 'TOTAL':
                continue
            # Remove last 2 columns from data row
            values = values[:-2]
            
            # Get cash market data for this date and client type
            client_type = values[0]
            cash_buy = ''
            cash_sell = ''
            if date_str in cash_data:
                if client_type == 'FII':
                    if 'FII/FPI' in cash_data[date_str]:
                        cash_buy = cash_data[date_str]['FII/FPI']['buy']
                        cash_sell = cash_data[date_str]['FII/FPI']['sell']
                elif client_type == 'DII':
                    if 'DII' in cash_data[date_str]:
                        cash_buy = cash_data[date_str]['DII']['buy']
                        cash_sell = cash_data[date_str]['DII']['sell']
            
            # Add date, index values, usdinr, vix, and cash market data
            new_row = [date_str, nifty_close, banknifty_close, usdinr, vix] + values + [cash_buy, cash_sell]
            rows.append(new_row)
        
        print(f"{date_str}: data fetched ✓")
        return new_headers, rows
    except requests.exceptions.Timeout:
        print(f"{date_str}: timeout - skipping")
        return None
    except requests.exceptions.ConnectionError:
        print(f"{date_str}: connection error - skipping")
        return None
    except Exception as e:
        print(f"{date_str}: error - {e}")
        return None

def get_last_recorded_date():
    output_file = 'data/FO_Position.csv'
    if not os.path.exists(output_file):
        return None
    
    try:
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) <= 1:
                return None
            last_row = rows[-1]
            return last_row[0] if last_row else None
    except Exception as e:
        print(f"Error reading last date: {e}")
        return None

def main():
    output_file = 'data/FO_Position.csv'
    
    last_date = get_last_recorded_date()
    
    if last_date:
        last_date_obj = datetime.strptime(last_date, "%d%m%Y")
        start_date = (last_date_obj + timedelta(days=1)).strftime("%d%m%Y")
        print(f"Last recorded date: {last_date}")
        print(f"Fetching from: {start_date}")
    else:
        start_date = "01062026"
        print(f"No existing data. Fetching from: {start_date}")
    
    end_date = datetime.now().strftime("%d%m%Y")
    
    if datetime.strptime(start_date, "%d%m%Y") > datetime.strptime(end_date, "%d%m%Y"):
        print("No new data to fetch. Already up to date.")
        sys.exit(0)
    
    start_date_api = datetime.strptime(start_date, "%d%m%Y").strftime("%d-%m-%Y")
    end_date_api = datetime.now().strftime("%d-%m-%Y")
    
    print("Fetching NIFTY50 data...")
    nifty_data = fetch_index_data('NIFTY%2050', start_date_api, end_date_api)
    print(f"NIFTY50 data fetched for {len(nifty_data)} days")
    
    print("Fetching BANK NIFTY data...")
    banknifty_data = fetch_index_data('NIFTY%20BANK', start_date_api, end_date_api)
    print(f"BANK NIFTY data fetched for {len(banknifty_data)} days")
    
    print("Fetching USDINR data...")
    usdinr_data = fetch_usdinr_data(start_date_api, end_date_api)
    print(f"USDINR data fetched for {len(usdinr_data)} days")
    
    print("Fetching VIX data...")
    vix_data = fetch_vix_data(start_date_api, end_date_api)
    print(f"VIX data fetched for {len(vix_data)} days")
    
    print("Fetching Cash Market data...")
    cash_data = fetch_cash_market_data(start_date_api, end_date_api)
    print(f"Cash Market data fetched for {len(cash_data)} days")
    
    dates = generate_dates(start_date, end_date)
    
    all_rows = []
    headers = None
    
    for date in dates:
        result = fetch_and_process(date, nifty_data, banknifty_data, usdinr_data, vix_data, cash_data)
        if result:
            h, rows = result
            if headers is None:
                headers = h
            all_rows.extend(rows)
        time.sleep(0.5)
    
    if not all_rows:
        print("No new data to append")
        sys.exit(0)
    
    os.makedirs('data', exist_ok=True)
    
    file_exists = os.path.exists(output_file)
    
    with open(output_file, 'a' if file_exists else 'w', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerows(all_rows)
    
    print(f"Appended {len(all_rows)} rows to {output_file}")
    
    if file_exists:
        with open(output_file, 'r') as f:
            total_rows = len(list(csv.reader(f))) - 1
        print(f"Total rows now: {total_rows}")

if __name__ == "__main__":
    main()
