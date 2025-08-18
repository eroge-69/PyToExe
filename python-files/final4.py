import requests
import time
import sqlite3
import threading
import urllib.parse
import tkinter as tk
from tkinter import ttk
from datetime import date
from statistics import mode

# ─── CONFIG ───────────────────────────────────
NSE_BASE    = "https://www.nseindia.com"
HEADERS     = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{NSE_BASE}/option-chain"
}
SYMBOLS_URL = f"{NSE_BASE}/api/equity-stockIndices?index=NIFTY%2050"
OPTION_EQ   = f"{NSE_BASE}/api/option-chain-equities?symbol="
OPTION_IDX  = f"{NSE_BASE}/api/option-chain-indices?symbol="
DB_FILE     = "straddle_history.db"
UPDATE_FREQ = 60  # seconds refresh

session = requests.Session()
session.headers.update(HEADERS)

# ─── SQLITE SETUP (thread-safe) ───────────────
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

cursor.execute("""
CREATE TABLE IF NOT EXISTS step(
    symbol TEXT PRIMARY KEY,
    step REAL,
    checked TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS straddle(
    dt TEXT,
    symbol TEXT,
    atm REAL,
    ce REAL,
    pe REAL,
    straddle REAL,
    PRIMARY KEY(dt, symbol)
)
""")
conn.commit()

# ─── HELPERS ─────────────────────────────────
def warmup():
    try:
        session.get(f"{NSE_BASE}/option-chain", timeout=5)
        time.sleep(1)
    except Exception as e:
        print("[WARN] Warmup failed:", e)

def fetch_nifty50():
    """Fetch Nifty50 symbols"""
    try:
        r = session.get(SYMBOLS_URL, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", [])
        return [x["symbol"] for x in data]
    except Exception as e:
        print("[ERROR] Fetch Nifty50 list:", e)
        return []

def fetch_option_chain(sym):
    """Get option chain JSON"""
    try:
        safe_sym = urllib.parse.quote(sym)
        url = OPTION_IDX + safe_sym if sym in ("NIFTY", "BANKNIFTY") else OPTION_EQ + safe_sym
        r = session.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "records" not in data:
            print(f"[WARN] {sym} - No 'records' in API response")
            return None
        return data
    except Exception as e:
        print(f"[ERROR] {sym} OC fetch:", e)
        return None

def fetch_underlying(sym):
    """Spot LTP"""
    try:
        url = f"{NSE_BASE}/api/quote-equity?symbol={urllib.parse.quote(sym)}"
        r = session.get(url, timeout=10)
        r.raise_for_status()
        return r.json()["priceInfo"]["lastPrice"]
    except Exception as e:
        print(f"[ERROR] {sym} LTP fetch:", e)
        return None

def get_strike_step(sym):
    """Auto detect strike step or use DB cache"""
    try:
        with db_lock:
            row = cursor.execute("SELECT step FROM step WHERE symbol=?", (sym,)).fetchone()
        if row:
            return row[0]
        oc = fetch_option_chain(sym)
        if not oc:
            return None
        expiry = oc["records"]["expiryDates"]
        strikes = sorted({
            item["strikePrice"] for item in oc["records"]["data"]
            if item.get("expiryDate") == expiry and isinstance(item.get("strikePrice"), (int, float))
        })
        if len(strikes) < 2:
            return None
        diffs = [round(strikes[i+1] - strikes[i], 4) for i in range(len(strikes)-1)]
        clean_diffs = [d for d in diffs if d > 1]
        step = mode(clean_diffs) if clean_diffs else None
        if step:
            with db_lock:
                cursor.execute(
                    "REPLACE INTO step(symbol,step,checked) VALUES(?,?,?)",
                    (sym, step, date.today().isoformat())
                )
                conn.commit()
        return step
    except Exception as e:
        print(f"[ERROR] {sym} get_strike_step:", e)
        return None

def compute_straddle(sym):
    """Calculate PrevDay straddle + PrevDay ATM + current ATM straddle + % change"""
    try:
        step = get_strike_step(sym)
        if not step:
            print(f"[WARN] Step missing for {sym}")
            return None

        spot = fetch_underlying(sym)
        if not spot:
            return None
        atm = int(round(spot / step) * step)

        oc = fetch_option_chain(sym)
        if not oc:
            return None
        expiry = oc["records"]["expiryDates"][0]

        strikes = [d["strikePrice"] for d in oc["records"]["data"] if d.get("expiryDate") == expiry]
        closest_strike = min(strikes, key=lambda x: abs(x - atm))

        ce = pe = None
        for d in oc["records"]["data"]:
            if d.get("expiryDate") == expiry and d["strikePrice"] == closest_strike:
                ce = d.get("CE", {}).get("lastPrice")
                pe = d.get("PE", {}).get("lastPrice")
                break

        if ce is None or pe is None:
            print(f"[WARN] CE/PE missing for {sym}")
            return None

        curr_straddle = ce + pe
        today = date.today().isoformat()

        with db_lock:
            # Save today's data
            cursor.execute(
                "INSERT OR IGNORE INTO straddle VALUES(?,?,?,?,?,?)",
                (today, sym, closest_strike, ce, pe, curr_straddle)
            )
            conn.commit()
            # Fetch last available day before today (with ATM and straddle)
            prev = cursor.execute(
                "SELECT atm, straddle FROM straddle WHERE dt<? AND symbol=? ORDER BY dt DESC LIMIT 1",
                (today, sym)
            ).fetchone()
        prev_atm = prev[0] if prev else 0
        prev_straddle = prev[1] if prev else 0
        pct_change = ((curr_straddle - prev_straddle) / prev_straddle * 100) if prev_straddle > 0 else 100

        return (sym, prev_straddle, prev_atm, closest_strike, ce, pe, curr_straddle, round(pct_change, 2))

    except Exception as e:
        print(f"[ERROR] {sym} compute_straddle:", e)
        return None

# ─── UI ──────────────────────────────────────
root = tk.Tk()
root.title("NIFTY50 Straddle Scanner")
root.geometry("1200x600")

# Updated columns: Added "Prev ATM" column and rearranged
cols = ("Symbol", "Prev Day", "Prev ATM", "Current ATM", "CE", "PE", "Straddle", "% Change")
tree = ttk.Treeview(root, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(fill="both", expand=True)

def refresh():
    warmup()
    symbols = fetch_nifty50()

    # Clear existing data
    for row in tree.get_children():
        tree.delete(row)

    # Collect all results first
    results = []
    for s in symbols:
        try:
            out = compute_straddle(s)
            if out:
                results.append(out)
        except Exception as e:
            print(f"[ERROR-loop] {s}:", e)
        time.sleep(0.5)  # avoid API block

    # Sort results by % change (highest first)
    results.sort(key=lambda x: x[7], reverse=True)  # Sort by % change column (index 7)

    # Insert sorted results
    for result in results:
        tree.insert("", "end", values=result)

    root.after(UPDATE_FREQ * 1000, refresh)

threading.Thread(target=refresh, daemon=True).start()
root.mainloop()

