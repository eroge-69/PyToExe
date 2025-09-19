import http.client
import json
import time
import pyotp
import pandas as pd
import requests
from typing import Dict, Any, List, Optional
from SmartApi import SmartConnect
import os
import math
from scipy.stats import norm
import sqlite3
import logging
import pytz
import tenacity
import gspread
from gspread_dataframe import set_with_dataframe
import traceback
import threading
from datetime import datetime, timedelta, timezone, date
import angellogin as l

# Global variables
money_flow_data = []
previous_data = pd.DataFrame()
last_aggregation_minute = None

os.chdir('/home/vamshi/angelone')

# Configure logging
logging.getLogger('SmartApi').handlers = []  # Clear SmartApi default handlers
logging.basicConfig(
    filename='option_chain.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

spreadsheet_id = l.spreadsheet_id

api_key = l.api_key
client_id = l.client_id
password = l.password
totp_secret = l.totp_secret

# Time zone
IST = pytz.timezone('Asia/Kolkata')

# Initialize gspread client
try:
    gc = gspread.service_account(filename='/home/vamshi/angelone/gupta_fixing/sonic-ivy-403017-bc15df409bbf.json')
except Exception as e:
    print(f"Failed to initialize gspread client: {e}")
    logger.error(f"Failed to initialize gspread client: {e}")
    exit(1)

# Retry decorator for Google Sheets
@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_fixed(5),
    retry=tenacity.retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: print(f"Retrying Google Sheets operation (attempt {retry_state.attempt_number})...") or logger.info(f"Retrying Google Sheets operation (attempt {retry_state.attempt_number})...")
)
def update_google_sheet(gc, spreadsheet_id, df, sheet_name="Sheet1"):
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.get_all_worksheets()[0]
            print(f"Worksheet '{sheet_name}' not found. Using the first worksheet instead.")
            logger.info(f"Worksheet '{sheet_name}' not found. Using the first worksheet instead.")
        
        worksheet.clear()
        set_with_dataframe(worksheet, df)
        print("Data exported to Google Sheet successfully.")
        logger.info("Data exported to Google Sheet successfully.")
    except Exception as e:
        print(f"Error exporting data to Google Sheet: {e}")
        logger.error(f"Error exporting data to Google Sheet: {e}")
        raise

# Load and clean instrument data
url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
response = requests.get(url)
response.raise_for_status()
data = response.json()
token_df = pd.DataFrame(data)

# Clean and convert columns
token_df['expiry'] = pd.to_datetime(token_df['expiry'], format='%d%b%Y', errors='coerce').dt.strftime('%d-%b-%Y')
token_df['expiry_date'] = pd.to_datetime(token_df['expiry'], format='%d-%b-%Y', errors='coerce').dt.date
token_df['strike'] = pd.to_numeric(token_df['strike'], errors='coerce')

def save_to_csv(df: pd.DataFrame, filename: str):
    try:
        # Define expected columns based on DataFrame type
        if 'strike' in df.columns:
            expected_columns = ['timestamp', 'strike', 'call_money_flow', 'put_money_flow', 'net_strike_money_flow', 'total_mf']
        else:
            expected_columns = ['minute', 'total_mf_sum', 'total_mf_avg', 'data_points', 'call_mf_sum', 'put_mf_sum', 'avg_strikes']
        
        # Check for missing columns
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: DataFrame missing columns {missing_columns}. Found: {df.columns.tolist()}")
            logger.warning(f"Missing columns in {filename}: {missing_columns}")
            return
        
        # Save to CSV
        if os.path.exists(filename) and os.stat(filename).st_size > 0:
            df[expected_columns].to_csv(filename, mode='a', header=False, index=False)
        else:
            df[expected_columns].to_csv(filename, mode='w', header=True, index=False)
        print(f"Saved {len(df)} rows to {filename}")
        logger.info(f"Saved {len(df)} rows to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")
        logger.error(f"Error saving {filename}: {e}")

# Black-Scholes helper functions
def black_scholes_greeks(S: float, K: float, T: float, r: float, sigma: float) -> Dict[str, float]:
    try:
        S = float(S)
        K = float(K)
        T = float(T)
        r = float(r)
        sigma = float(sigma)
    except (ValueError, TypeError):
        return {'gamma': 0.0, 'vega': 0.0, 'delta': 0.0}

    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {'gamma': 0.0, 'vega': 0.0, 'delta': 0.0}
    
    try:
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * norm.pdf(d1) * math.sqrt(T) / 100
        delta = norm.cdf(d1)
        return {'gamma': gamma, 'vega': vega, 'delta': delta}
    except (ValueError, ZeroDivisionError):
        return {'gamma': 0.0, 'vega': 0.0, 'delta': 0.0}

