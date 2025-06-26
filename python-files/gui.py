import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import tkinter as tk
from tkinter import filedialog, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ANALYST 9000")
        self.root.geometry("1000x700")

        self.file_path = "NVIDIA Stock Price History.csv"

        # Date range inputs
        tk.Label(root, text="Start Date (YYYY-MM-DD):").pack()
        self.start_date_entry = tk.Entry(root)
        self.start_date_entry.insert(0, "2009-01-01")
        self.start_date_entry.pack()

        tk.Label(root, text="End Date (YYYY-MM-DD):").pack()
        self.end_date_entry = tk.Entry(root)
        self.end_date_entry.insert(0, "2025-01-01")
        self.end_date_entry.pack()

        # Buttons
        tk.Button(root, text="Plot Stock Price", command=self.plot_price).pack(pady=5)
        tk.Button(root, text="Plot Daily % Change", command=self.plot_change).pack(pady=5)
        tk.Button(root, text="Show Raw Data", command=self.show_raw_data).pack(pady=5)
        tk.Button(root, text="Load New CSV", command=self.load_file).pack(pady=5)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.file_path = path

    def get_date_range(self):
        try:
            start = pd.to_datetime(self.start_date_entry.get(), errors='coerce')
            end = pd.to_datetime(self.end_date_entry.get(), errors='coerce')
            if pd.isnull(start) or pd.isnull(end):
                raise ValueError
            return start, end
        except:
            print("Invalid date format.")
            return None, None

    def plot_price(self):
        df = pd.read_csv(self.file_path, usecols=["Date", "Price"])
        df["Date"] = pd.to_datetime(df["Date"])
        df["Price"] = df["Price"].apply(lambda x: str(x).replace(',', '')).astype(float)

        start, end = self.get_date_range()
        if not start or not end:
            return

        df = df[(df["Date"] >= start) & (df["Date"] <= end)]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df["Date"], df["Price"], label="Price", color='blue')
        ax.set_title(" Stock Price Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")
        ax.grid(True)
        fig.tight_layout()

        self.show_plot(fig)

    def plot_change(self):
        df = pd.read_csv(self.file_path, usecols=["Date", "Change %"], dtype=str)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Change %"] = df["Change %"].apply(lambda x: str(x).replace('%', '').replace(',', '') if pd.notnull(x) else '0')
        df["Change %"] = df["Change %"].astype(float)

        start, end = self.get_date_range()
        if not start or not end:
            return

        df = df[(df["Date"] >= start) & (df["Date"] <= end)]
        df = df.sort_values("Date")

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df["Date"], df["Change %"], color='orange')
        ax.set_title(" Daily % Change")
        ax.set_xlabel("Date")
        ax.set_ylabel("Change %")
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        ax.grid(True)
        fig.tight_layout()

        self.show_plot(fig)

    def show_raw_data(self):
        try:
            df = pd.read_csv(self.file_path)
        except Exception as e:
            print("Error loading data:", e)
            return

        raw_window = tk.Toplevel(self.root)
        raw_window.title("Raw CSV Data")
        raw_window.geometry("1000x400")

        tree = ttk.Treeview(raw_window)
        tree.pack(fill=tk.BOTH, expand=True)

        # Add scrollbars
        y_scroll = ttk.Scrollbar(raw_window, orient=tk.VERTICAL, command=tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=y_scroll.set)

        x_scroll = ttk.Scrollbar(raw_window, orient=tk.HORIZONTAL, command=tree.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.configure(xscrollcommand=x_scroll.set)

        # Define columns
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for index, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

    def show_plot(self, fig):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
