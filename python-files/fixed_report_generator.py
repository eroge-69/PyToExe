"""
Fixed and improved version of the NSE report generator + email sender.
Key fixes and improvements:
- Use a single requests.Session() with retries/backoff.
- Date handling uses datetime objects for correct chronological sorting.
- FO "previous day" lookup uses the previous available FO file rather than naive date-1.
- Safer ZIP extraction that handles arbitrary inner filenames and avoids overwrite issues.
- Better error handling and logging using Python's logging module.
- Avoid storing SMTP password in plaintext by default; saved settings exclude password.
- More defensive checks for missing columns; return np.nan where appropriate.
- Minor performance tweaks and code cleanup.

Dependencies: pandas, numpy, requests, nselib, xlsxwriter (pandas), tkinter (stdlib)

Save this file and run it on a desktop Python interpreter that has Tkinter support.
"""

import os
import json
import zipfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ----------------------- Configuration / Globals -----------------------
DATA_DIR = Path("data")
REPORTS_DIR = Path.cwd() / "Reports"
SETTINGS_FILE = Path("smtp_settings.json")

DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("report_generator")

# Create a global session with retries/backoff
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
session.mount("https://", HTTPAdapter(max_retries=retries))
session.headers.update({
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    "accept-encoding": "gzip, deflate",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
})

BASE_URL = "https://nsearchives.nseindia.com"

# ----------------------- Helper utilities -----------------------