# AngelOne API functions
# Also improve the fetch_data_angelone function to handle empty responses better
def fetch_data_angelone(headers, payload, endpoint="/rest/secure/angelbroking/market/v1/quote/"):
    """
    Improved version with better error handling and timeout
    """
    conn = None
    try:
        conn = http.client.HTTPSConnection("apiconnect.angelone.in", timeout=30)
        conn.request("POST", endpoint, payload, headers)
        res = conn.getresponse()
        
        # Read the response
        data = res.read()
        status = res.status
        
        # Close connection
        conn.close()
        
        # Decode data
        if data:
            decoded_data = data.decode("utf-8")
            return decoded_data, status
        else:
            print(f"Empty response from API endpoint {endpoint}")
            logger.warning(f"Empty response from API endpoint {endpoint}")
            return "", status
            
    except http.client.HTTPException as http_err:
        print(f"HTTP error in fetch_data_angelone: {http_err}")
        logger.error(f"HTTP error in fetch_data_angelone: {http_err}")
        if conn:
            conn.close()
        return "", 0
        
    except Exception as e:
        print(f"General error in fetch_data_angelone: {e}")
        logger.error(f"General error in fetch_data_angelone: {e}")
        if conn:
            conn.close()
        return "", 0

# Add a function to validate expiry format
def validate_and_get_expiry(symbol="NIFTY"):
    """
    Get expiry and validate it exists in token data
    """
    try:
        # Get available expiries for the symbol
        options = token_df[
            (token_df['exch_seg'] == 'NFO') &
            (token_df['name'] == symbol) &
            (token_df['instrumenttype'] == 'OPTIDX') &
            (token_df['expiry_date'].notna())
        ]
        
        if options.empty:
            raise ValueError(f"No options found for {symbol}")
        
        # Get unique expiries and sort them
        today = date.today()
        future_exps = sorted(options[options['expiry_date'] >= today]['expiry_date'].unique())
        
        if not future_exps:
            raise ValueError("No future expiries found")
        
        nearest_date = future_exps[0]
        nearest_expiry_str = options[options['expiry_date'] == nearest_date]['expiry'].iloc[0]
        expiry_date_formatted = nearest_date.strftime("%d-%b-%Y")
        expiry_greek = datetime.strptime(expiry_date_formatted, "%d-%b-%Y").strftime("%d%b%Y").upper()
        
        # Validate that we have options for this expiry
        test_options = token_df[
            (token_df['exch_seg'] == 'NFO') &
            (token_df['name'] == symbol) &
            (token_df['instrumenttype'] == 'OPTIDX') &
            (token_df['expiry'] == expiry_date_formatted)
        ]
        
        print(f"Found {len(test_options)} options for expiry {expiry_date_formatted}")
        logger.info(f"Validated expiry {expiry_date_formatted} with {len(test_options)} options")
        
        return expiry_date_formatted, expiry_greek
        
    except Exception as e:
        print(f"Error in validate_and_get_expiry: {e}")
        logger.error(f"Error in validate_and_get_expiry: {e}")
        raise


def get_new_token(api_key, client_id, password, totp_secret):
    smartApi = SmartConnect(api_key=api_key)
    try:
        otp = pyotp.TOTP(totp_secret).now()
        print(f"Generated TOTP: {otp}")
        data = smartApi.generateSession(client_id, password, otp)
        print(f"Session data: {data}")
        jwt_token = data.get("data", {}).get("jwtToken")
        if not jwt_token:
            raise Exception(f"Failed to retrieve JWT token: {data.get('message', 'No token returned')}")
        if jwt_token.startswith("Bearer "):
            jwt_token = jwt_token[7:]
        print(f"JWT Token: {jwt_token}")
        return jwt_token
    except Exception as e:
        print(f"Login failed: {e}")
        raise

