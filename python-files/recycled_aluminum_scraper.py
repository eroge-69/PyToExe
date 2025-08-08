"""
Simple GUI application for fetching the latest recycled aluminium price
from the Shanghai Metals Market website and saving the data to an Excel file.

The application uses the public page for the ADC12 aluminium alloy price as
a proxy for the recycled aluminium price. When the user clicks the
“Get Latest Price” button the program fetches the page, extracts
the first price row from the table, displays it on screen and appends
the result to a local CSV/Excel archive. A second button allows the
user to export all recorded prices to an Excel file, and a third
button draws a simple trend chart using the recorded data.

This script is designed to be run with Python 3. It uses the
``requests`` library to download the web page, ``beautifulsoup4``
for HTML parsing, ``pandas`` to manage tabular data and export to
Excel, and ``matplotlib`` to plot the price trend.

If you intend to collect historical data over multiple days simply run
the program periodically; it will append new entries to the existing
archive file (``price_history.csv``) and update the trend chart.

Usage:
    python recycled_aluminum_scraper.py

"""

import datetime
import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog

import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


# Constants for the target URL and local storage
PRICE_URL = "http://hq.smm.cn/h5/ADC12-aluminum-alloy-price-chart"
# File used to accumulate daily price history in CSV format
HISTORY_FILE = "price_history.csv"


def fetch_latest_price():
    """Fetch the latest recycled aluminium price from the SMM site.

    The function downloads the ADC12 aluminium alloy price chart page,
    parses the HTML to find the first row of the price table, and
    returns the parsed result. If any step fails an exception is
    propagated upwards.

    Returns:
        dict: A dictionary with keys ``date``, ``name``, ``range``,
        ``average_price``, ``change`` and ``unit``.

    Raises:
        RuntimeError: If the page cannot be retrieved or parsed.
    """
    try:
        response = requests.get(PRICE_URL, timeout=15)
        response.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Failed to download price page: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("Price table not found on the page")

    rows = table.find_all("tr")
    # Expecting header row followed by price rows
    if len(rows) < 2:
        raise RuntimeError("Price table did not contain any data rows")

    # First data row after header holds the national average price
    first_row_cols = [c.get_text(strip=True) for c in rows[1].find_all(["th", "td"])]
    if len(first_row_cols) < 6:
        raise RuntimeError("Unexpected table structure while parsing price row")

    # Map the columns to a dict
    price_data = {
        "name": first_row_cols[0],
        "range": first_row_cols[1],
        "average_price": first_row_cols[2],
        "change": first_row_cols[3],
        "unit": first_row_cols[4],
        "date": first_row_cols[5],
    }
    return price_data


def append_price_to_history(price_info):
    """Append a price record to the CSV history file.

    If the file does not yet exist it will be created with headers.

    Args:
        price_info (dict): The price record returned by
            ``fetch_latest_price``.
    """
    df = pd.DataFrame([price_info])
    # Check if file exists to decide whether to write headers
    write_header = not os.path.isfile(HISTORY_FILE)
    df.to_csv(HISTORY_FILE, mode="a", index=False, header=write_header, encoding="utf-8-sig")


class PriceApp:
    """Tkinter-based GUI for fetching and displaying recycled aluminium prices."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Recycled Aluminium Price Fetcher")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        # Create UI elements
        self.status_label = tk.Label(root, text="Click 'Get Latest Price' to fetch today's price.")
        self.status_label.pack(pady=10)

        self.price_text = tk.StringVar()
        self.price_label = tk.Label(root, textvariable=self.price_text, font=("Arial", 12))
        self.price_label.pack(pady=10)

        self.fetch_button = tk.Button(root, text="Get Latest Price", command=self.fetch_price)
        self.fetch_button.pack(pady=5)

        self.export_button = tk.Button(root, text="Export to Excel", command=self.export_to_excel)
        self.export_button.pack(pady=5)

        self.chart_button = tk.Button(root, text="Show Trend Chart", command=self.show_trend_chart)
        self.chart_button.pack(pady=5)

    def fetch_price(self):
        """Handler for the fetch button.

        Runs the price retrieval in a background thread to avoid blocking the UI.
        """
        def task():
            try:
                self.status_label.config(text="Fetching latest price…")
                price_info = fetch_latest_price()
                # Update UI with the fetched price
                self.price_text.set(
                    f"{price_info['date']} {price_info['name']}\n"
                    f"Range: {price_info['range']}\n"
                    f"Average: {price_info['average_price']} {price_info['unit']}\n"
                    f"Change: {price_info['change']}"
                )
                self.status_label.config(text="Price fetched successfully.")
                # Append to history
                append_price_to_history(price_info)
            except Exception as exc:
                self.status_label.config(text="Failed to fetch price.")
                messagebox.showerror("Error", str(exc))

        threading.Thread(target=task, daemon=True).start()

    def export_to_excel(self):
        """Export the recorded price history to an Excel file.

        The user is prompted to choose the destination file name. The
        application reads the existing CSV history (if any) and writes
        it to an Excel file using Pandas. Any errors are shown in a
        message box.
        """
        if not os.path.isfile(HISTORY_FILE):
            messagebox.showinfo("No Data", "No price history found to export.")
            return
        # Prompt for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Excel File"
        )
        if not file_path:
            return
        try:
            df = pd.read_csv(HISTORY_FILE, encoding="utf-8-sig")
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    def show_trend_chart(self):
        """Display a simple line chart of the recorded price trend.

        Reads the history CSV file and plots the ``average_price`` versus
        ``date``. It attempts to convert the average price to numeric
        values and uses Matplotlib to create the chart. If no data
        exists a message box is displayed instead.
        """
        if not os.path.isfile(HISTORY_FILE):
            messagebox.showinfo("No Data", "No price history found to display.")
            return
        try:
            df = pd.read_csv(HISTORY_FILE, encoding="utf-8-sig")
            # Convert date strings to datetime objects
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Clean the average_price column to numeric (remove commas if any)
            df['average_price'] = pd.to_numeric(df['average_price'].astype(str).str.replace(',', ''), errors='coerce')
            df = df.dropna(subset=['date', 'average_price'])
            df = df.sort_values('date')
            if df.empty:
                raise ValueError("No valid data points to plot.")
            plt.figure(figsize=(8, 4))
            plt.plot(df['date'], df['average_price'], marker='o')
            plt.title('Recycled Aluminium Price Trend (ADC12)')
            plt.xlabel('Date')
            plt.ylabel(f"Average Price ({df['unit'].iloc[0]})" if 'unit' in df.columns else 'Average Price')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        except Exception as exc:
            messagebox.showerror("Chart Error", str(exc))


def main():
    root = tk.Tk()
    app = PriceApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()