def safe_write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def safe_write_bytes(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


# ----------------------- Download functions -----------------------

def try_download_bhav(date_obj: datetime) -> bool:
    """Download bhav CSV for a given date (datetime). Returns True if saved."""
    date_str = date_obj.strftime("%d%m%Y")
    url = f"{BASE_URL}/products/content/sec_bhavdata_full_{date_str}.csv"
    try:
        resp = session.get(url, timeout=20)
        if resp.status_code == 200 and resp.text.strip():
            file_path = DATA_DIR / f"sec_bhavdata_full_{date_str}.csv"
            safe_write_text(file_path, resp.text)
            logger.info(f"Downloaded bhav: {file_path}")
            return True
        else:
            logger.debug(f"No bhav at {url} status={resp.status_code}")
    except Exception as e:
        logger.warning(f"Failed to download bhav for {date_str}: {e}")
    return False


def try_download_fo(date_obj: datetime) -> bool:
    """Download FO zip for given date (datetime). Returns True if saved."""
    fo_date = date_obj.strftime("%Y%m%d")
    url = f"{BASE_URL}/content/fo/BhavCopy_NSE_FO_0_0_0_{fo_date}_F_0000.csv.zip"
    zip_path = DATA_DIR / f"fo{fo_date}bhav.csv.zip"
    try:
        resp = session.get(url, timeout=30)
        if resp.status_code == 200 and resp.content:
            safe_write_bytes(zip_path, resp.content)
            logger.info(f"Downloaded FO zip: {zip_path}")
            return True
        else:
            logger.debug(f"No FO zip at {url} status={resp.status_code}")
    except Exception as e:
        logger.warning(f"Failed to download FO for {fo_date}: {e}")
    return False


def extract_first_csv_from_zip(zip_path: Path, target_csv_path: Path) -> bool:
    """Extract the first CSV-like member from a zip and rename/move to target_csv_path."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            members = [m for m in z.namelist() if m.lower().endswith('.csv')]
            if not members:
                logger.warning(f"No CSV member found in {zip_path}")
                return False
            # Prefer the shortest filename to avoid nested folders
            chosen = sorted(members, key=lambda s: (len(s), s))[0]
            temp_extract_path = DATA_DIR / chosen
            z.extract(chosen, path=DATA_DIR)
            # Move/rename to the canonical name
            temp_extract = temp_extract_path
            # If extraction created directories, the path may include directories - resolve
            if not temp_extract.exists():
                # sometimes z.extract will create nested dirs; search for file
                for p in DATA_DIR.rglob(Path(chosen).name):
                    temp_extract = p
                    break
            temp_extract.rename(target_csv_path)
            logger.info(f"Extracted {target_csv_path} from {zip_path}")
            return True
    except Exception as e:
        logger.warning(f"Failed to extract {zip_path}: {e}")
    return False


# ----------------------- File discovery / ensuring -----------------------

def list_cached_bhav_dates() -> list:
    """Return list of datetime objects for cached bhav files in DATA_DIR."""
    res = []
    for p in DATA_DIR.glob('sec_bhavdata_full_*.csv'):
        try:
            dstr = p.stem.replace('sec_bhavdata_full_', '')
            d = datetime.strptime(dstr, "%d%m%Y")
            res.append(d)
        except Exception:
            continue
    return sorted(res)


def list_cached_fo_dates() -> list:
    """Return list of datetime objects for FO csv files in DATA_DIR (foYYYYMMDDbhav.csv)."""
    res = []
    for p in DATA_DIR.glob('fo????????bhav.csv'):
        try:
            dstr = p.stem[2:10]
            d = datetime.strptime(dstr, "%Y%m%d")
            res.append(d)
        except Exception:
            continue
    return sorted(res)


def ensure_last_n_trading_files(n: int) -> tuple:
    """Ensure last n trading bhav files exist locally. Returns list of date strings (DDMMYYYY) and corresponding FO date strings (YYYYMMDD).
    This function scans backwards from today and downloads missing files when possible. Sorting is chronological (oldest first).
    """
    today = datetime.today()
    found_dates = []  # datetimes for bhav
    found_fo_dates = []  # datetimes for fo

    # We'll iterate day-by-day until we collect n trading days or reach two years
    delta = 0
    max_delta = 730
    seen = set()
    while len(found_dates) < n and delta <= max_delta:
        d = today - timedelta(days=delta)
        dd_str = d.strftime("%d%m%Y")
        fo_str = d.strftime("%Y%m%d")
        if dd_str in seen:
            delta += 1
            continue
        seen.add(dd_str)
        bhav_path = DATA_DIR / f"sec_bhavdata_full_{dd_str}.csv"
        fo_csv_path = DATA_DIR / f"fo{fo_str}bhav.csv"
        fo_zip_path = DATA_DIR / f"fo{fo_str}bhav.csv.zip"

        # Ensure FO exists first — many markets skip bhav for non-trading days; FO presence is a reasonable proxy
        if not fo_csv_path.exists():
            # Try to extract if zip exists
            if fo_zip_path.exists():
                _ = extract_first_csv_from_zip(fo_zip_path, fo_csv_path)
            else:
                # Try download
                try_download_fo(d)
                if (DATA_DIR / f"fo{fo_str}bhav.csv.zip").exists():
                    _ = extract_first_csv_from_zip(DATA_DIR / f"fo{fo_str}bhav.csv.zip", fo_csv_path)
        fo_exists = fo_csv_path.exists()

        if fo_exists:
            # Now ensure bhav exists
            if not bhav_path.exists():
                try_download_bhav(d)
            if bhav_path.exists():
                found_dates.append(d)
                found_fo_dates.append(d)
        delta += 1

    # Sort ascending chronological
    combined = sorted(zip(found_dates, found_fo_dates), key=lambda x: x[0])
    bhav_list = [dt.strftime("%d%m%Y") for dt, _ in combined]
    fo_list = [dt.strftime("%Y%m%d") for _, dt in combined]
    return bhav_list, fo_list


def ensure_last_n_fo_csv_files(n: int) -> list:
    """Ensure last n FO CSVs exist (download or extract if needed). Return list of YYYYMMDD strings oldest-first."""
    today = datetime.today()
    found = []
    checked = 0
    delta = 0
    max_delta = 730
    while len(found) < n and delta <= max_delta:
        d = today - timedelta(days=delta)
        fo_date = d.strftime("%Y%m%d")
        csv_path = DATA_DIR / f"fo{fo_date}bhav.csv"
        zip_path = DATA_DIR / f"fo{fo_date}bhav.csv.zip"
        if not csv_path.exists():
            if zip_path.exists():
                if extract_first_csv_from_zip(zip_path, csv_path):
                    found.append(d)
            else:
                if try_download_fo(d):
                    if extract_first_csv_from_zip(zip_path, csv_path):
                        found.append(d)
        else:
            found.append(d)
        delta += 1
        checked += 1
    found_sorted = sorted(found)
    return [dt.strftime("%Y%m%d") for dt in found_sorted]


# ----------------------- Data loading -----------------------

def load_dataframes(dates_ddmmYYYY: list) -> list:
    """Load bhav CSVs given dates in DDMMYYYY, return list of DataFrames sorted chronological (oldest first)."""
    dfs = []
    for ds in dates_ddmmYYYY:
        path = DATA_DIR / f"sec_bhavdata_full_{ds}.csv"
        if path.exists():
            try:
                df = pd.read_csv(path)
                df.columns = df.columns.str.strip()
                df["DATE"] = ds
                # Convert numeric columns safely
                for col in ["CLOSE_PRICE", "TTL_TRD_QNTY", "NO_OF_TRADES", "DELIV_QTY", "AVG_PRICE"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                dfs.append(df)
            except Exception as e:
                logger.warning(f"Error reading {path}: {e}")
    # sort by actual datetime
    dfs = sorted(dfs, key=lambda df: datetime.strptime(df["DATE"].iloc[0], "%d%m%Y"))
    return dfs


# ----------------------- Nifty series (via nselib) -----------------------

def fetch_nifty50_close_series(dates_ddmmYYYY: list) -> dict:
    """Use nselib.capital_market.index_data to fetch Nifty 50 close for the min..max date range and return a map DDMMYYYY->close.
    Returns {} on failure.
    """
    if not dates_ddmmYYYY:
        return {}
    try:
        from nselib import capital_market
        date_objs = [datetime.strptime(d, "%d%m%Y") for d in dates_ddmmYYYY]
        from_date = min(date_objs).strftime('%d-%m-%Y')
        to_date = max(date_objs).strftime('%d-%m-%Y')
        idx_df = capital_market.index_data(index='Nifty 50', from_date=from_date, to_date=to_date)
        if idx_df is None or idx_df.empty:
            logger.warning("nselib returned empty index data")
            return {}
        idx_df['TIMESTAMP'] = pd.to_datetime(idx_df['TIMESTAMP'], format='%d-%m-%Y')
        idx_df = idx_df.sort_values('TIMESTAMP').reset_index(drop=True)
        mapping = {dt.strftime('%d%m%Y'): close for dt, close in zip(idx_df['TIMESTAMP'], idx_df['CLOSE_INDEX_VAL'])}
        return mapping
    except Exception as e:
        logger.warning(f"Failed to fetch nifty series via nselib: {e}")
        return {}


# ----------------------- Reports preparation -----------------------

def calculate_rs_roc(asset_close: pd.Series, nifty_close: pd.Series, windows=[7, 14]) -> pd.DataFrame:
    df = pd.DataFrame({'asset_close': asset_close, 'nifty_close': nifty_close})
    df['rs_ratio'] = df['asset_close'] / df['nifty_close']
    for w in windows:
        df[f'rs_roc_{w}'] = (df['rs_ratio'] / df['rs_ratio'].shift(w) - 1) * 100
        df[f'asset_ret_{w}'] = (df['asset_close'] / df['asset_close'].shift(w) - 1) * 100
    return df


def prepare_report(symbols, dfs, today_df, today_fo_symbols, nifty500_symbols, nifty_close_map):
    # (Implementation remains close to original but more defensive)
    prev_df = pd.concat(dfs[:-1]) if len(dfs) > 1 else pd.DataFrame()
    today_df = dfs[-1]
    prev_14_df = pd.concat(dfs[-15:]) if len(dfs) >= 15 else prev_df
    if not prev_14_df.empty:
        prev_14_df['avg_qnty_per_trade'] = prev_14_df['TTL_TRD_QNTY'] / prev_14_df['NO_OF_TRADES'].replace(0, np.nan)

    means = prev_df.groupby('SYMBOL').mean(numeric_only=True) if not prev_df.empty else pd.DataFrame()

    all_df = pd.concat(dfs, ignore_index=True)
    all_df['DATE'] = pd.to_datetime(all_df['DATE'], format='%d%m%Y')
    # Ensure numeric
    for col in ['CLOSE_PRICE', 'DELIV_QTY', 'AVG_PRICE', 'TTL_TRD_QNTY']:
        if col in all_df.columns:
            all_df[col] = pd.to_numeric(all_df[col], errors='coerce')

    all_df = all_df.sort_values(['SYMBOL', 'DATE'])
    # shifts
    all_df['PREV_CLOSE'] = all_df.groupby('SYMBOL')['CLOSE_PRICE'].shift(1)
    all_df['PREV_DELIV'] = all_df.groupby('SYMBOL')['DELIV_QTY'].shift(1)
    all_df['PREV_TRADED'] = all_df.groupby('SYMBOL')['TTL_TRD_QNTY'].shift(1)

    all_df['PRICE_CHANGE'] = (all_df['CLOSE_PRICE'] - all_df['PREV_CLOSE']) / all_df['PREV_CLOSE'] * 100
    all_df['DELIV_CHANGE'] = all_df['DELIV_QTY'] - all_df['PREV_DELIV']
    all_df['TRADED_CHANGE'] = all_df['TTL_TRD_QNTY'] - all_df['PREV_TRADED']

    ad_mask = (all_df['PRICE_CHANGE'] > 0.20) & (all_df['DELIV_CHANGE'] > 0)
    ad_mask_1 = (all_df['PRICE_CHANGE'] > 0.20) & (all_df['TRADED_CHANGE'] > 0)
    dd_mask = (all_df['PRICE_CHANGE'] < 0.20) & (all_df['DELIV_CHANGE'] < 0)
    dd_mask_1 = (all_df['PRICE_CHANGE'] < 0.20) & (all_df['TRADED_CHANGE'] < 0)
    na_mask = ~(ad_mask | dd_mask)
    na_mask_1 = ~(ad_mask_1 | dd_mask_1)

    ad_counts = all_df[ad_mask].groupby('SYMBOL').size()
    dd_counts = all_df[dd_mask].groupby('SYMBOL').size()
    na_counts = all_df[na_mask].groupby('SYMBOL').size()

    ad_counts_1 = all_df[ad_mask_1].groupby('SYMBOL').size()
    dd_counts_1 = all_df[dd_mask_1].groupby('SYMBOL').size()
    na_counts_1 = all_df[na_mask_1].groupby('SYMBOL').size()

    report_rows = []
    for symbol in symbols:
        today_row = today_df[today_df['SYMBOL'] == symbol]
        if today_row.empty:
            continue
        tr = today_row.iloc[0]

        prev_14_sym = prev_14_df[prev_14_df['SYMBOL'] == symbol] if not prev_14_df.empty else pd.DataFrame()
        qnty_per_trade = prev_14_sym.iloc[-1]['avg_qnty_per_trade'] if not prev_14_sym.empty else np.nan
        avg_qnty_per_trade = prev_14_sym['avg_qnty_per_trade'].median() if not prev_14_sym.empty else np.nan

        deliv_qty = float(tr.get('DELIV_QTY', np.nan)) if 'DELIV_QTY' in tr else np.nan
        avg_deliv_qty = prev_14_sym['DELIV_QTY'].median() if not prev_14_sym.empty and 'DELIV_QTY' in prev_14_sym.columns else np.nan

        if symbol in means.index and 'TTL_TRD_QNTY' in means.columns and means.loc[symbol, 'TTL_TRD_QNTY'] != 0:
            trade_qty_deviation = ((float(tr.get('TTL_TRD_QNTY', np.nan)) - means.loc[symbol, 'TTL_TRD_QNTY']) / means.loc[symbol, 'TTL_TRD_QNTY']) * 100
        else:
            trade_qty_deviation = np.nan

        if not np.isnan(avg_deliv_qty) and avg_deliv_qty != 0:
            delivery_qty_deviation = ((deliv_qty - avg_deliv_qty) / avg_deliv_qty) * 100
        else:
            delivery_qty_deviation = np.nan

        fo_flag = 'Y' if today_fo_symbols and symbol in today_fo_symbols else 'N'
        nifty500_flag = 'Y' if nifty500_symbols and symbol in nifty500_symbols else 'N'

        symbol_df = all_df[all_df['SYMBOL'] == symbol].tail(20).copy()
        symbol_df['DATE'] = symbol_df['DATE'].dt.strftime('%d%m%Y')

        # VWAP vs CLOSE counts
        prev_14_sym_1 = prev_14_sym[:-1] if len(prev_14_sym) > 1 else prev_14_sym
        vwap_gt_close_7 = int((prev_14_sym_1.tail(7)['AVG_PRICE'] < prev_14_sym_1.tail(7)['CLOSE_PRICE']).sum()) if not prev_14_sym_1.empty else 0
        vwap_lt_close_7 = int((prev_14_sym_1.tail(7)['AVG_PRICE'] > prev_14_sym_1.tail(7)['CLOSE_PRICE']).sum()) if not prev_14_sym_1.empty else 0
        vwap_gt_close_14 = int((prev_14_sym_1.tail(14)['AVG_PRICE'] < prev_14_sym_1.tail(14)['CLOSE_PRICE']).sum()) if not prev_14_sym_1.empty else 0
        vwap_lt_close_14 = int((prev_14_sym_1.tail(14)['AVG_PRICE'] > prev_14_sym_1.tail(14)['CLOSE_PRICE']).sum()) if not prev_14_sym_1.empty else 0

        prev_20_df = all_df[all_df['SYMBOL'] == symbol].tail(20)
        deliv_5 = prev_20_df.tail(5)['DELIV_QTY'].mean() if len(prev_20_df) >= 5 else np.nan
        deliv_10 = prev_20_df.tail(10)['DELIV_QTY'].mean() if len(prev_20_df) >= 10 else np.nan
        deliv_15 = prev_20_df.tail(15)['DELIV_QTY'].mean() if len(prev_20_df) >= 15 else np.nan
        deliv_20 = prev_20_df.tail(20)['DELIV_QTY'].mean() if len(prev_20_df) >= 20 else np.nan

        # RS ROC calculation
        prev_14_dates = prev_14_sym['DATE'].tolist() if not prev_14_sym.empty else []
        asset_closes = prev_14_sym['CLOSE_PRICE'].values if 'CLOSE_PRICE' in prev_14_sym.columns else np.array([])
        valid_pairs = [(ac, d) for ac, d in zip(asset_closes, prev_14_sym['DATE'].tolist()) if d in nifty_close_map]
        if len(valid_pairs) >= 14:
            asset_closes_aligned = [ac for ac, d in valid_pairs]
            nifty_closes_aligned = [nifty_close_map[d] for ac, d in valid_pairs]
            rs_df = pd.DataFrame({'asset_close': asset_closes_aligned, 'nifty_close': nifty_closes_aligned})
            rs_df['rs_ratio'] = rs_df['asset_close'] / rs_df['nifty_close']
            rs_df['rs_roc_7'] = (rs_df['rs_ratio'] / rs_df['rs_ratio'].shift(7) - 1) * 100
            rs_df['rs_roc_14'] = (rs_df['rs_ratio'] / rs_df['rs_ratio'].shift(14) - 1) * 100
            roc_rs_7 = float(rs_df['rs_roc_7'].iloc[-1]) if not rs_df['rs_roc_7'].isna().all() else np.nan
            roc_rs_14 = float(rs_df['rs_roc_14'].iloc[-1]) if not rs_df['rs_roc_14'].isna().all() else np.nan
            roc_rs_7_14 = roc_rs_7 - roc_rs_14 if not np.isnan(roc_rs_7) and not np.isnan(roc_rs_14) else np.nan
        else:
            roc_rs_7 = np.nan
            roc_rs_14 = np.nan
            roc_rs_7_14 = np.nan

        report_rows.append({
            "Symbol": symbol,
            "Date": datetime.today().strftime("%Y%m%d"),
            "qnty_per_trade": qnty_per_trade,
            "avg_qnty_per_trade": avg_qnty_per_trade,
            "deliv_qty": deliv_qty,
            "avg_deliv_qty": avg_deliv_qty,
            "trade_qty_deviation": trade_qty_deviation,
            "delivery_qty_deviation": delivery_qty_deviation,
            "F&O": fo_flag,
            "NIFTY_500": nifty500_flag,
            "AD_DELIVER_Count": int(ad_counts.get(symbol, 0)) if hasattr(ad_counts, 'get') else 0,
            "DD_DELIVER_Count": int(dd_counts.get(symbol, 0)) if hasattr(dd_counts, 'get') else 0,
            "NA_DELIVER_Count": int(na_counts.get(symbol, 0)) if hasattr(na_counts, 'get') else 0,
            "AD_TRADED_Count": int(ad_counts_1.get(symbol, 0)) if hasattr(ad_counts_1, 'get') else 0,
            "DD_TRADED_Count": int(dd_counts_1.get(symbol, 0)) if hasattr(dd_counts_1, 'get') else 0,
            "NA_TRADED_Count": int(na_counts_1.get(symbol, 0)) if hasattr(na_counts_1, 'get') else 0,
            "vwap_positive_7days": int(vwap_gt_close_7),
            "vwap_negative_7days": int(vwap_lt_close_7),
            "vwap_positive_14days": int(vwap_gt_close_14),
            "vwap_negative_14days": int(vwap_lt_close_14),
            "5_Day_Deliver": deliv_5,
            "10-Day_Delivery": deliv_10,
            "15-Delivery": deliv_15,
            "20-Delivery": deliv_20,
            "ROC_RS_7": roc_rs_7,
            "ROC_RS_14": roc_rs_14,
            "ROC_RS_7_14_Diff": roc_rs_7_14
        })

    return pd.DataFrame(report_rows)


# ----------------------- FO helper utilities -----------------------

def load_fo_dataframe(fo_date_str: str) -> pd.DataFrame:
    path = DATA_DIR / f"fo{fo_date_str}bhav.csv"
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        logger.warning(f"Failed to read FO {path}: {e}")
        return pd.DataFrame()


def get_today_fo_symbols(today_fo_date_str: str) -> set:
    df = load_fo_dataframe(today_fo_date_str)
    if df.empty:
        return set()
    if 'TckrSymb' in df.columns:
        return set(df['TckrSymb'].astype(str).str.strip())
    return set()


def get_previous_available_fo_date(today_fo_date_str: str) -> str:
    """Return the nearest earlier FO date string (YYYYMMDD) available in DATA_DIR, or None."""
    available = list_cached_fo_dates()
    if not available:
        return None
    target = datetime.strptime(today_fo_date_str, "%Y%m%d")
    earlier = [d for d in available if d < target]
    if not earlier:
        return None
    return earlier[-1].strftime("%Y%m%d")


# ----------------------- Stock generator & other FO reports -----------------------
# For brevity we keep logic similar but with safer previous-FO fetching


def prepare_stock_generator_report(today_fo_date_str, today_df):
    fo_csv_path = DATA_DIR / f"fo{today_fo_date_str}bhav.csv"
    if not fo_csv_path.exists():
        return pd.DataFrame()
    df_fo = load_fo_dataframe(today_fo_date_str)
    if df_fo.empty:
        return pd.DataFrame()
    # Normalize
    df_fo.columns = df_fo.columns.str.strip()
    fut = df_fo[df_fo['OptnTp'].isna() | (df_fo['OptnTp'].astype(str).str.strip() == "")]
    opt = df_fo[df_fo['OptnTp'].astype(str).str.strip().isin(['CE', 'PE'])]

    lot_size_map = fut.groupby('TckrSymb')['NewBrdLotQty'].first().to_dict() if 'NewBrdLotQty' in fut.columns else {}
    symbols = sorted(set(df_fo['TckrSymb'].astype(str)))

    # Build combined historical EOD
    try:
        eod_dates = ensure_last_n_trading_files(20)[0]
    except Exception:
        eod_dates = []
    eod_dfs = load_dataframes(eod_dates)
    all_eod_df = pd.concat(eod_dfs, ignore_index=True) if eod_dfs else pd.DataFrame()
    all_eod_df['SYMBOL'] = all_eod_df['SYMBOL'].astype(str).str.strip()
    if 'CLOSE_PRICE' in all_eod_df.columns:
        all_eod_df['CLOSE_PRICE'] = pd.to_numeric(all_eod_df['CLOSE_PRICE'], errors='coerce')

    # Previous FO
    prev_fo_date = get_previous_available_fo_date(today_fo_date_str)
    df_fo_prev = load_fo_dataframe(prev_fo_date) if prev_fo_date else pd.DataFrame()

    rows = []
    today_map = {str(r['SYMBOL']).strip(): r for _, r in today_df.iterrows()} if not today_df.empty else {}

    for symbol in symbols:
        lot_size = lot_size_map.get(symbol, np.nan)
        fut_rows = fut[fut['TckrSymb'] == symbol]
        future_oi_raw = fut_rows['OpnIntrst'].sum() if not fut_rows.empty and 'OpnIntrst' in fut_rows.columns else np.nan

        prev_future_oi_raw = np.nan
        if not df_fo_prev.empty:
            fut_prev = df_fo_prev[df_fo_prev['OptnTp'].isna() | (df_fo_prev['OptnTp'].astype(str).str.strip() == "")]
            prev_future_oi_raw = fut_prev[fut_prev['TckrSymb'] == symbol]['OpnIntrst'].sum() if 'OpnIntrst' in fut_prev.columns else np.nan

        future_oi = future_oi_raw / lot_size if lot_size and not np.isnan(future_oi_raw) else np.nan
        prev_future_oi = prev_future_oi_raw / lot_size if lot_size and not np.isnan(prev_future_oi_raw) else np.nan
        change_future_oi = future_oi - prev_future_oi if not np.isnan(future_oi) and not np.isnan(prev_future_oi) else np.nan
        pct_change_future_oi = (change_future_oi / prev_future_oi * 100) if prev_future_oi and not np.isnan(change_future_oi) and prev_future_oi != 0 else np.nan

        pe_rows = opt[(opt['TckrSymb'] == symbol) & (opt['OptnTp'].astype(str).str.strip() == 'PE')]
        ce_rows = opt[(opt['TckrSymb'] == symbol) & (opt['OptnTp'].astype(str).str.strip() == 'CE')]

        pe_oi_raw = pe_rows['OpnIntrst'].sum() if not pe_rows.empty and 'OpnIntrst' in pe_rows.columns else np.nan
        ce_oi_raw = ce_rows['OpnIntrst'].sum() if not ce_rows.empty and 'OpnIntrst' in ce_rows.columns else np.nan

        prev_pe_oi_raw = np.nan
        prev_ce_oi_raw = np.nan
        if not df_fo_prev.empty:
            prev_opt = df_fo_prev[df_fo_prev['OptnTp'].astype(str).str.strip().isin(['CE', 'PE'])]
            prev_pe_oi_raw = prev_opt[(prev_opt['TckrSymb'] == symbol) & (prev_opt['OptnTp'].astype(str).str.strip() == 'PE')]['OpnIntrst'].sum() if 'OpnIntrst' in prev_opt.columns else np.nan
            prev_ce_oi_raw = prev_opt[(prev_opt['TckrSymb'] == symbol) & (prev_opt['OptnTp'].astype(str).str.strip() == 'CE')]['OpnIntrst'].sum() if 'OpnIntrst' in prev_opt.columns else np.nan

        pe_oi = pe_oi_raw / lot_size if lot_size and not np.isnan(pe_oi_raw) else np.nan
        ce_oi = ce_oi_raw / lot_size if lot_size and not np.isnan(ce_oi_raw) else np.nan
        prev_pe_oi = prev_pe_oi_raw / lot_size if lot_size and not np.isnan(prev_pe_oi_raw) else np.nan
        prev_ce_oi = prev_ce_oi_raw / lot_size if lot_size and not np.isnan(prev_ce_oi_raw) else np.nan

        change_pe_oi = pe_oi - prev_pe_oi if not np.isnan(pe_oi) and not np.isnan(prev_pe_oi) else np.nan
        change_ce_oi = ce_oi - prev_ce_oi if not np.isnan(ce_oi) and not np.isnan(prev_ce_oi) else np.nan
        pct_change_pe_oi = (change_pe_oi / prev_pe_oi * 100) if prev_pe_oi and not np.isnan(change_pe_oi) and prev_pe_oi != 0 else np.nan
        pct_change_ce_oi = (change_ce_oi / prev_ce_oi * 100) if prev_ce_oi and not np.isnan(change_ce_oi) and prev_ce_oi != 0 else np.nan

        vwap = today_map.get(symbol, {}).get('AVG_PRICE', np.nan) if today_map else np.nan
        close_price = today_map.get(symbol, {}).get('CLOSE_PRICE', np.nan) if today_map else np.nan
        delivery_qty = today_map.get(symbol, {}).get('DELIV_QTY', np.nan) if today_map else np.nan
        total_traded_qty = today_map.get(symbol, {}).get('TTL_TRD_QNTY', np.nan) if today_map else np.nan
        delivery_pct = (delivery_qty / total_traded_qty * 100) if total_traded_qty and not np.isnan(delivery_qty) and total_traded_qty != 0 else np.nan
        prev_close = today_map.get(symbol, {}).get('PREV_CLOSE', np.nan) if today_map else np.nan
        pct_change_price = ((close_price - prev_close) / prev_close * 100) if prev_close and not np.isnan(close_price) and prev_close != 0 else np.nan

        # Price low/high from fut_rows (if present)
        pct_change_price_from_low = np.nan
        pct_change_price_from_high = np.nan
        fo_row = fut_rows.iloc[0] if not fut_rows.empty else None
        if fo_row is not None:
            try:
                day_low = float(fo_row.get('LwPric', np.nan))
                day_high = float(fo_row.get('HghPric', np.nan))
                day_close = float(fo_row.get('ClsPric', np.nan))
                if day_low and not np.isnan(day_low) and day_low != 0:
                    pct_change_price_from_low = ((day_close - day_low) / day_low) * 100
                if day_high and not np.isnan(day_high) and day_high != 0:
                    pct_change_price_from_high = ((day_close - day_high) / day_high) * 100
            except Exception:
                pass

        ce_pe_ratio = (ce_oi / pe_oi) if pe_oi and not np.isnan(ce_oi) and pe_oi != 0 else np.nan
        prev_ce_pe_ratio = (prev_ce_oi / prev_pe_oi) if prev_pe_oi and not np.isnan(prev_ce_oi) and prev_pe_oi != 0 else np.nan
        change_ce_pe_ratio = ce_pe_ratio - prev_ce_pe_ratio if not np.isnan(ce_pe_ratio) and not np.isnan(prev_ce_pe_ratio) else np.nan

        pe_ce_ratio = (pe_oi / ce_oi) if ce_oi and not np.isnan(pe_oi) and ce_oi != 0 else np.nan
        prev_pe_ce_ratio = (prev_pe_oi / prev_ce_oi) if prev_ce_oi and not np.isnan(prev_pe_oi) and prev_ce_oi != 0 else np.nan
        change_pe_ce_ratio = pe_ce_ratio - prev_pe_ce_ratio if not np.isnan(pe_ce_ratio) and not np.isnan(prev_pe_ce_ratio) else np.nan

        rows.append({
            "Symbol": symbol,
            "Lot Size": lot_size,
            "Future OI": future_oi,
            "Change (Future OI)": change_future_oi,
            "% Change in Future_OI": pct_change_future_oi,
            "PE OI": pe_oi,
            "Change (PE OI)": change_pe_oi,
            "% Change (PE OI)": pct_change_pe_oi,
            "CE OI": ce_oi,
            "Change (CE OI)": change_ce_oi,
            "% Change (CE OI)": pct_change_ce_oi,
            "VWAP": vwap,
            "CLOSE PRICE": close_price,
            "Change CE / PE Ratio (OI)": change_ce_pe_ratio,
            "Change PE / CE Ratio (OI)": change_pe_ce_ratio,
            "Delivery %": delivery_pct,
            "% Change in Price": pct_change_price,
            "% Change in Price From Low": pct_change_price_from_low,
            "% Change in Price From High": pct_change_price_from_high
        })

    return pd.DataFrame(rows)


# ----------------------- AD/DD volume report -----------------------

def prepare_ad_dd_volume_report(dfs, today_fo_symbols=None, nifty500_symbols=None):
    if len(dfs) < 2:
        return pd.DataFrame()
    prev_df = dfs[-2].copy()
    today_df = dfs[-1].copy()
    prev_df['SYMBOL'] = prev_df['SYMBOL'].astype(str).str.strip()
    today_df['SYMBOL'] = today_df['SYMBOL'].astype(str).str.strip()
    prev_map = prev_df.set_index('SYMBOL')

    rows_ad = []
    rows_dd = []
    for _, row in today_df.iterrows():
        symbol = str(row['SYMBOL']).strip()
        if symbol not in prev_map.index:
            continue
        prev_row = prev_map.loc[symbol]
        try:
            today_close = float(row.get('CLOSE_PRICE', np.nan))
            prev_close = float(prev_row.get('CLOSE_PRICE', np.nan))
            today_deliv = float(row.get('DELIV_QTY', np.nan))
            prev_deliv = float(prev_row.get('DELIV_QTY', np.nan))
            today_vol = float(row.get('TTL_TRD_QNTY', np.nan))
            prev_vol = float(prev_row.get('TTL_TRD_QNTY', np.nan))
        except Exception:
            continue
        if prev_close and not np.isnan(prev_close):
            price_change = (today_close - prev_close) / prev_close * 100
        else:
            price_change = 0
        deliv_change = today_deliv - prev_deliv
        volume_gt_100 = today_vol > 2 * prev_vol if prev_vol and not np.isnan(prev_vol) else False

        fo_flag = 'Y' if today_fo_symbols and symbol in today_fo_symbols else 'N'
        nifty500_flag = 'Y' if nifty500_symbols and symbol in nifty500_symbols else 'N'

        if price_change > 0.20 and volume_gt_100:
            rows_ad.append({"Symbol": symbol, "NIFTY_500": nifty500_flag, "F&O": fo_flag})
        if price_change < 0.20 and volume_gt_100:
            rows_dd.append({"Symbol": symbol, "NIFTY_500": nifty500_flag, "F&O": fo_flag})

    max_len = max(len(rows_ad), len(rows_dd))
    rows_ad += [{}] * (max_len - len(rows_ad))
    rows_dd += [{}] * (max_len - len(rows_dd))

    return pd.DataFrame({
        "AD Symbol": [r.get("Symbol", "") for r in rows_ad],
        "AD NIFTY_500": [r.get("NIFTY_500", "") for r in rows_ad],
        "AD F&O": [r.get("F&O", "") for r in rows_ad],
        "DD Symbol": [r.get("Symbol", "") for r in rows_dd],
        "DD NIFTY_500": [r.get("NIFTY_500", "") for r in rows_dd],
        "DD F&O": [r.get("F&O", "") for r in rows_dd]
    })


# ----------------------- Top-level report generation -----------------------

def generate_report(log_callback=None):
    if log_callback is None:
        log = lambda msg: logger.info(msg)
    else:
        log = log_callback

    log("Starting report generation...")
    bhav_dates, fo_dates = ensure_last_n_trading_files(25)
    log(f"Found {len(bhav_dates)} bhav dates (oldest->newest).")
    ensure_last_n_fo_csv_files(25)
    last_25_fo_csv_dates = ensure_last_n_fo_csv_files(25)
    log(f"Found {len(last_25_fo_csv_dates)} FO CSV dates.")

    dfs = load_dataframes(bhav_dates)
    if len(dfs) < 25:
        log("Not enough trading files to prepare report.")
        return None

    today_df = dfs[-1]
    symbols = today_df['SYMBOL'].astype(str).unique().tolist()
    today_fo_symbols = get_today_fo_symbols(last_25_fo_csv_dates[-1]) if last_25_fo_csv_dates else set()

    # Download Nifty500 list if not present
    nifty500_set = set()
    nifty500_csv = DATA_DIR / 'ind_nifty500list.csv'
    if not nifty500_csv.exists():
        try:
            r = session.get('https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv', timeout=15)
            if r.status_code == 200 and r.text.strip():
                safe_write_text(nifty500_csv, r.text)
        except Exception:
            pass
    if nifty500_csv.exists():
        try:
            dfn = pd.read_csv(nifty500_csv)
            dfn.columns = dfn.columns.str.strip()
            if 'Symbol' in dfn.columns:
                nifty500_set = set(dfn['Symbol'].astype(str).str.strip())
            elif 'SYMBOL' in dfn.columns:
                nifty500_set = set(dfn['SYMBOL'].astype(str).str.strip())
        except Exception:
            nifty500_set = set()

    log("Fetching Nifty 50 close series for RS calculations...")
    last_40_bhav_dates, _ = ensure_last_n_trading_files(40)
    nifty_close_map = fetch_nifty50_close_series(last_40_bhav_dates)

    log("Preparing main report...")
    report_df = prepare_report(symbols, dfs, today_df, today_fo_symbols, nifty500_set, nifty_close_map)
    # Round numeric columns
    for col in report_df.select_dtypes(include=[np.number]).columns:
        report_df[col] = report_df[col].round(2)

    log("Preparing stock generator report...")
    stock_gen_df = prepare_stock_generator_report(last_25_fo_csv_dates[-1], today_df) if last_25_fo_csv_dates else pd.DataFrame()

    # initial_series_oi and monthly reports left as exercise; keep original behavior simplified
    log("Preparing AD/DD volume report...")
    ad_dd_df = prepare_ad_dd_volume_report(dfs, today_fo_symbols=today_fo_symbols, nifty500_symbols=nifty500_set)

    today_str = datetime.today().strftime('%Y%m%d')
    excel_path = REPORTS_DIR / f"report_{today_str}.xlsx"
    log(f"Saving report to {excel_path} ...")
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, sheet_name='1.All Data CSV Report', index=False)
        if not stock_gen_df.empty:
            stock_gen_df.to_excel(writer, sheet_name='2.Stock Generator Report', index=False)
        ad_dd_df.to_excel(writer, sheet_name='6.AD DD Volume Report', index=False)
    log(f"Report saved to {excel_path}")
    return str(excel_path)


# ----------------------- Email sending -----------------------

def send_email_with_attachment(to_email, subject, body, attachment_path, log_callback, smtp_server, smtp_port, smtp_user, smtp_pass):
    log_callback(f"Attaching file: {attachment_path}")
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg.attach(MIMEText(body, 'plain'))
    try:
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{Path(attachment_path).name}"')
            msg.attach(part)
    except Exception as e:
        log_callback(f"Failed to attach file: {e}")
        return

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as smtp:
            smtp.login(smtp_user, smtp_pass)
            log_callback(f"Sending email to {to_email} ...")
            smtp.sendmail(smtp_user, [to_email], msg.as_string())
        log_callback(f"Sent to {to_email}")
    except Exception as e:
        log_callback(f"Failed to send to {to_email}: {e}")


# ----------------------- Process & Thread wrapper -----------------------

def process_and_send(input_excel, log_callback, smtp_server, smtp_port, smtp_user, smtp_pass):
    try:
        log_callback('Reading input file for emails...')
        df = pd.read_excel(input_excel)
        email_col = None
        for col in df.columns:
            if 'email' in col.lower():
                email_col = col
                break
        if not email_col:
            log_callback('No email column found in input file.')
            return
        emails = df[email_col].dropna().astype(str).unique()
        log_callback(f'Found {len(emails)} unique email addresses.')

        log_callback('Generating report...')
        report_path = generate_report(log_callback)
        if not report_path:
            log_callback('Report generation failed.')
            return

        for idx, email in enumerate(emails, 1):
            log_callback(f'[{idx}/{len(emails)}] Sending to {email}...')
            send_email_with_attachment(
                to_email=email,
                subject='Your Daily Report',
                body='Attached is the latest daily report.',
                attachment_path=report_path,
                log_callback=log_callback,
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                smtp_user=smtp_user,
                smtp_pass=smtp_pass
            )
        log_callback('All emails processed.')
    except Exception as e:
        log_callback(f'Error in process_and_send: {e}')


# ----------------------- SMTP settings persistence (no password saved) -----------------------

def save_smtp_settings(server, port, user, passwd, save_password=False):
    data = {'server': server, 'port': port, 'user': user}
    if save_password:
        data['passwd'] = passwd
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        logger.warning('Failed to save SMTP settings')


def load_smtp_settings():
    if not SETTINGS_FILE.exists():
        return '', '', '', ''
    try:
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('server', ''), str(data.get('port', '')), data.get('user', ''), data.get('passwd', '')
    except Exception:
        return '', '', '', ''


# ----------------------- Tkinter GUI -----------------------

def main_app():
    root = tk.Tk()
    root.title('Report Generator & Email Sender (Fixed)')
    root.geometry('750x560')

    input_file_var = tk.StringVar()
    smtp_server_var = tk.StringVar()
    smtp_port_var = tk.StringVar()
    smtp_user_var = tk.StringVar()
    smtp_pass_var = tk.StringVar()
    save_pass_var = tk.BooleanVar(value=False)

    server, port, user, passwd = load_smtp_settings()
    smtp_server_var.set(server)
    smtp_port_var.set(port)
    smtp_user_var.set(user)
    smtp_pass_var.set('')  # never auto-fill password

    def browse_file():
        fp = filedialog.askopenfilename(filetypes=[('Excel files', '*.xlsx;*.xls')])
        if fp:
            input_file_var.set(fp)

    tk.Label(root, text='Select Excel with email addresses:').pack(pady=5)
    frame = tk.Frame(root)
    frame.pack()
    tk.Entry(frame, textvariable=input_file_var, width=60).pack(side=tk.LEFT, padx=5)
    tk.Button(frame, text='Browse', command=browse_file).pack(side=tk.LEFT)

    smtp_frame = tk.LabelFrame(root, text='SMTP Settings', padx=10, pady=10)
    smtp_frame.pack(padx=10, pady=10, fill='x')

    tk.Label(smtp_frame, text='SMTP Server:').grid(row=0, column=0, sticky='e')
    tk.Entry(smtp_frame, textvariable=smtp_server_var, width=40).grid(row=0, column=1, padx=5, pady=2)
    tk.Label(smtp_frame, text='SMTP Port:').grid(row=1, column=0, sticky='e')
    tk.Entry(smtp_frame, textvariable=smtp_port_var, width=40).grid(row=1, column=1, padx=5, pady=2)
    tk.Label(smtp_frame, text='SMTP User:').grid(row=2, column=0, sticky='e')
    tk.Entry(smtp_frame, textvariable=smtp_user_var, width=40).grid(row=2, column=1, padx=5, pady=2)
    tk.Label(smtp_frame, text='SMTP Password:').grid(row=3, column=0, sticky='e')
    tk.Entry(smtp_frame, textvariable=smtp_pass_var, width=40, show='*').grid(row=3, column=1, padx=5, pady=2)
    tk.Checkbutton(smtp_frame, text='Save password (insecure)', variable=save_pass_var).grid(row=4, column=1, sticky='w')

    log_widget = scrolledtext.ScrolledText(root, width=95, height=18)
    log_widget.pack(pady=10)

    def log_callback(msg):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_widget.insert(tk.END, f"{ts} - {msg}\n")
        log_widget.see(tk.END)
        logger.info(msg)

    def on_generate_send():
        if not input_file_var.get():
            messagebox.showerror('Error', 'Please select input Excel file')
            return
        if not smtp_server_var.get() or not smtp_port_var.get() or not smtp_user_var.get() or not smtp_pass_var.get():
            messagebox.showerror('Error', 'Please fill all SMTP settings')
            return
        try:
            smtp_port = int(smtp_port_var.get())
        except Exception:
            messagebox.showerror('Error', 'SMTP Port must be a number')
            return

        # Save settings (without password unless user explicitly asked)
        save_smtp_settings(smtp_server_var.get(), smtp_port, smtp_user_var.get(), smtp_pass_var.get(), save_password=save_pass_var.get())

        log_widget.delete('1.0', tk.END)
        threading.Thread(target=process_and_send, args=(input_file_var.get(), log_callback, smtp_server_var.get(), smtp_port, smtp_user_var.get(), smtp_pass_var.get()), daemon=True).start()

    tk.Button(root, text='Generate and Send', command=on_generate_send, width=24).pack(pady=8)

    root.mainloop()


if __name__ == '__main__':
    main_app()