def initialize_headers_angelone(api_key, token):
    return {
        'X-PrivateKey': api_key,
        'Accept': 'application/json',
        'X-SourceID': 'WEB',
        'X-ClientLocalIP': '127.0.0.1',
        'X-ClientPublicIP': '127.0.0.1',
        'X-MACAddress': '00:00:00:00:00:00',
        'X-UserType': 'USER',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

# Function to refresh token if invalid
def refresh_token_if_needed(api_key, client_id, password, totp_secret, headers, current_token):
    try:
        test_payload = json.dumps({"mode": "LTP", "exchangeTokens": {"NSE": ["99926000"]}})
        response_data, status_code = fetch_data_angelone(headers, test_payload)
        print(f"Test token response: {response_data}, Status: {status_code}")
        response_json = json.loads(response_data)
        if response_json.get("message", "").lower().find("invalid token") != -1 or status_code != 200:
            print("Token invalid, refreshing...")
            current_token = get_new_token(api_key, client_id, password, totp_secret)
            headers = initialize_headers_angelone(api_key, current_token)
            print("Token refreshed successfully.")
        return current_token, headers
    except Exception as e:
        print(f"Error testing token: {e}. Attempting to refresh...")
        current_token = get_new_token(api_key, client_id, password, totp_secret)
        headers = initialize_headers_angelone(api_key, current_token)
        return current_token, headers


def get_nearest_expiry(symbol="NIFTY"):
    options = token_df[
        (token_df['exch_seg'] == 'NFO') &
        (token_df['name'] == symbol) &
        (token_df['instrumenttype'] == 'OPTIDX') &
        (token_df['expiry_date'].notna())
    ]
    if options.empty:
        raise ValueError(f"No options found for {symbol}")
    today = date.today()
    future_exps = sorted(options[options['expiry_date'] >= today]['expiry_date'].unique())
    if not future_exps:
        raise ValueError("No future expiries found")
    nearest_date = future_exps[0]
    nearest_expiry_str = options[options['expiry_date'] == nearest_date]['expiry'].iloc[0]
    expiry_date_formatted = nearest_date.strftime("%d-%b-%Y")
    expiry_greek = datetime.strptime(expiry_date_formatted, "%d-%b-%Y").strftime("%d%b%Y").upper()
    return expiry_date_formatted, expiry_greek

def fetch_option_chain_oi(headers, symbol, expiry_date, batch_size):
    """
    Fixed version with better error handling for the JSON parsing issue
    """
    try:
        # Get options data
        options = token_df[
            (token_df['exch_seg'] == 'NFO') &
            (token_df['name'] == symbol) &
            (token_df['instrumenttype'] == 'OPTIDX') &
            (token_df['expiry'] == expiry_date)
        ]
        
        if options.empty:
            print(f"No options found for {symbol} with expiry {expiry_date}")
            logger.warning(f"No options found for {symbol} with expiry {expiry_date}")
            return pd.DataFrame()
        
        df = options.copy()
        df['strikePrice'] = (df['strike'] / 100).astype(int)
        df['optionType'] = df['symbol'].str[-2:]
        tokens = df['token'].tolist()
        
        print(f"Found {len(tokens)} option tokens for {symbol} {expiry_date}")
        logger.info(f"Found {len(tokens)} option tokens for {symbol} {expiry_date}")
        
        # Create batches
        token_batches = [tokens[i:i + batch_size] for i in range(0, len(tokens), batch_size)]
        all_quote_data = []
        
        for batch_idx, batch in enumerate(token_batches):
            print(f"Processing batch {batch_idx + 1}/{len(token_batches)} with {len(batch)} tokens")
            
            payload = json.dumps({
                "mode": "FULL",
                "exchangeTokens": {
                    "NFO": batch
                }
            })
            
            try:
                response_data, status_code = fetch_data_angelone(headers, payload)
                
                # Debug: Print raw response info
                print(f"Batch {batch_idx + 1} - Status Code: {status_code}")
                print(f"Batch {batch_idx + 1} - Response Length: {len(response_data) if response_data else 0}")
                print(f"Batch {batch_idx + 1} - First 100 chars: {response_data[:100] if response_data else 'Empty response'}")
                
                logger.info(f"Batch {batch_idx + 1} - Status: {status_code}, Length: {len(response_data) if response_data else 0}")
                
                # Check if response is empty or invalid
                if not response_data or response_data.strip() == "":
                    print(f"Empty response for batch {batch_idx + 1}")
                    logger.warning(f"Empty response for batch {batch_idx + 1}")
                    continue
                
                # Check for non-200 status codes
                if status_code != 200:
                    print(f"Non-200 status code {status_code} for batch {batch_idx + 1}")
                    logger.warning(f"Non-200 status code {status_code} for batch {batch_idx + 1}")
                    continue
                
                # Try to parse JSON
                try:
                    response_json = json.loads(response_data)
                except json.JSONDecodeError as json_err:
                    print(f"JSON decode error for batch {batch_idx + 1}: {json_err}")
                    print(f"Raw response data: {response_data}")
                    logger.error(f"JSON decode error for batch {batch_idx + 1}: {json_err}")
                    logger.error(f"Raw response: {response_data}")
                    continue
                
                # Check if API response indicates success
                if response_json.get("status"):
                    quote_data = response_json.get("data", {}).get("fetched", [])
                    if quote_data:
                        print(f"Successfully fetched {len(quote_data)} quotes from batch {batch_idx + 1}")
                        all_quote_data.extend(quote_data)
                    else:
                        print(f"No quote data in successful response for batch {batch_idx + 1}")
                        logger.warning(f"No quote data in batch {batch_idx + 1}")
                else:
                    error_message = response_json.get('message', 'Unknown error')
                    print(f"API error for batch {batch_idx + 1}: {error_message}")
                    logger.error(f"API error for batch {batch_idx + 1}: {error_message}")
                    
                    # If it's a token issue, return empty DataFrame to trigger token refresh
                    if "token" in error_message.lower() or "invalid" in error_message.lower():
                        print("Token-related error detected, returning empty DataFrame")
                        return pd.DataFrame()
                
            except Exception as batch_error:
                print(f"Exception processing batch {batch_idx + 1}: {batch_error}")
                logger.error(f"Exception processing batch {batch_idx + 1}: {batch_error}")
                traceback.print_exc()
                continue
        
        # Check if we got any data
        if not all_quote_data:
            print("No quote data retrieved from any batch.")
            logger.warning("No quote data retrieved from any batch")
            return pd.DataFrame()
        
        print(f"Total quotes retrieved: {len(all_quote_data)}")
        logger.info(f"Total quotes retrieved: {len(all_quote_data)}")
        
        # Process the data
        df['token'] = df['token'].astype(str)
        oi_dict = {}
        ltp_dict = {}
        vol_dict = {}
        
        for item in all_quote_data:
            token_str = str(item['symbolToken'])
            oi_dict[token_str] = item.get('opnInterest', 0)
            ltp_dict[token_str] = item.get('ltp', 0)
            vol_dict[token_str] = item.get('tradeVolume', 0)
        
        df['oi'] = df['token'].map(oi_dict).fillna(0).astype(int)
        df['ltp'] = df['token'].map(ltp_dict).fillna(0).astype(float)
        df['vol'] = df['token'].map(vol_dict).fillna(0).astype(int)
        
        # Separate calls and puts
        call_df = df[df['optionType'] == 'CE'][['strikePrice', 'oi', 'ltp', 'vol']].rename(
            columns={'oi': 'call_oi', 'ltp': 'call_ltp', 'vol': 'call_vol'}
        )
        put_df = df[df['optionType'] == 'PE'][['strikePrice', 'oi', 'ltp', 'vol']].rename(
            columns={'oi': 'put_oi', 'ltp': 'put_ltp', 'vol': 'put_vol'}
        )
        
        # Merge calls and puts
        oi_df = pd.merge(call_df, put_df, on='strikePrice', how='outer').fillna(0)
        oi_df['expiry'] = expiry_date
        oi_df = oi_df.sort_values('strikePrice').reset_index(drop=True)
        
        print(f"Final OI DataFrame shape: {oi_df.shape}")
        logger.info(f"Final OI DataFrame created with {len(oi_df)} strikes")
        
        return oi_df
        
    except Exception as e:
        print(f"Error in fetch_option_chain_oi: {e}")
        logger.error(f"Error in fetch_option_chain_oi: {e}")
        traceback.print_exc()
        return pd.DataFrame()



# Fix 2: Improve the retry logic for spot price
@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_fixed(2),
    retry=tenacity.retry_if_result(lambda result: result == 0.0),
    before_sleep=lambda retry_state: logger.info(f"Retrying fetch_spot_price (attempt {retry_state.attempt_number})..."),
    retry_error_callback=lambda retry_state: logger.error("All attempts to fetch spot price failed")
)
def fetch_spot_price(headers, symbol="NIFTY"):
    try:
        index_row = token_df[
            (token_df['name'] == symbol) &
            (token_df['exch_seg'] == 'NSE') &
            (token_df['instrumenttype'] == 'AMXIDX')
        ]
        
        if index_row.empty:
            logger.warning(f"Index not found for {symbol}")
            return 0.0
        
        token = index_row['token'].iloc[0]
        payload = json.dumps({
            "mode": "LTP",
            "exchangeTokens": {
                "NSE": [token]
            }
        })
        
        response_data, status_code = fetch_data_angelone(headers, payload)
        logger.info(f"Spot price response status: {status_code}")
        
        if status_code != 200:
            logger.warning(f"Non-200 status code: {status_code}")
            return 0.0
        
        response_json = json.loads(response_data)
        
        if response_json.get("status") and response_json.get("data", {}).get("fetched"):
            data = response_json["data"]["fetched"][0]
            spot_price = float(data.get('ltp', 0))
            logger.info(f"Successfully fetched spot price: {spot_price}")
            return spot_price
        else:
            logger.warning(f"Invalid response structure: {response_json.get('message', 'No data returned')}")
            return 0.0
            
    except Exception as e:
        logger.error(f"Exception in fetch_spot_price: {e}")
        return 0.0

