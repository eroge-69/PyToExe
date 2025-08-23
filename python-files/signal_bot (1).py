#!/usr/bin/env python3
"""
Realistic trading signal bot (no guarantees of accuracy).
- Fetches market data via yfinance
- Computes EMA200, RSI, MACD
- Generates example long/short signals
- Backtests with simple SL/TP/HOLD rules
- Optional: send alerts via Telegram (set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
Requirements:
    pip install pandas numpy yfinance requests
Usage:
    python signal_bot.py              # run backtest
    python signal_bot.py --live       # monitor and print/telegram alerts
    python signal_bot.py --symbol BTC-USD --interval 5m --lookback 30d
"""
import argparse
import math
import time
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict

import numpy as np
import pandas as pd
import yfinance as yf

# ---------- Default Config (can be overridden via CLI) ----------
DEFAULT_SYMBOL = "EURUSD=X"   # examples: "EURUSD=X", "BTC-USD", "AAPL"
DEFAULT_INTERVAL = "5m"       # 1m, 2m, 5m, 15m, 1h, 1d, etc.
DEFAULT_LOOKBACK = "30d"      # amount of history to fetch
ALERT_COOLDOWN_SEC = 60

# Optional Telegram (set both to enable)
TELEGRAM_BOT_TOKEN = ""      # e.g., "123456:ABC..."
TELEGRAM_CHAT_ID = ""        # your chat ID

# Strategy parameters
RSI_LEN = 14
RSI_OB = 65
RSI_OS = 35
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
EMA_TREND_LEN = 200

# Backtest parameters (toy example)
HOLD_BARS = 6       # exit after N bars
SL_PCT = 0.004      # 0.4% stop
TP_PCT = 0.006      # 0.6% take profit

# ---------- Indicator utilities ----------
def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up, index=series.index).ewm(alpha=1/length, adjust=False).mean()
    roll_down = pd.Series(down, index=series.index).ewm(alpha=1/length, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-12)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast=12, slow=26, signal=9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

# ---------- Data ----------
def fetch_history(symbol: str, interval: str, lookback: str) -> pd.DataFrame:
    df = yf.download(symbol, period=lookback, interval=interval, progress=False, auto_adjust=True)
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise RuntimeError("No data returned. Try a different symbol/interval or longer lookback.")
    df = df.rename(columns=str.capitalize)
    return df  # columns: Open, High, Low, Close, Volume

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EMA_trend"] = ema(df["Close"], EMA_TREND_LEN)
    df["RSI"] = rsi(df["Close"], RSI_LEN)
    macd_line, signal_line, hist = macd(df["Close"], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    df["MACD"] = macd_line
    df["MACDsig"] = signal_line
    df["MACDhist"] = hist
    # Trend regime (above 200 EMA = uptrend; below = downtrend)
    df["Regime"] = np.where(df["Close"] > df["EMA_trend"], 1, -1)
    return df

# ---------- Signals ----------
@dataclass
class Signal:
    time: pd.Timestamp
    side: str            # "long" or "short"
    price: float
    reason: str

def generate_signals(df: pd.DataFrame) -> List[Signal]:
    """
    Example rules:
      - Go LONG when in uptrend (price > EMA200), MACD crosses up, RSI rises from <50 to >50 and < overbought.
      - Go SHORT when in downtrend (price < EMA200), MACD crosses down, RSI falls from >50 to <50 and > oversold.
    """
    signals: List[Signal] = []
    d = df.copy()
    d["MACD_cross_up"] = (d["MACD"].shift(1) < d["MACDsig"].shift(1)) & (d["MACD"] > d["MACDsig"])
    d["MACD_cross_dn"] = (d["MACD"].shift(1) > d["MACDsig"].shift(1)) & (d["MACD"] < d["MACDsig"])
    d["RSI_up_50"] = (d["RSI"].shift(1) < 50) & (d["RSI"] >= 50) & (d["RSI"] < RSI_OB)
    d["RSI_dn_50"] = (d["RSI"].shift(1) > 50) & (d["RSI"] <= 50) & (d["RSI"] > RSI_OS)

    for idx in range(2, len(d)):
        row = d.iloc[idx]
        ts = d.index[idx]
        px = float(row["Close"])

        if row["Regime"] == 1 and row["MACD_cross_up"] and row["RSI_up_50"]:
            signals.append(Signal(time=ts, side="long", price=px, reason="Uptrend + MACD up + RSI>50"))
        elif row["Regime"] == -1 and row["MACD_cross_dn"] and row["RSI_dn_50"]:
            signals.append(Signal(time=ts, side="short", price=px, reason="Downtrend + MACD down + RSI<50"))
    return signals

# ---------- Backtest ----------
@dataclass
class TradeResult:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    side: str
    entry: float
    exit: float
    ret_pct: float
    bars_held: int
    reason: str

def backtest(df: pd.DataFrame, signals: List[Signal]) -> List[TradeResult]:
    results: List[TradeResult] = []
    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values
    times = df.index

    for sig in signals:
        try:
            entry_idx = df.index.get_loc(sig.time)
        except KeyError:
            continue
        # Enter next bar open (more realistic than same-bar fill)
        if entry_idx + 1 >= len(df):
            continue
        entry_idx += 1
        entry = float(df["Open"].iloc[entry_idx])
        side = sig.side

        tp = entry * (1 + (TP_PCT if side == "long" else -TP_PCT))
        sl = entry * (1 - (SL_PCT if side == "long" else -SL_PCT))

        exit_idx = min(entry_idx + HOLD_BARS, len(df) - 1)
        exit_px = float(closes[exit_idx])
        exit_time = times[exit_idx]
        # simulate intra-bar SL/TP hit
        for j in range(entry_idx, exit_idx + 1):
            hi, lo = highs[j], lows[j]
            if side == "long":
                if hi >= tp:
                    exit_px = tp
                    exit_time = times[j]
                    break
                if lo <= sl:
                    exit_px = sl
                    exit_time = times[j]
                    break
            else:
                if lo <= tp:  # for short, tp is lower
                    exit_px = tp
                    exit_time = times[j]
                    break
                if hi >= sl:  # for short, sl is higher
                    exit_px = sl
                    exit_time = times[j]
                    break

        ret_pct = (exit_px / entry - 1.0) * (1 if side == "long" else -1)
        results.append(TradeResult(
            entry_time=sig.time, exit_time=exit_time, side=side,
            entry=entry, exit=exit_px, ret_pct=ret_pct,
            bars_held=(exit_idx - entry_idx + 1), reason=sig.reason
        ))
    return results

def performance_summary(results: List[TradeResult]) -> Dict[str, float]:
    if not results:
        return {}
    rets = np.array([r.ret_pct for r in results])
    wins = (rets > 0).sum()
    win_rate = wins / len(rets)
    avg = rets.mean()
    std = rets.std(ddof=1) if len(rets) > 1 else 0.0
    # rough scaling for intraday; adjust per your bar size
    sharpe_like = (avg / (std + 1e-12)) * math.sqrt(252*78)
    dd = 0.0
    equity = (1 + rets).cumprod()
    peak = 1.0
    for v in equity:
        peak = max(peak, v)
        dd = min(dd, v - peak)
    return {
        "trades": float(len(rets)),
        "win_rate": float(win_rate),
        "avg_return_pct": float(avg * 100),
        "stdev_return_pct": float(std * 100),
        "max_drawdown_pct": float(dd * 100),
        "sharpe_like": float(sharpe_like),
    }

def format_summary(summary: Dict[str, float]) -> str:
    if not summary:
        return "No trades produced by the rules."
    return (
        f"Trades: {summary['trades']:.0f}\n"
        f"Win rate: {summary['win_rate']*100:.1f}%\n"
        f"Avg return: {summary['avg_return_pct']:.3f}% per trade\n"
        f"Stdev return: {summary['stdev_return_pct']:.3f}%\n"
        f"Max drawdown: {summary['max_drawdown_pct']:.2f}%\n"
        f"Sharpe-like: {summary['sharpe_like']:.2f}"
    )

# ---------- Alerts ----------
def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Alert]", message)
        return
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)
        print("[Alert Fallback]", message)

