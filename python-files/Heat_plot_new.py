import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from plotly.graph_objs import Scatter, Layout, Figure
import plotly.offline as py_offline
from sqlalchemy import create_engine, text

# 📦 Update your Oracle DB connection string accordingly
DATABASE_URL = "oracle+cx_oracle://rspbof:rdcis@192.183.160.13:1521/bof"  # For example: 'postgresql://user:pass@localhost/dbname'

# 🔌 Create the database engine
engine = create_engine(DATABASE_URL)

# 🎯 GUI App
class TimeSeriesPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Heat Number Time Series Plot")

        # Heat number dropdown
        tk.Label(root, text="Select Heat No:").grid(row=0, column=0, padx=10, pady=10)
        self.heat_combobox = ttk.Combobox(root, values=[], state="readonly", width=30)
        self.heat_combobox.grid(row=0, column=1)

        # Button to load latest heat numbers
        self.load_heats_button = tk.Button(root, text="Load Latest Heats", command=self.load_latest_heats)
        self.load_heats_button.grid(row=0, column=2, padx=5)

        # Item dropdown
        tk.Label(root, text="Select Item Name:").grid(row=1, column=0, padx=10, pady=10)
        self.item_combobox = ttk.Combobox(root, values=[], state="readonly", width=30)
        self.item_combobox.grid(row=1, column=1)

        # Load items button
        self.load_button = tk.Button(root, text="Load Items", command=self.load_items)
        self.load_button.grid(row=1, column=2, pady=5)

        # Plot button
        self.plot_button = tk.Button(root, text="Plot Time Series", command=self.plot_graph)
        self.plot_button.grid(row=3, column=0, columnspan=2, pady=10)

    def load_latest_heats(self):
        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT HEATNO FROM (SELECT DISTINCT HEATNO FROM ADDITIVES_CONVA) FETCH FIRST 20 ROWS ONLY
                """)
                result = conn.execute(query)
                heatnos = [row[0] for row in result]
                self.heat_combobox["values"] = heatnos
                if heatnos:
                    self.heat_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def load_items(self):
        heat_no = self.heat_combobox.get().strip()
        if not heat_no:
            messagebox.showerror("Input Error", "Please select a heat number.")
            return

        try:
            with engine.connect() as conn:
                query = text("SELECT DISTINCT ITEM_NAME FROM ADDITIVES_CONVA WHERE HEATNO = :heat_no")
                result = conn.execute(query, {"heat_no": heat_no})
                items = [row[0] for row in result]
                if not items:
                    messagebox.showinfo("No Data", "No items found for the selected heat number.")
                self.item_combobox["values"] = items
                if items:
                    self.item_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def plot_graph(self):
        heat_no = self.heat_combobox.get().strip()
        item_name = self.item_combobox.get().strip()

        if not heat_no or not item_name:
            messagebox.showerror("Input Error", "Please select both heat number and item.")
            return

        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT ENTRY_DATETIME, ITEM_VALUE 
                    FROM ADDITIVES_CONVA 
                    WHERE HEATNO = :heat_no AND ITEM_NAME = :item_name 
                    ORDER BY ENTRY_DATETIME
                """)
                df = pd.read_sql_query(query, conn, params={"heat_no": heat_no, "item_name": item_name})

            if df.empty:
                messagebox.showinfo("No Data", "No data found for the selected heat number and item.")
                return

            # Preprocessing
            df.columns = [col.upper() for col in df.columns]
            df['ENTRY_DATETIME'] = pd.to_datetime(df['ENTRY_DATETIME']).dt.tz_localize(None)
            df['ITEM_VALUE'] = pd.to_numeric(df['ITEM_VALUE'], errors='coerce')
            df = df.dropna(subset=['ITEM_VALUE'])

            if df.empty:
                messagebox.showinfo("No Valid Data", "Data has invalid or missing ITEM_VALUE entries.")
                return

            # Resample to 60s
            df.set_index('ENTRY_DATETIME', inplace=True)
            df_resampled = df['ITEM_VALUE'].resample('60s').mean().dropna().reset_index()

            if df_resampled.empty:
                messagebox.showinfo("No Data", "No data available after resampling.")
                return

            # Plot
            trace = Scatter(
                x=df_resampled['ENTRY_DATETIME'],
                y=df_resampled['ITEM_VALUE'],
                mode='lines+markers',
                hovertemplate='Time: %{x}<br>Value: %{y}<extra></extra>',
                line=dict(width=2)
            )

            layout = Layout(
                title=f"{item_name} (Heat No: {heat_no}) – Hover to See Timestamp",
                xaxis=dict(title='Timestamp'),
                yaxis=dict(title='Item Value'),
                hovermode='x unified',
                margin=dict(l=60, r=20, t=60, b=80),
                height=500
            )

            fig = Figure(data=[trace], layout=layout)
            py_offline.plot(fig, auto_open=True)

        except Exception as e:
            messagebox.showerror("Plotting Error", str(e))


# 🏁 Start the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TimeSeriesPlotterApp(root)
    root.mainloop()