# Fix 3: Create fallback function for Greeks calculation
def create_fallback_greeks_df(symbol, expiry_date, S, T, r):
    """Fallback function when Greeks API fails"""
    try:
        options = token_df[
            (token_df['exch_seg'] == 'NFO') &
            (token_df['name'] == symbol) &
            (token_df['instrumenttype'] == 'OPTIDX') &
            (token_df['expiry'] == expiry_date)
        ]
        
        if options.empty:
            logger.warning(f"No options found for fallback calculation: {symbol} {expiry_date}")
            return pd.DataFrame()
        
        df = options.copy()
        df['strikePrice'] = (df['strike'] / 100).astype(float)
        df['optionType'] = df['symbol'].str[-2:]
        
        # Initialize Greeks columns
        df['gamma'] = 0
        df['vega'] = 0
        df['delta'] = 0
        df['theta'] = 0
        df['impliedVolatility'] = 20  # Default 20% IV
        df['bs_gamma'] = 0
        df['bs_vega'] = 0
        df['bs_delta'] = 0
        df['expiry'] = expiry_date
        
        # Calculate Black-Scholes Greeks
        for idx, row in df.iterrows():
            K = row['strikePrice']
            sigma = 0.2  # 20% default volatility
            if T > 0 and K > 0 and S > 0:
                greeks = black_scholes_greeks(S, K, T, r, sigma)
                df.at[idx, 'bs_gamma'] = greeks['gamma']
                df.at[idx, 'bs_vega'] = greeks['vega']
                df.at[idx, 'bs_delta'] = greeks['delta']
        
        required_columns = ['strikePrice', 'optionType', 'gamma', 'vega', 'delta', 'theta', 'impliedVolatility', 'expiry']
        return df[required_columns + ['bs_gamma', 'bs_vega', 'bs_delta']]
        
    except Exception as e:
        logger.error(f"Error in fallback Greeks calculation: {e}")
        return pd.DataFrame()


