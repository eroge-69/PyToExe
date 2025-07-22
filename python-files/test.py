import requests
import csv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

session = requests.Session()
session.headers.update(HEADERS)

def get_expiry_dates(symbol):
    url = f"https://www.nseindia.com/api/option-chain-contract-info?symbol={symbol}"
    session.get("https://www.nseindia.com/option-chain")  # Set cookies via homepage visit
    r = session.get(url, headers={"Referer": "https://www.nseindia.com/option-chain"})
    data = r.json()
    return data['expiryDates']

def fetch_oc(symbol, expiry):
    url = f"https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol={symbol}&expiry={expiry}"
    r = session.get(url, headers={"Referer": "https://www.nseindia.com/option-chain"})
    return r.json()

def parse_oc_json_to_csv_rows(oc_json, expiry_date):
    data = oc_json['records']['data']
    # Combined symmetric column format
    columns = [
        "CALL OI","CALL CHNG IN OI","CALL VOLUME","CALL IV","CALL LTP","CALL CHNG",
        "CALL BID QTY", "CALL BID", "CALL ASK", "CALL ASK QTY",
        "STRIKE",
        "PUT BID QTY", "PUT BID", "PUT ASK", "PUT ASK QTY",
        "PUT CHNG","PUT LTP","PUT IV","PUT VOLUME","PUT CHNG IN OI","PUT OI"
    ]
    rows = []
    for record in data:
        strike = record.get("strikePrice")
        ce = record.get("CE", {})
        pe = record.get("PE", {})
        row = {
            "CALL OI": ce.get("openInterest", ""),
            "CALL CHNG IN OI": ce.get("changeinOpenInterest", ""),
            "CALL VOLUME": ce.get("totalTradedVolume", ""),
            "CALL IV": ce.get("impliedVolatility", ""),
            "CALL LTP": ce.get("lastPrice", ""),
            "CALL CHNG": ce.get("change", ""),
            "CALL BID QTY": ce.get("buyQuantity1", ""),
            "CALL BID": ce.get("buyPrice1", ""),
            "CALL ASK": ce.get("sellPrice1", ""),
            "CALL ASK QTY": ce.get("sellQuantity1", ""),
            "STRIKE": strike,
            "PUT BID QTY": pe.get("buyQuantity1", ""),
            "PUT BID": pe.get("buyPrice1", ""),
            "PUT ASK": pe.get("sellPrice1", ""),
            "PUT ASK QTY": pe.get("sellQuantity1", ""),
            "PUT CHNG": pe.get("change", ""),
            "PUT LTP": pe.get("lastPrice", ""),
            "PUT IV": pe.get("impliedVolatility", ""),
            "PUT VOLUME": pe.get("totalTradedVolume", ""),
            "PUT CHNG IN OI": pe.get("changeinOpenInterest", ""),
            "PUT OI": pe.get("openInterest", ""),
        }
        rows.append(row)
    return columns, rows

def save_to_csv(columns, rows, outfilename):
    with open(outfilename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Saved {outfilename}")

#### --- Main logic ---

# NIFTY
nifty_expiries = get_expiry_dates("NIFTY")[:2]
for expiry in nifty_expiries:
    oc_json = fetch_oc("NIFTY", expiry)
    columns, rows = parse_oc_json_to_csv_rows(oc_json, expiry)
    save_to_csv(columns, rows, f"nifty_{expiry}.csv")

# BANKNIFTY
banknifty_expiry = get_expiry_dates("BANKNIFTY")[0]
oc_json = fetch_oc("BANKNIFTY", banknifty_expiry)
columns, rows = parse_oc_json_to_csv_rows(oc_json, banknifty_expiry)
save_to_csv(columns, rows, f"banknifty_{banknifty_expiry}.csv")
