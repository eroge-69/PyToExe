import os
import asyncio
import json
import sys
from datetime import datetime, timezone, timedelta
from quotexapi.stable_api import Quotex
import time
import pytz
import logging
from collections import defaultdict
import time
import hashlib
import requests
from rich.console import Console
from rich.progress import Progress
from termcolor import colored
import random
import requests
from datetime import datetime, timedelta
import os
import pytz
import tempfile

def rainbow_print(text):
    colors = ['magenta', 'red']
    lines = text.strip('\n').split('\n')
    for line in lines:
        color = random.choice(colors)
        print(colored(line, color))

banner = """
╔═════════════════════════════════════════╗
║         ╔╗ ╦  ╔═╗╔═╗╦╔═                 ║
║         ╠╩╗║  ╠═╣║  ╠╩╗                 ║
║         ╚═╝╩═╝╩ ╩╚═╝╩ ╩                 ║
║     ╔╦╗╔═╗╔╦╗╔╗ ╔═╗  ═╗ ╦╔╦╗            ║
║     ║║║╠═╣║║║╠╩╗╠═╣  ╔╩╦╝ ║║            ║
║     ╩ ╩╩ ╩╩ ╩╚═╝╩ ╩  ╩ ╚══╩╝    OTC v1.0║
╠═════════════════════════════════════════╣
║        Owner: BlackSocket.t.me          ║
║        Idea: mamba_owner.t.me           ║
║        Dev: CBI403.t.me                 ║
╚═════════════════════════════════════════╝
"""

email = "ch3cooh1337@gmail.com"
password = "siamkhan"
lang = "en"
client = Quotex(email, password, lang)

async def fetch_and_save_candles(client, asset, period=60, filename=None):
    end_from_time = time.time()
    all_candles = []

    while len(all_candles) < 199:
        fetch_size = 199 - len(all_candles)
        candles = await client.get_candles(asset, end_from_time, fetch_size, period)

        if not candles:
            print(f"No more candle data available for {asset}.")
            break

        candles.reverse()
        all_candles.extend(candles)
        end_from_time = candles[0]["time"] - period

    all_candles = all_candles[:candles_need]
    dhaka_tz = timezone(timedelta(hours=6))

    if filename is None:
        filename = f"{asset}_data.json"

    json_data = []

    for candle in all_candles:
        timestamp = datetime.fromtimestamp(candle['time'], tz=timezone.utc).astimezone(dhaka_tz)
        formatted_time = timestamp.strftime('%H:%M')
        candle_open = candle["open"]
        candle_high = candle["high"]
        candle_low = candle["low"]
        candle_close = candle["close"]

        candle_type = "CALL" if candle_close > candle_open else "PUT" if candle_close < candle_open else "NEUTRAL"
        candle_range = abs(candle_open - candle_close)

        if candle_range > 0.1:
            size_category = "Big"
        elif candle_range > 0.04:
            size_category = "Medium"
        else:
            size_category = "Small"

        json_data.append({
            "time": formatted_time,
            "direction": candle_type,
            "size": size_category,
            "open": candle_open,
            "high": candle_high,
            "low": candle_low,
            "close": candle_close,
            "range": candle_range
        })

    with open(filename, "w") as file:
        json.dump(json_data, file, indent=4)

async def connect_create():
    check_connect = await client.connect()
    if not check_connect:
        attempt = 0
        while attempt <= 3:
            if not await client.check_connect():
                check_connect = await client.connect()
                if check_connect:
                    break
                else:
                    attempt += 1
            await asyncio.sleep(5)
    print("\nConnected successfully to BlackSocket Server.\n")

async def main():
    for asset in assets:
        await fetch_and_save_candles(client, asset, period=60, filename=f"{asset}_data.json")

def run_silently(func, *args, **kwargs):
    logging.disable(logging.CRITICAL)
    try:
        asyncio.run(func(*args, **kwargs))
    finally:
        logging.disable(logging.NOTSET)

async def connection_cr():
    await connect_create()

async def fetch_save():
    await main()

def calculate_bollinger_bands(closes, period=20, num_std=2):
    if len(closes) < period:
        return None, None

    # Calculate moving average without numpy
    moving_avg = sum(closes[-period:]) / period
    
    # Calculate standard deviation without numpy
    squared_diffs = [(x - moving_avg) ** 2 for x in closes[-period:]]
    variance = sum(squared_diffs) / period
    std_dev = variance ** 0.5

    upper_band = moving_avg + (num_std * std_dev)
    lower_band = moving_avg - (num_std * std_dev)

    return upper_band, lower_band

def find_patterns(file_path, asset_name):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        data.reverse()

        patterns = [("Big", "Big")]
        results = []

        closes = [c["close"] for c in data if "close" in c]

        for i in range(len(data) - 1):
            current = data[i]
            next_candle = data[i + 1]

            if current["direction"] == next_candle["direction"]:
                pair = (current["size"], next_candle["size"])
                if pair in patterns:
                    # Apply Bollinger Bands filter
                    if i + 1 >= 20:
                        recent_closes = [c["close"] for c in data[i - 18:i + 2]]
                        upper_band, lower_band = calculate_bollinger_bands(recent_closes)

                        if upper_band is None or lower_band is None:
                            continue

                        if next_candle["close"] > upper_band or next_candle["close"] < lower_band:
                            results.append({
                                "time": current["time"],
                                "direction": current["direction"],
                                "pattern": f"{pair[0]} -> {pair[1]}",
                                "asset": asset_name
                            })

        return results
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def signal_find():
    all_results = []
    for asset in assets:
        file_path = f"{asset}_data.json"
        all_results.extend(find_patterns(file_path, asset))

    all_results.sort(key=lambda x: datetime.strptime(x["time"], "%H:%M"))

    print("\nGenerated signals:\n")
    print("```")  # For Markdown-style mono block
    for result in all_results:
        adjusted_time = (datetime.strptime(result["time"], "%H:%M") + timedelta(hours=1)).strftime("%H:%M")
        adjusted_pair = result['asset'].replace("_", "-").upper()
        print(f"{adjusted_pair} $ {adjusted_time} $ {result['direction']}")
    print("```")

def delete_data_json_files_in_current_directory():
    current_dir = os.getcwd()
    for filename in os.listdir(current_dir):
        if filename.endswith('_data.json'):
            file_path = os.path.join(current_dir, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    run_silently(connection_cr)
    assets_input = input("Input asset name(s) (separate multiple assets by commas)\n==> ")
    assets = [asset.strip() for asset in assets_input.split(',')]
    candles_need = 120 
    run_silently(fetch_save)
    signal_find()
    delete_data_json_files_in_current_directory()