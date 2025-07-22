#!/usr/bin/env python3
"""
fo_automation_fixed.py

This optimized F&O automation script now reliably plays an MP3 notification
each time it completes its main Analysis task.
"""

import yaml
import requests
import pandas as pd
import telegram
import threading
import time
from pathlib import Path
from datetime import datetime, date, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from apscheduler.schedulers.blocking import BlockingScheduler
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday
from playsound import playsound

# -------------------------
# config.yaml loader
# -------------------------
CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

# -------------------------
# Holiday calendar
# -------------------------
class NSEHolidayCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday("Republic Day", month=1, day=26),
        Holiday("Independence Day", month=8, day=15),
        Holiday("Gandhi Jayanti", month=10, day=2),
        # Add other exchange holidays...
    ]

def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in pd.to_datetime(
        NSEHolidayCalendar().holidays(d, d)
    ).date

# -------------------------
# DataStore: I/O
# -------------------------
class DataStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def _folder_for_date(self, ts: datetime) -> Path:
        folder = self.base_dir / ts.strftime("%Y%m%d")
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def format_snapshot(self, symbol: str, data: list, ts: datetime) -> pd.DataFrame:
        records = []
        time_str = ts.strftime("%H:%M")
        for item in data:
            md = item["metadata"]
            ti = item["marketDeptOrderBook"]["tradeInfo"]
            records.append({
                "Name": symbol,
                "Type": md.get("instrumentType") or md.get("optionType"),
                "Strike": md.get("strikePrice", ""),
                "Expiry": md.get("expiryDate", ""),
                "OI": int(ti.get("openInterest") or 0),
                "OI_Change": int(ti.get("changeinOpenInterest") or 0),
                "LTP": float(md.get("lastPrice") or 0),
                "Cash_ltp": float(item.get("underlyingValue") or 0),
                "Vwap": float(ti.get("vmap") or 0),
                "Time": time_str,
            })
        return pd.DataFrame(records)

    def save_snapshot(self, symbol: str, df: pd.DataFrame):
        folder = self._folder_for_date(datetime.now())
        file = folder / f"{symbol}.csv"
        df.to_csv(file, mode="a", header=not file.exists(), index=False)

# -------------------------
# NSEClient: HTTP
# -------------------------
class NSEClient:
    def __init__(self, base_url, max_retries=5, backoff=0.3):
        self.session = requests.Session()
        retry = Retry(total=max_retries, backoff_factor=backoff,
                      status_forcelist=[429,500,502,503,504])
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
        })
        self.base_url = base_url

    def fetch_derivative(self, symbol: str) -> dict:
        url = f"{self.base_url}/quote-derivative?symbol={symbol}"
        resp = self.session.get(url, timeout=20)
        resp.raise_for_status()
        return resp.json()

# -------------------------
# Analyzer: computations
# -------------------------
class Analyzer:
    def __init__(self, store: DataStore, thresholds: dict):
        self.store = store
        self.th = thresholds

    def _latest_folder(self) -> Path:
        today = date.today()
        while today.weekday() >= 5 or is_holiday(today):
            today -= timedelta(days=1)
        return self.store.base_dir / today.strftime("%Y%m%d")

    def analyze_symbol(self, symbol: str) -> dict:
        folder = self._latest_folder()
        df = pd.read_csv(folder / f"{symbol}.csv")
        now = df["Time"].iloc[-1]
        df = df[df["Time"] == now]
        fut = df[df.Type.str.contains("Fut")]
        ce = df[df.Type=="CE"]
        pe = df[df.Type=="PE"]
        results = {
            "top_ce": ce.nlargest(2, "OI")[["Strike","OI"]],
            "top_pe": pe.nlargest(2, "OI")[["Strike","OI"]],
            "PCR": round(pe["OI"].sum() / ce["OI"].sum(), 2),
            "fut_pct": round(
                fut["OI_Change"].sum() /
                (fut["OI"].sum() - fut["OI_Change"].sum()) * 100, 2
            ),
            "unusual": pd.concat([
                ce[ce["OI_Change"] >= self.th["unusual_activity_pct"]/100*ce["OI"].sum()],
                pe[pe["OI_Change"] >= self.th["unusual_activity_pct"]/100*pe["OI"].sum()],
            ]),
        }
        spot = fut["Cash_ltp"].iloc[0]
        door = ce.assign(
            dist=(ce.Strike - spot)/spot*100
        ).query(
            f"dist >= {self.th['door_distance_pct']} and OI_Change*Lotsize*LTP/100000 >= {self.th['door_value_min']}"
        )
        results["door"] = door
        return results

# -------------------------
# Reporter: CSV & Telegram
# -------------------------
class Reporter:
    def __init__(self, telegram_cfg):
        self.bots = {
            role: telegram.Bot(token=token)
            for role, token in telegram_cfg["tokens"].items()
        }
        self.chats = telegram_cfg["chat_ids"]

    def to_csv(self, df: pd.DataFrame, name: str):
        df.to_csv(f"{name}.csv", index=False)

    def to_telegram(self, df: pd.DataFrame, channel: str, role="common"):
        msg = df.to_markdown()
        bot = self.bots[role]
        bot.send_message(chat_id=self.chats[channel], text=msg)

# -------------------------
# Play notification sound
# -------------------------
def play_notification():
    # Blocking call guarantees playback starts
    playsound(str(Path(__file__).parent / "Play.mp3"))

# -------------------------
# Scheduler job
# -------------------------
def job():
    client = NSEClient(cfg["nse"]["api_base"])
    store  = DataStore(Path("data"))
    analyzer = Analyzer(store, cfg["thresholds"])
    reporter = Reporter(cfg["telegram"])
    symbols = cfg["nse"]["symbols"]["indices"] + cfg["nse"]["symbols"]["watchlist"]

    # Download and save snapshots
    for sym in symbols:
        data = client.fetch_derivative(sym)["stocks"]
        df = store.format_snapshot(sym, data, datetime.now())
        store.save_snapshot(sym, df)

    # Analyze indices and report
    for idx in cfg["nse"]["symbols"]["indices"]:
        res = analyzer.analyze_symbol(idx)
        reporter.to_csv(res["top_ce"], f"{idx}_top_ce")
        reporter.to_telegram(res["top_ce"], "common")

    # Play completion sound in background thread so scheduler isn't blocked
    threading.Thread(target=play_notification, daemon=True).start()

# -------------------------
# Main entry
# -------------------------
if __name__ == "__main__":
    sched = BlockingScheduler()
    sched.add_job(
        job,
        "cron",
        minute=f"*/{cfg['schedule']['interval_minutes']}",
        hour="9-15"
    )
    sched.start()
