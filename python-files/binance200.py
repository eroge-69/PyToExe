#!/usr/bin/env python3
# crypto_futures_ema_crossover.py

import sys
import time
import requests
import pandas as pd
from datetime import timedelta
from ta.trend import EMAIndicator

# ─── Telegram Bot Configuration ────────────────────────────────────────────────
TELEGRAM_TOKEN = "7474513929:AAF_1exWrzvKf59ORoBh1dlwOo6RWmAoiNM"
TELEGRAM_CHAT_ID = "6288279632"
# ────────────────────────────────────────────────────────────────────────────────

BINANCE_FUTURES_EXINFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
BINANCE_FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"

sent_signals = set()

def send_telegram_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": text})
        resp.raise_for_status()
    except Exception as e:
        print(f"[Telegram Error] {e}", file=sys.stderr)

def get_top_200_futures_pairs() -> list[str]:
    try:
        resp = requests.get(BINANCE_FUTURES_EXINFO, timeout=10)
        resp.raise_for_status()
        all_symbols = resp.json()["symbols"]
        usdt_pairs = [s["symbol"] for s in all_symbols if s["quoteAsset"] == "USDT" and s["contractType"] == "PERPETUAL"]
        return usdt_pairs[:200]  # Top 200 Futures USDT pairs
    except Exception as e:
        print(f"[ERROR] Could not fetch futures pairs: {e}", file=sys.stderr)
        return []

def get_klines(symbol: str, interval: str = "15m", limit: int = 100) -> pd.DataFrame:
    resp = requests.get(BINANCE_FUTURES_KLINES, params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }, timeout=10)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json(), columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms") + timedelta(hours=5)  # Pakistan Time
    return df[["timestamp", "close"]]

def check_ema_crossover(df: pd.DataFrame) -> str | None:
    ema9 = EMAIndicator(df["close"], window=9).ema_indicator()
    ema21 = EMAIndicator(df["close"], window=21).ema_indicator()
    if ema9.iloc[-2] < ema21.iloc[-2] and ema9.iloc[-1] > ema21.iloc[-1]:
        return "🔼 Bullish EMA 9/21 Crossover"
    elif ema9.iloc[-2] > ema21.iloc[-2] and ema9.iloc[-1] < ema21.iloc[-1]:
        return "🔽 Bearish EMA 9/21 Crossover"
    return None

def main():
    print("[INFO] Script started for Binance Futures Top 200 USDT pairs...")
    symbols = get_top_200_futures_pairs()

    while True:
        print(f"[INFO] Checking {len(symbols)} pairs for crossovers...")
        for symbol in symbols:
            try:
                df = get_klines(symbol)
                signal = check_ema_crossover(df)
                if signal:
                    timestamp = str(df['timestamp'].iloc[-1])
                    unique_key = f"{symbol}_{signal}_{timestamp}"
                    if unique_key not in sent_signals:
                        msg = f"{signal} detected on {symbol} at {timestamp}"
                        send_telegram_message(msg)
                        sent_signals.add(unique_key)
                        print(f"[ALERT] {msg}")
            except Exception as e:
                print(f"[ERROR] Failed on {symbol}: {e}", file=sys.stderr)

        print("[INFO] Sleeping 15 minutes...\n")
        time.sleep(900)

if __name__ == "__main__":
    main()