# ---------- Runners ----------
def run_backtest(symbol: str, interval: str, lookback: str):
    df = fetch_history(symbol, interval, lookback)
    df = compute_indicators(df)
    sigs = generate_signals(df)
    results = backtest(df, sigs)
    summary = performance_summary(results)
    print("=== Backtest Summary ===")
    print(format_summary(summary))
    if results:
        last = results[-5:]
        print("\nLast few trades:")
        for r in last:
            print(f"{r.entry_time} -> {r.exit_time} | {r.side.upper()} | "
                  f"entry {r.entry:.5f} exit {r.exit:.5f} | {r.ret_pct*100:+.3f}% | {r.reason}")

def monitor_live(symbol: str, interval: str, cooldown: int = ALERT_COOLDOWN_SEC):
    last_sig_time: Optional[pd.Timestamp] = None
    while True:
        try:
            df = fetch_history(symbol, interval, "2d")
            df = compute_indicators(df)
            sigs = generate_signals(df)
            if sigs:
                last_sig = sigs[-1]
                if last_sig_time is None or last_sig.time > last_sig_time:
                    msg = (f"[{symbol} {interval}] {last_sig.side.upper()} at {last_sig.price} on {last_sig.time} — "
                           f"{last_sig.reason}")
                    send_telegram(msg)
                    last_sig_time = last_sig.time
            time.sleep(max(5, cooldown))
        except KeyboardInterrupt:
            print("Stopped.")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(10)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Realistic trading signal bot (no guarantees).")
    p.add_argument("--symbol", default=DEFAULT_SYMBOL, help="Ticker/symbol (e.g., EURUSD=X, BTC-USD, AAPL)")
    p.add_argument("--interval", default=DEFAULT_INTERVAL, help="Bar interval (e.g., 1m, 5m, 15m, 1h, 1d)")
    p.add_argument("--lookback", default=DEFAULT_LOOKBACK, help="History window (e.g., 7d, 30d, 1y, max)")
    p.add_argument("--live", action="store_true", help="Run live monitor/alerts instead of backtest")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.live:
        monitor_live(args.symbol, args.interval, ALERT_COOLDOWN_SEC)
    else:
        run_backtest(args.symbol, args.interval, args.lookback)
