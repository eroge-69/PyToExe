import requests
import time
import math

# --- CONFIG ---
symbol = "RELIANCE"   # Underlying stock
strike_step = 10      # Reliance options have 10 point strike gap

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain"
}

session = requests.Session()
session.headers.update(headers)

# === Warmup request to set cookies ===
session.get("https://www.nseindia.com/option-chain", timeout=5)
time.sleep(1)

# --- Functions ---
def get_last_close_equity(symbol):
    """Fetch previous close for the underlying equity"""
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    r = session.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["priceInfo"]["previousClose"]

def get_option_chain_equity(symbol):
    """Fetch option chain for equity"""
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    r = session.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def round_strike(price, step):
    return int(round(price / step) * step)

# === 1. Get previous close & ATM strike ===
last_close = get_last_close_equity(symbol)
atm_strike = round_strike(last_close, strike_step)
print(f"Previous Close: {last_close} | Rounded ATM Strike: {atm_strike}")

# === 2. Get option chain data ===
oc_data = get_option_chain_equity(symbol)
expiry = oc_data["records"]["expiryDates"][0]
print(f"Nearest expiry from NSE: {expiry}")

# === 3. Find available strikes for this expiry ===
available_strikes = sorted({item["strikePrice"] for item in oc_data["records"]["data"] if item["expiryDate"] == expiry})

# Pick closest strike in case exact ATM not available
closest_strike = min(available_strikes, key=lambda x: abs(x - atm_strike))
if closest_strike != atm_strike:
    print(f"Exact ATM {atm_strike} not found, using closest: {closest_strike}")

# === 4. Get CE & PE previous close for that strike ===
ce_price = None
pe_price = None

for rec in oc_data["records"]["data"]:
    if rec["expiryDate"] == expiry and rec["strikePrice"] == closest_strike:
        if "CE" in rec:
            ce_price = rec["CE"].get("closePrice")
        if "PE" in rec:
            pe_price = rec["PE"].get("closePrice")
        break

# === 5. Output result ===
if ce_price is not None and pe_price is not None:
    straddle_prev = ce_price + pe_price
    print(f"ATM Strike: {closest_strike}")
    print(f"Prev Day CE Close: {ce_price}, PE Close: {pe_price}")
    print(f"Prev Day Straddle: {straddle_prev}")
else:
    print("CE/PE data not found for strike!")

