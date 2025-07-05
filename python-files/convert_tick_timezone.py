import os
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
from functools import partial
from zoneinfo import ZoneInfo

FIXED_HOLIDAYS = {
    "01-01", "05-01", "07-04", "12-25", "12-26"
}

TIMEZONE_OPTIONS = {
    'UTC+1': 'Etc/GMT-1', 'UTC+2': 'Etc/GMT-2', 'UTC+3': 'Etc/GMT-3', 'UTC+7': 'Etc/GMT-7',
    'UTC+8': 'Etc/GMT-8', 'UTC+9': 'Etc/GMT-9', 'UTC-5': 'Etc/GMT+5', 'UTC-4': 'Etc/GMT+4',
    'UTC-6': 'Etc/GMT+6', 'UTC-7': 'Etc/GMT+7', 'UTC-8': 'Etc/GMT+8', 'UTC+10': 'Etc/GMT-10',
    'UTC+4:30': 'Asia/Kabul', 'UTC+12': 'Etc/GMT-12', 'UTC-3': 'Etc/GMT+3',
    'UTC+2/3 with DST': 'Europe/Bucharest'
}

ROLLING_WINDOW = 500
ROLLING_ZSCORE_THRESHOLD = 3

def choose_timezone():
    print("Select a timezone for the Time column conversion:")
    for i, tz in enumerate(TIMEZONE_OPTIONS.keys()):
        print(f"{i+1}. {tz}")
    while True:
        try:
            choice = int(input("Enter the timezone number: "))
            if 1 <= choice <= len(TIMEZONE_OPTIONS):
                tz = list(TIMEZONE_OPTIONS.keys())[choice - 1]
                tz_name = TIMEZONE_OPTIONS[tz]
                print(f"Selected timezone: {tz} ({tz_name})")
                return tz_name
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def ask_remove_weekend():
    while True:
        ans = input("Remove weekend data (Saturday & Sunday)? [y/n]: ").strip().lower()
        if ans in ('y', 'yes'): return True
        elif ans in ('n', 'no'): return False
        else: print("Please answer y or n.")

def ask_remove_fixed_holiday():
    while True:
        ans = input("Remove fixed holidays (e.g. Christmas, New Year)? [y/n]: ").strip().lower()
        if ans in ('y', 'yes'): return True
        elif ans in ('n', 'no'): return False
        else: print("Please answer y or n.")

def select_folder(title="Select folder"):
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title=title)
    root.destroy()
    return folder_path

def is_holiday(date_series):
    return date_series.dt.strftime("%m-%d").isin(FIXED_HOLIDAYS)

def convert_timezone_with_zoneinfo(times_utc, target_tz_name):
    return times_utc.dt.tz_convert(ZoneInfo(target_tz_name)).dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-3]

def process_chunk(chunk, target_tz_name, remove_weekend=False, remove_fixed_holiday=False):
    if not all(c in chunk.columns for c in ['Time','Bid','Ask']):
        raise ValueError("Input CSV is missing 'Time', 'Bid' or 'Ask' columns.")
    original_columns = chunk.columns.tolist()

    times_utc = pd.to_datetime(chunk['Time'], utc=True)
    chunk['Time'] = convert_timezone_with_zoneinfo(times_utc, target_tz_name)
    dt = pd.to_datetime(chunk['Time'])

    if remove_weekend:
        mask = ~dt.dt.weekday.isin([5,6])  # Remove Saturday & Sunday
        chunk, dt = chunk[mask], dt[mask]
    if remove_fixed_holiday:
        mask = ~is_holiday(dt)
        chunk, dt = chunk[mask], dt[mask]

    chunk = chunk.drop_duplicates()
    chunk = chunk[chunk['Ask'] >= chunk['Bid']]

    chunk['Bid_mean'] = chunk['Bid'].rolling(ROLLING_WINDOW).mean()
    chunk['Bid_std'] = chunk['Bid'].rolling(ROLLING_WINDOW).std()
    chunk['Ask_mean'] = chunk['Ask'].rolling(ROLLING_WINDOW).mean()
    chunk['Ask_std'] = chunk['Ask'].rolling(ROLLING_WINDOW).std()

    chunk['Bid_z'] = (chunk['Bid'] - chunk['Bid_mean']) / chunk['Bid_std']
    chunk['Ask_z'] = (chunk['Ask'] - chunk['Ask_mean']) / chunk['Ask_std']

    chunk_filtered = chunk.iloc[ROLLING_WINDOW:].copy()
    mask = ~((chunk_filtered['Bid_z'].abs() > ROLLING_ZSCORE_THRESHOLD) | (chunk_filtered['Ask_z'].abs() > ROLLING_ZSCORE_THRESHOLD))
    chunk = pd.concat([chunk.iloc[:ROLLING_WINDOW], chunk_filtered[mask]], ignore_index=True)

    chunk = chunk.drop(columns=['Bid_mean','Bid_std','Ask_mean','Ask_std','Bid_z','Ask_z'])

    return chunk[original_columns]

def process_file(input_path, output_path, target_tz_name, remove_weekend=False, remove_fixed_holiday=False, chunksize=200_000):
    try:
        reader = pd.read_csv(input_path, chunksize=chunksize)

        worker = partial(
            process_chunk,
            target_tz_name=target_tz_name,
            remove_weekend=remove_weekend,
            remove_fixed_holiday=remove_fixed_holiday
        )

        with Pool(cpu_count()) as pool:
            results = list(tqdm(pool.imap(worker, reader), desc=f"Processing {os.path.basename(input_path)}", unit='chunk'))

        df_final = pd.concat(results).reset_index(drop=True)
        df_final.to_csv(output_path, index=False, encoding='utf-8')

        return f"✅ Done: {os.path.basename(output_path)}"
    except Exception as e:
        return f"⚠️ Failed: {os.path.basename(input_path)} → {e}"

def batch_process(input_folder, output_folder, target_tz_name, remove_weekend, remove_fixed_holiday):
    os.makedirs(output_folder, exist_ok=True)
    files = [f for f in os.listdir(input_folder) if f.lower().endswith('.csv')]
    if not files:
        print("No CSV files found in the input folder.")
        return

    for filename in files:
        input_path = os.path.join(input_folder, filename)
        suffix = f"_tz{str(target_tz_name).replace('/', '_')}"
        if remove_weekend: suffix += "_noweekend"
        if remove_fixed_holiday: suffix += "_nofixedholiday"
        suffix += "_cleaned"
        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + suffix + ".csv")

        print(f"\nProcessing file: {filename}")
        print(process_file(input_path, output_path, target_tz_name, remove_weekend, remove_fixed_holiday))

def main():
    print("=== MT5 Tick Data Cleaner with zoneinfo Timezone + Rolling Z-Score Outlier Removal ===")
    input_folder = select_folder("Select input folder containing CSV files")
    if not input_folder:
        print("No input folder selected. Exiting.")
        return
    output_folder = select_folder("Select output folder to save cleaned files")
    if not output_folder:
        print("No output folder selected. Exiting.")
        return

    target_tz_name = choose_timezone()
    remove_weekend = ask_remove_weekend()
    remove_fixed_holiday = ask_remove_fixed_holiday()

    batch_process(input_folder, output_folder, target_tz_name, remove_weekend, remove_fixed_holiday)

if __name__ == "__main__":
    main()