def create_database_and_table(db_name, symbol_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    table_name = f"{symbol_name}_option_chain"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_oi REAL,
        call_ltp REAL,
        call_vol REAL,
        call_gamma REAL,
        call_vega REAL,
        call_delta REAL,
        call_theta REAL,
        call_iv REAL,
        strikePrice REAL,
        put_ltp REAL,
        put_oi REAL,
        put_vol REAL,
        put_gamma REAL,
        put_vega REAL,
        put_delta REAL,
        put_theta REAL,
        put_iv REAL,
        expiry TEXT,
        nifty_spot REAL,
        timestamp TEXT,
        created_at DATETIME DEFAULT (datetime('now', 'localtime', '+05:30'))
    )
    """
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print(f"Database and table {table_name} created/verified successfully")

def load_csv_to_database(df, db_name, symbol_name):
    try:
        required_columns = {'call_oi', 'call_ltp', 'call_vol', 'call_gamma', 'call_vega', 'call_delta', 'call_theta', 
                           'call_iv', 'strikePrice', 'put_ltp', 'put_oi', 'put_vol', 'put_gamma', 
                           'put_vega', 'put_delta', 'put_theta', 'put_iv', 'expiry', 'nifty_spot', 'timestamp'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        conn = sqlite3.connect(db_name)
        table_name = f"{symbol_name}_option_chain"
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['created_at'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            df['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.to_sql(table_name, conn, if_exists='append', index=False, 
                  dtype={'created_at': 'DATETIME'})
        conn.close()
        print(f"Successfully loaded {len(df)} records to {table_name}")
    except Exception as e:
        print(f"Error loading data to database: {e}")
        if 'conn' in locals():
            conn.close()

def fetch_option_chain_with_greeks_angelone(headers, symbol, expiry_date, expiry_str):
    S = fetch_spot_price(headers, symbol)
    if S == 0.0:
        logger.error(f"Failed to fetch valid spot price for {symbol}. Aborting Greeks calculation.")
        return pd.DataFrame()
    
    expiry_dt = datetime.strptime(expiry_date, "%d-%b-%Y").replace(tzinfo=IST)
    today = datetime.now(IST)
    T = (expiry_dt - today).total_seconds() / (365.0 * 24 * 60 * 60)
    
    if T <= 0:
        logger.warning("Expiry is in the past or invalid. Setting T to small positive value.")
        T = 1.0 / 365.0
    
    r = 0.06
    payload = json.dumps({
        "name": symbol,
        "expirydate": expiry_str
    })
    
    try:
        response_data, status_code = fetch_data_angelone(headers, payload, endpoint="/rest/secure/angelbroking/marketData/v1/optionGreek")
        logger.info(f"Raw API response status: {status_code}")
        
        # Parse response FIRST before using it
        response_json = json.loads(response_data)
        
        # Now save the data
        try:
            with open('greek_api_response.json', 'w') as f:
                json.dump(response_json.get('data', []), f, indent=2)
            logger.info("Saved raw API data to greek_api_response.json")
        except Exception as save_error:
            logger.warning(f"Could not save API response: {save_error}")
        
        if response_json.get("status") and response_json.get("data"):
            df = pd.DataFrame(response_json["data"])
            logger.info(f"Greeks DataFrame shape: {df.shape}")
            
            # Rest of the function remains the same...
            df['strikePrice'] = pd.to_numeric(df['strikePrice'], errors='coerce').fillna(0).astype(float)
            df['impliedVolatility'] = pd.to_numeric(df['impliedVolatility'], errors='coerce').fillna(0)
            
            required_columns = ['strikePrice', 'optionType', 'gamma', 'vega', 'delta', 'theta', 'impliedVolatility', 'expiry']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0 if col != 'optionType' and col != 'expiry' else ''
            
            df['expiry'] = pd.to_datetime(df['expiry'], format='%d%b%Y', errors='coerce').dt.strftime('%d-%b-%Y')
            df['bs_gamma'] = 0.0
            df['bs_vega'] = 0.0
            df['bs_delta'] = 0.0
            
            for idx, row in df.iterrows():
                K = row['strikePrice']
                sigma = row['impliedVolatility'] / 100.0 if row['impliedVolatility'] > 0 else 0.2
                if sigma > 0 and T > 0 and K > 0:
                    greeks = black_scholes_greeks(S, K, T, r, sigma)
                    df.at[idx, 'bs_gamma'] = greeks['gamma']
                    df.at[idx, 'bs_vega'] = greeks['vega']
                    df.at[idx, 'bs_delta'] = greeks['delta']
            
            return df[required_columns + ['bs_gamma', 'bs_vega', 'bs_delta']]
        else:
            logger.warning(f"Greeks API failed: {response_json.get('message')}. Falling back to manual calculation.")
            # Fallback logic remains the same...
            
    except Exception as e:
        logger.error(f"Error in Greeks API call: {e}")
        # Fallback to manual calculation
        return create_fallback_greeks_df(symbol, expiry_date, S, T, r)

def calculate_money_flow(current_data, previous_data):
    global money_flow_data
    try:
        print("Starting money flow calculation...")
        print(f"Current data shape: {current_data.shape}, columns: {current_data.columns.tolist()}")
        print(f"Previous data shape: {previous_data.shape}, columns: {previous_data.columns.tolist()}")
        
        if current_data.empty or previous_data.empty:
            print("Current or previous data is empty, skipping money flow calculation")
            logger.warning("Current or previous data is empty in calculate_money_flow")
            return pd.DataFrame()
        
        # Reshape current_data to long format
        calls_long = current_data[['strikePrice', 'call_ltp', 'call_vol', 'expiry']].copy()
        calls_long['optionType'] = 'CE'
        calls_long = calls_long.rename(columns={'call_ltp': 'ltp', 'call_vol': 'volume'})
        puts_long = current_data[['strikePrice', 'put_ltp', 'put_vol', 'expiry']].copy()
        puts_long['optionType'] = 'PE'
        puts_long = puts_long.rename(columns={'put_ltp': 'ltp', 'put_vol': 'volume'})
        current_data_long = pd.concat([calls_long, puts_long], ignore_index=True)
        
        # Reshape previous_data to long format
        calls_long_prev = previous_data[['strikePrice', 'call_ltp', 'call_vol', 'expiry']].copy()
        calls_long_prev['optionType'] = 'CE'
        calls_long_prev = calls_long_prev.rename(columns={'call_ltp': 'ltp', 'call_vol': 'volume'})
        puts_long_prev = previous_data[['strikePrice', 'put_ltp', 'put_vol', 'expiry']].copy()
        puts_long_prev['optionType'] = 'PE'
        puts_long_prev = puts_long_prev.rename(columns={'put_ltp': 'ltp', 'put_vol': 'volume'})
        previous_data_long = pd.concat([calls_long_prev, puts_long_prev], ignore_index=True)
        
        required_columns = ['strikePrice', 'optionType', 'ltp', 'volume']
        current_missing = [col for col in required_columns if col not in current_data_long.columns]
        previous_missing = [col for col in required_columns if col not in previous_data_long.columns]
        
        if current_missing or previous_missing:
            print(f"Current data missing columns: {current_missing}")
            print(f"Previous data missing columns: {previous_missing}")
            logger.warning(f"Current data missing columns: {current_missing}, Previous data missing columns: {previous_missing}")
            return pd.DataFrame()
        
        current_data_long['key'] = current_data_long['strikePrice'].astype(str) + '_' + current_data_long['optionType']
        previous_data_long['key'] = previous_data_long['strikePrice'].astype(str) + '_' + previous_data_long['optionType']
        
        merged = pd.merge(
            current_data_long[['key', 'strikePrice', 'optionType', 'ltp', 'volume']],
            previous_data_long[['key', 'ltp', 'volume']],
            on='key',
            how='inner',
            suffixes=('_current', '_previous')
        )
        
        if merged.empty:
            print("No matching data found for money flow calculation")
            logger.warning("No matching data found for money flow calculation")
            return pd.DataFrame()
        
        print(f"Merged DataFrame shape: {merged.shape}")
        merged['ltp_diff'] = merged['ltp_current'] - merged['ltp_previous']
        merged['volume_diff'] = merged['volume_current'] - merged['volume_previous']
        merged['money_flow'] = merged['ltp_diff'] * merged['volume_diff']
        
        calls = merged[merged['optionType'] == 'CE'].copy()
        puts = merged[merged['optionType'] == 'PE'].copy()
        
        strike_money_flow = []
        strikes = merged['strikePrice'].unique()
        
        for strike in strikes:
            call_mf = calls[calls['strikePrice'] == strike]['money_flow'].sum() if not calls[calls['strikePrice'] == strike].empty else 0
            put_mf = puts[puts['strikePrice'] == strike]['money_flow'].sum() if not puts[puts['strikePrice'] == strike].empty else 0
            net_strike_mf = call_mf - put_mf
            strike_money_flow.append({
                'timestamp': datetime.now(IST),
                'strike': strike,
                'call_money_flow': call_mf,
                'put_money_flow': put_mf,
                'net_strike_money_flow': net_strike_mf
            })
        
        strike_mf_df = pd.DataFrame(strike_money_flow)
        
        if not strike_mf_df.empty:
            total_money_flow = strike_mf_df['net_strike_money_flow'].sum()
            total_call_mf = strike_mf_df['call_money_flow'].sum()
            total_put_mf = strike_mf_df['put_money_flow'].sum()
            strike_mf_df['total_mf'] = total_money_flow
            total_mf_entry = {
                'timestamp': datetime.now(IST),
                'total_money_flow': total_money_flow,
                'call_money_flow': total_call_mf,
                'put_money_flow': total_put_mf,
                'num_strikes': len(strikes)
            }
            money_flow_data.append(total_mf_entry)
            print(f"Total Money Flow: {total_money_flow:,.2f}")
            print(f"Total Call Money Flow: {total_call_mf:,.2f}")
            print(f"Total Put Money Flow: {total_put_mf:,.2f}")
            print(f"Number of strikes analyzed: {len(strikes)}")
            return strike_mf_df
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"Error in calculate_money_flow: {e}")
        logger.error(f"Error in calculate_money_flow: {e}")
        traceback.print_exc()
        return pd.DataFrame()

def aggregate_minute_data():
    global money_flow_data
    if not money_flow_data:
        return pd.DataFrame()
    df = pd.DataFrame(money_flow_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['minute'] = df['timestamp'].dt.floor('Min')
    minute_agg = df.groupby('minute').agg({
        'total_money_flow': ['sum', 'mean', 'count'],
        'call_money_flow': 'sum',
        'put_money_flow': 'sum',
        'num_strikes': 'mean'
    }).round(2)
    minute_agg.columns = ['total_mf_sum', 'total_mf_avg', 'data_points', 'call_mf_sum', 'put_mf_sum', 'avg_strikes']
    minute_agg.reset_index(inplace=True)
    return minute_agg

# Main execution loop
if __name__ == "__main__":
    try:
        current_token = get_new_token(api_key, client_id, password, totp_secret)
        headers_angelone = initialize_headers_angelone(api_key, current_token)
        logger.info("AngelOne Token initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing AngelOne token: {e}")
        exit(1)

    retry_count = 0
    max_retries = 3
    symbol_name = "NIFTY"
    try:
        expiry_date, expiry_greek = validate_and_get_expiry(symbol_name)
        print(f"Using expiry: {expiry_date} ({expiry_greek})")
        logger.info(f"Validated expiry: {expiry_date} ({expiry_greek})")
    except Exception as e:
        logger.error(f"Error getting/validating expiry: {e}")
        error_df = pd.DataFrame([{"Metric": "Error", "Value": f"Failed to get expiry: {str(e)}"}])
        try:
            update_google_sheet(gc, spreadsheet_id, error_df)
        except Exception as sheet_e:
            logger.error(f"Failed to log error to Google Sheet: {sheet_e}")
        exit(1)

    while True:
        try:
            current_token, headers_angelone = refresh_token_if_needed(api_key, client_id, password, totp_secret, headers_angelone, current_token)
            retry_count = 0

            # Fetch spot price first
            nifty_spot = fetch_spot_price(headers_angelone, symbol_name)
            if nifty_spot == 0.0:
                logger.warning("Invalid spot price. Skipping this iteration.")
                error_df = pd.DataFrame([{"Metric": "Error", "Value": "Invalid spot price. Retrying in next iteration."}])
                update_google_sheet(gc, spreadsheet_id, error_df)
                time.sleep(10)
                continue

            angelone_df = fetch_option_chain_with_greeks_angelone(headers_angelone, symbol=symbol_name, expiry_date=expiry_date, expiry_str=expiry_greek)
            logger.info("Greeks dataframe fetched.")
            
            oi_df = fetch_option_chain_oi(headers_angelone, symbol=symbol_name, expiry_date=expiry_date, batch_size=50)
            logger.info("OI dataframe fetched.")

            if not oi_df.empty:
                if not previous_data.empty:
                    strike_mf_df = calculate_money_flow(oi_df, previous_data)
                    if not strike_mf_df.empty:
                        today_date_ist = datetime.now(IST).strftime("%Y-%m-%d")
                        filename = f"strike_money_flow.csv"
                        save_to_csv(strike_mf_df, filename)
                        logger.info("\nTop Money Flow Strikes:")
                        logger.info(strike_mf_df.nlargest(5, 'net_strike_money_flow')[['strike', 'call_money_flow', 'put_money_flow', 'net_strike_money_flow', 'total_mf']].to_string())
                
                previous_data = oi_df.copy()
                
                # Check if a new minute has started
                current_minute = datetime.now(IST).minute
                if last_aggregation_minute is None or current_minute != last_aggregation_minute:
                    minute_agg = aggregate_minute_data()
                    if not minute_agg.empty:
                        today_date_ist = datetime.now(IST).strftime("%Y-%m-%d")
                        minute_filename = f"minute_aggregated_money_flow.csv"
                        save_to_csv(minute_agg.tail(1), minute_filename)
                        logger.info(f"\nLatest Minute Aggregation:")
                        logger.info(minute_agg.tail(1).to_string())
                    last_aggregation_minute = current_minute
            else:
                logger.warning(f"Failed to fetch option chain data for {symbol_name}.")

            if not angelone_df.empty and not oi_df.empty:
                logger.info(f"NIFTY spot price: {nifty_spot}")

                angelone_df['expiry'] = pd.to_datetime(angelone_df['expiry'], format='%d-%b-%Y', errors='coerce').dt.strftime('%d-%b-%Y')
                angelone_ce = angelone_df[angelone_df['optionType'] == 'CE'].copy()
                angelone_ce = angelone_ce.rename(columns={
                    'bs_gamma': 'call_gamma',
                    'bs_vega': 'call_vega',
                    'bs_delta': 'call_delta',
                    'theta': 'call_theta',
                    'impliedVolatility': 'call_iv'
                })
                angelone_pe = angelone_df[angelone_df['optionType'] == 'PE'].copy()
                angelone_pe = angelone_pe.rename(columns={
                    'bs_gamma': 'put_gamma',
                    'bs_vega': 'put_vega',
                    'bs_delta': 'put_delta',
                    'theta': 'put_theta',
                    'impliedVolatility': 'put_iv'
                })
                angelone_pe['put_delta'] = angelone_pe['put_delta'] - 1

                greeks_df = pd.merge(
                    angelone_ce[['strikePrice', 'expiry', 'call_gamma', 'call_vega', 'call_delta', 'call_theta', 'call_iv']],
                    angelone_pe[['strikePrice', 'expiry', 'put_gamma', 'put_vega', 'put_delta', 'put_theta', 'put_iv']],
                    on=['strikePrice', 'expiry'],
                    how='outer'
                )

                combined_df = pd.merge(greeks_df, oi_df, on=['strikePrice', 'expiry'], how='inner')

                if not combined_df.empty:
                    combined_df['nifty_spot'] = nifty_spot
                    combined_df['timestamp'] = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
                    final_df = combined_df[[
                        'call_oi', 'call_ltp', 'call_vol', 'call_gamma', 'call_vega', 'call_delta', 'call_theta', 'call_iv',
                        'strikePrice',
                        'put_ltp', 'put_oi', 'put_vol', 'put_gamma', 'put_vega', 'put_delta', 'put_theta', 'put_iv',
                        'expiry', 'nifty_spot', 'timestamp'
                    ]]
                    filename = f"{symbol_name}_option_chain_output.csv"
                    filename2 = f"{symbol_name}_option_chain_output_full.csv"
                    final_df.to_csv(filename, index=False)
                    final_df.to_csv(filename2, mode='a', header=not os.path.exists(filename2), index=False)
                    logger.info(f"{symbol_name} Option chain saved as {filename}")

                    # Export to Google Sheet
                    option_chain_df = final_df.copy()
                    option_chain_df = option_chain_df.sort_values(by='strikePrice', ascending=True).reset_index(drop=True)
                    data_to_export = []
                    desired_columns = [
                        'call_oi', 'call_ltp', 'call_gamma', 'call_vega', 'call_vol', 'call_iv',
                        'strikePrice',
                        'put_ltp', 'put_oi', 'put_gamma', 'put_vega', 'put_vol', 'put_iv',
                        'expiry', 'nifty_spot', 'timestamp'
                    ]
                    all_columns = ['Metric', 'Value'] + desired_columns

                    if nifty_spot != 0.0:
                        nifty_row = {'Metric': 'Nifty Spot Price', 'Value': nifty_spot}
                        for col in all_columns:
                            if col not in nifty_row:
                                nifty_row[col] = None
                        data_to_export.append(nifty_row)

                    current_time_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                    time_row = {'Metric': 'Time (IST)', 'Value': current_time_ist}
                    for col in all_columns:
                        if col not in time_row:
                            time_row[col] = None
                    data_to_export.append(time_row)

                    option_chain_records = option_chain_df.to_dict('records')
                    aligned_records = [{col: record.get(col, None) for col in all_columns} for record in option_chain_records]
                    data_to_export.extend(aligned_records)

                    final_df_export = pd.DataFrame(data_to_export, columns=all_columns)
                    logger.info("Updating Google Sheet...")
                    update_google_sheet(gc, spreadsheet_id, final_df_export)
                else:
                    logger.warning("Merged DataFrame is empty. Check strike and expiry date formats.")
                    error_df = pd.DataFrame([{"Metric": "Error", "Value": "Merged DataFrame is empty. Check strike and expiry."}])
                    update_google_sheet(gc, spreadsheet_id, error_df)
            else:
                logger.warning("Failed to fetch data from one or both sources.")
                error_df = pd.DataFrame([{"Metric": "Error", "Value": "Failed to fetch data from one or both sources."}])
                update_google_sheet(gc, spreadsheet_id, error_df)

            time.sleep(10)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            retry_count += 1
            if retry_count >= max_retries:
                logger.error("Max retries reached. Exiting.")
                break
            time.sleep(10)
