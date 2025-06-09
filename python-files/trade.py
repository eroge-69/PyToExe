import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import datetime
import os
import shutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkcalendar import Calendar
from fpdf import FPDF
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# --- Database ---
DB_NAME = "trade_manager.db"
BACKUP_DIR = "backups"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        profit REAL NOT NULL,
        note TEXT,
        tag TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def add_trade(date, symbol, profit, note, tag):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO trades (date, symbol, profit, note, tag) VALUES (?,?,?,?,?)",
              (date, symbol, profit, note, tag))
    conn.commit()
    conn.close()

def update_trade(trade_id, date, symbol, profit, note, tag):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE trades SET date=?, symbol=?, profit=?, note=?, tag=? WHERE id=?",
              (date, symbol, profit, note, tag, trade_id))
    conn.commit()
    conn.close()

def get_trades(filter_symbol=None, filter_tag=None, filter_date=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query = "SELECT * FROM trades WHERE 1=1"
    params = []
    if filter_symbol:
        query += " AND symbol LIKE ?"
        params.append(f"%{filter_symbol}%")
    if filter_tag:
        query += " AND tag LIKE ?"
        params.append(f"%{filter_tag}%")
    if filter_date:
        query += " AND date = ?"
        params.append(filter_date)
    query += " ORDER BY date DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def delete_trade(trade_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM trades WHERE id=?", (trade_id,))
    conn.commit()
    conn.close()

def backup_database():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"trade_manager_{timestamp}.db")
    try:
        shutil.copy2(DB_NAME, backup_path)
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

# --- Main Application ---
class TradeManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.themes = {"Light": "flatly", "Dark": "darkly"}
        self.current_theme = get_setting("theme") or "Light"
        self.chart_type = tk.StringVar(value="Line")
        self.style = ttk.Style(theme=self.themes[self.current_theme])
        self.title("Trade Manager - Mohammad")
        self.geometry("1100x850")
        self.minsize(1000, 750)

        self.symbols_cache = set()
        self.tags_cache = set()

        # Login
        self.password = get_setting("password")
        if not self.password:
            self.set_password_initial()
        else:
            if not self.login():
                self.destroy()
                return

        self.create_widgets()
        self.load_trades()
        self.refresh_symbols_cache()
        self.draw_summary()
        self.update_dashboard()

        # Bind close event for backup
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if backup_database():
            messagebox.showinfo("Backup", "Database backup created successfully.")
        else:
            messagebox.showwarning("Backup", "Failed to create database backup.")
        self.destroy()

    def set_password_initial(self):
        while True:
            pwd1 = simpledialog.askstring("Set Password", "Enter initial password:", show='*', parent=self)
            if pwd1 is None:
                self.destroy()
                return
            pwd2 = simpledialog.askstring("Confirm Password", "Confirm password:", show='*', parent=self)
            if pwd1 == pwd2:
                set_setting("password", pwd1)
                self.password = pwd1
                messagebox.showinfo("Success", "Password set successfully.")
                break
            else:
                messagebox.showerror("Error", "Passwords do not match. Try again.")

    def login(self):
        for _ in range(3):
            pwd = simpledialog.askstring("Login", "Enter password:", show='*', parent=self)
            if pwd is None:
                return False
            if pwd == self.password:
                return True
            else:
                messagebox.showerror("Error", "Incorrect password.")
        return False

    def toggle_theme(self):
        self.current_theme = "Dark" if self.current_theme == "Light" else "Light"
        set_setting("theme", self.current_theme)
        self.style.theme_use(self.themes[self.current_theme])
        self.update_colors()

    def update_colors(self):
        bg_color = "#f8f9fa" if self.current_theme == "Light" else "#343a40"
        chart_bg = "#f8f9fa" if self.current_theme == "Light" else "#212529"
        self.configure(bg=bg_color)
        self.canvas.get_tk_widget().configure(bg=bg_color)
        self.fig.set_facecolor(chart_bg)
        self.ax.set_facecolor(chart_bg)
        self.draw_summary()

    def open_calendar(self):
        top = ttk.Toplevel(self)
        top.title("Select Date")
        top.geometry("300x250")
        top.transient(self)
        top.grab_set()

        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd", font=("Roboto", 10))
        cal.pack(pady=10, padx=10)

        def select_date():
            self.date_filter_var.set(cal.get_date())
            self.load_trades()
            top.destroy()

        ttk.Button(top, text="Select 📅", command=select_date, style="primary.TButton").pack(pady=5)
        ttk.Button(top, text="Cancel ❌", command=top.destroy, style="secondary.TButton").pack(pady=5)

    def create_widgets(self):
        # Header
        header = ttk.Frame(self, style="primary.TFrame")
        header.pack(fill='x', pady=0)
        ttk.Label(header, text="Trade Manager - Mohammad", font=("Roboto", 22, "bold"), style="primary.Inverse.TLabel").pack(side='left', padx=20, pady=15)
        ttk.Label(header, text="Instagram: @4low.t", font=("Roboto", 14), style="primary.Inverse.TLabel").pack(side='left', padx=10)
        ttk.Button(header, text="Toggle Theme ☀️", command=self.toggle_theme, style="primary.TButton").pack(side='right', padx=10)

        # Dashboard
        dashboard_frame = ttk.Frame(self, style="light.TFrame")
        dashboard_frame.pack(fill='x', pady=10, padx=10)
        self.total_trades_label = ttk.Label(dashboard_frame, text="Total Trades: 0", font=("Roboto", 12), style="info.TLabel")
        self.total_trades_label.pack(side='left', padx=20)
        self.total_profit_label = ttk.Label(dashboard_frame, text="Total Profit/Loss: 0", font=("Roboto", 12), style="success.TLabel")
        self.total_profit_label.pack(side='left', padx=20)
        self.best_trade_label = ttk.Label(dashboard_frame, text="Best Trade: 0", font=("Roboto", 12), style="warning.TLabel")
        self.best_trade_label.pack(side='left', padx=20)

        # Button Frame
        btn_frame = ttk.Frame(self, style="light.TFrame")
        btn_frame.pack(fill='x', pady=10, padx=10)
        buttons = [
            ("Add Trade ➕", self.add_trade_dialog),
            ("Edit Trade ✏️", self.edit_trade_dialog),
            ("Change Password 🔑", self.change_password),
            ("Export Excel 📊", self.export_excel),
            ("Export PDF 📄", self.export_pdf),
            ("Refresh 🔄", self.load_trades)
        ]
        for text, command in buttons:
            btn = ttk.Button(btn_frame, text=text, command=command, style="primary.TButton")
            btn.pack(side='left', padx=5)

        # Filter Frame
        filter_frame = ttk.Frame(self, style="light.TFrame")
        filter_frame.pack(fill='x', pady=10, padx=10)
        ttk.Label(filter_frame, text="Filter Symbol:", font=("Roboto", 11)).pack(side='left', padx=10)
        self.symbol_filter_var = tk.StringVar()
        self.symbol_filter_var.trace_add("write", lambda *args: self.load_trades())
        self.symbol_entry = ttk.Combobox(filter_frame, textvariable=self.symbol_filter_var, font=("Roboto", 10), style="primary.TCombobox")
        self.symbol_entry.pack(side='left', padx=5, fill='x', expand=True)

        ttk.Label(filter_frame, text="Filter Tag:", font=("Roboto", 11)).pack(side='left', padx=10)
        self.tag_filter_var = tk.StringVar()
        self.tag_filter_var.trace_add("write", lambda *args: self.load_trades())
        self.tag_entry = ttk.Combobox(filter_frame, textvariable=self.tag_filter_var, font=("Roboto", 10), style="primary.TCombobox")
        self.tag_entry.pack(side='left', padx=5, fill='x', expand=True)

        ttk.Label(filter_frame, text="Filter Date:", font=("Roboto", 11)).pack(side='left', padx=10)
        self.date_filter_var = tk.StringVar()
        self.date_filter_entry = ttk.Entry(filter_frame, textvariable=self.date_filter_var, font=("Roboto", 10), style="primary.TEntry")
        self.date_filter_entry.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(filter_frame, text="Select Date 📅", command=self.open_calendar, style="primary.TButton").pack(side='left', padx=5)

        # Chart Type Selection
        chart_frame = ttk.Frame(self, style="light.TFrame")
        chart_frame.pack(fill='x', pady=5, padx=10)
        ttk.Label(chart_frame, text="Chart Type:", font=("Roboto", 11)).pack(side='left', padx=10)
        self.chart_type_combobox = ttk.Combobox(chart_frame, textvariable=self.chart_type, values=["Line", "Bar"], font=("Roboto", 10), style="primary.TCombobox", width=10)
        self.chart_type_combobox.pack(side='left', padx=5)
        self.chart_type.trace_add("write", lambda *args: self.draw_summary())

        # Trades Table
        columns = ("id", "date", "symbol", "profit", "note", "tag")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("profit", text="Profit/Loss")
        self.tree.heading("note", text="Note")
        self.tree.heading("tag", text="Tag")
        self.tree.column("id", width=60)
        self.tree.column("date", width=100)
        self.tree.column("symbol", width=120)
        self.tree.column("profit", width=120)
        self.tree.column("note", width=350)
        self.tree.column("tag", width=120)
        self.tree.pack(expand=True, fill='both', pady=10, padx=10)
        self.tree.bind("<Delete>", self.delete_selected_trade)

        # Summary Chart
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=10, padx=10)
        self.update_colors()

    def add_trade_dialog(self):
        dlg = AddTradeDialog(self)
        self.wait_window(dlg.top)
        if dlg.result:
            date, symbol, profit, note, tag = dlg.result
            add_trade(date, symbol, profit, note, tag)
            self.refresh_symbols_cache()
            self.load_trades()
            self.draw_summary()
            self.update_dashboard()

    def edit_trade_dialog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a trade to edit.")
            return
        trade_id = self.tree.item(sel[0])["values"][0]
        trade = next((t for t in get_trades() if t[0] == trade_id), None)
        if not trade:
            return
        dlg = EditTradeDialog(self, trade)
        self.wait_window(dlg.top)
        if dlg.result:
            date, symbol, profit, note, tag = dlg.result
            update_trade(trade_id, date, symbol, profit, note, tag)
            self.refresh_symbols_cache()
            self.load_trades()
            self.draw_summary()
            self.update_dashboard()

    def refresh_symbols_cache(self):
        trades = get_trades()
        self.symbols_cache = {t[2] for t in trades}
        self.tags_cache = {t[5] for t in trades if t[5]}
        self.symbol_entry['values'] = sorted(self.symbols_cache)
        self.tag_entry['values'] = sorted(self.tags_cache)

    def load_trades(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        filter_sym = self.symbol_filter_var.get().strip()
        filter_tag = self.tag_filter_var.get().strip()
        filter_date = self.date_filter_var.get().strip()
        trades = get_trades(
            filter_sym if filter_sym else None,
            filter_tag if filter_tag else None,
            filter_date if filter_date else None
        )
        for t in trades:
            self.tree.insert('', 'end', values=t)
        self.update_dashboard()

    def delete_selected_trade(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        for item in sel:
            trade_id = self.tree.item(item)["values"][0]
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this trade?"):
                delete_trade(trade_id)
        self.load_trades()
        self.draw_summary()
        self.update_dashboard()

    def update_dashboard(self):
        trades = get_trades()
        total_trades = len(trades)
        total_profit = sum(t[3] for t in trades)
        best_trade = max((t[3] for t in trades), default=0)
        self.total_trades_label.config(text=f"Total Trades: {total_trades}")
        self.total_profit_label.config(text=f"Total Profit/Loss: ${total_profit:.2f}")
        self.best_trade_label.config(text=f"Best Trade: ${best_trade:.2f}")

    def change_password(self):
        current = simpledialog.askstring("Current Password", "Enter current password:", show='*', parent=self)
        if current != self.password:
            messagebox.showerror("Error", "Incorrect current password.")
            return
        new_pass = simpledialog.askstring("New Password", "Enter new password:", show='*', parent=self)
        if not new_pass:
            return
        confirm_pass = simpledialog.askstring("Confirm Password", "Confirm new password:", show='*', parent=self)
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New passwords do not match.")
            return
        set_setting("password", new_pass)
        self.password = new_pass
        messagebox.showinfo("Success", "Password changed successfully.")

    def draw_summary(self):
        self.ax.clear()
        trades = get_trades(self.symbol_filter_var.get().strip(), self.tag_filter_var.get().strip(), self.date_filter_var.get().strip())
        if not trades:
            self.ax.text(0.5, 0.5, "No data to display", ha='center', va='center', fontsize=14, fontfamily="Roboto")
            self.canvas.draw()
            return

        weekly_data = {}
        for t in trades:
            dt = datetime.datetime.strptime(t[1], "%Y-%m-%d")
            week_start = dt - datetime.timedelta(days=dt.weekday())
            week_label = week_start.strftime("%Y-%m-%d")
            weekly_data.setdefault(week_label, 0)
            weekly_data[week_label] += t[3]

        weeks = sorted(weekly_data.keys())
        profits = [weekly_data[w] for w in weeks]
        line_color = "#007bff" if self.current_theme == "Light" else "#17a2b8"

        if self.chart_type.get() == "Line":
            self.ax.plot(weeks, profits, marker='o', color=line_color, linewidth=2, markersize=8)
        else:  # Bar
            self.ax.bar(weeks, profits, color=line_color, alpha=0.7)

        self.ax.set_title("Weekly Profit/Loss Summary", fontfamily="Roboto", fontsize=12, color=line_color)
        self.ax.set_ylabel("Profit/Loss", fontfamily="Roboto", color=line_color)
        self.ax.set_xlabel("Week", fontfamily="Roboto", color=line_color)
        self.ax.tick_params(axis='x', rotation=45, colors=line_color)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.fig.tight_layout()
        self.canvas.draw()

    @staticmethod
    def export_excel():
        rows = get_trades()
        if not rows:
            messagebox.showinfo("Info", "No data to export.")
            return
        df = pd.DataFrame(rows, columns=["ID", "Date", "Symbol", "Profit/Loss", "Note", "Tag"])
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported to {file_path}")

    @staticmethod
    def export_pdf():
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Error", "Please install fpdf library:\npip install fpdf")
            return
        rows = get_trades()
        if not rows:
            messagebox.showinfo("Info", "No data to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("Vazirmatn", "", "Vazirmatn-Regular.ttf", uni=True)
        pdf.set_font("Vazirmatn", size=12)
        pdf.cell(0, 10, "Trade Manager Report", ln=True, align='C')
        pdf.ln(10)

        col_widths = [15, 30, 30, 30, 60, 30]
        headers = ["ID", "Date", "Symbol", "Profit/Loss", "Note", "Tag"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1)
        pdf.ln()

        for row in rows:
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 10, str(item), border=1)
            pdf.ln()

        pdf.output(file_path)
        messagebox.showinfo("Success", f"PDF exported to {file_path}")

# --- Add Trade Dialog ---
class AddTradeDialog:
    def __init__(self, parent):
        self.top = ttk.Toplevel(parent)
        self.top.title("Add New Trade")
        self.top.geometry("450x450")
        self.top.transient(parent)
        self.top.grab_set()

        ttk.Label(self.top, text="Date:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(self.top, textvariable=self.date_var, font=("Roboto", 10), style="primary.TEntry")
        self.date_entry.pack(padx=10)
        ttk.Button(self.top, text="Select Date 📅", command=self.open_calendar, style="primary.TButton").pack(pady=5)

        ttk.Label(self.top, text="Symbol:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Combobox(self.top, textvariable=self.symbol_var, font=("Roboto", 10), style="primary.TCombobox")
        self.symbol_entry['values'] = sorted(parent.symbols_cache)
        self.symbol_entry.pack(padx=10)

        ttk.Label(self.top, text="Profit (+) / Loss (-):", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.profit_var = tk.StringVar()
        self.profit_entry = ttk.Entry(self.top, textvariable=self.profit_var, font=("Roboto", 10), style="primary.TEntry")
        self.profit_entry.pack(padx=10)

        ttk.Label(self.top, text="Note:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.note_var = tk.StringVar()
        self.note_entry = ttk.Entry(self.top, textvariable=self.note_var, font=("Roboto", 10), style="primary.TEntry")
        self.note_entry.pack(padx=10)

        ttk.Label(self.top, text="Tag:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.tag_var = tk.StringVar()
        self.tag_entry = ttk.Combobox(self.top, textvariable=self.tag_var, font=("Roboto", 10), style="primary.TCombobox")
        self.tag_entry['values'] = sorted(parent.tags_cache)
        self.tag_entry.pack(padx=10)

        ttk.Button(self.top, text="Add ➕", command=self.on_add, style="primary.TButton").pack(pady=15, padx=10)
        ttk.Button(self.top, text="Cancel ❌", command=self.top.destroy, style="secondary.TButton").pack(pady=5, padx=10)

        self.result = None

    def open_calendar(self):
        top = ttk.Toplevel(self.top)
        top.title("Select Date")
        top.geometry("300x250")
        top.transient(self.top)
        top.grab_set()

        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd", font=("Roboto", 10))
        cal.pack(pady=10, padx=10)

        def select_date():
            self.date_var.set(cal.get_date())
            top.destroy()

        ttk.Button(top, text="Select 📅", command=select_date, style="primary.TButton").pack(pady=5)
        ttk.Button(top, text="Cancel ❌", command=top.destroy, style="secondary.TButton").pack(pady=5)

    def on_add(self):
        date = self.date_var.get().strip()
        symbol = self.symbol_var.get().strip()
        profit_str = self.profit_var.get().strip()
        note = self.note_var.get().strip()
        tag = self.tag_var.get().strip()

        if not date or not symbol or not profit_str:
            messagebox.showerror("Error", "Date, Symbol, and Profit/Loss are required!")
            return
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date format must be YYYY-MM-DD")
            return
        try:
            profit = float(profit_str)
        except ValueError:
            messagebox.showerror("Error", "Profit/Loss must be a number!")
            return

        self.result = (date, symbol, profit, note, tag)
        self.top.destroy()

# --- Edit Trade Dialog ---
class EditTradeDialog(AddTradeDialog):
    def __init__(self, parent, trade):
        self.top = ttk.Toplevel(parent)
        self.top.title("Edit Trade")
        self.top.geometry("450x450")
        self.top.transient(parent)
        self.top.grab_set()

        ttk.Label(self.top, text="Date:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.date_var = tk.StringVar(value=trade[1])
        self.date_entry = ttk.Entry(self.top, textvariable=self.date_var, font=("Roboto", 10), style="primary.TEntry")
        self.date_entry.pack(padx=10)
        ttk.Button(self.top, text="Select Date 📅", command=self.open_calendar, style="primary.TButton").pack(pady=5)

        ttk.Label(self.top, text="Symbol:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.symbol_var = tk.StringVar(value=trade[2])
        self.symbol_entry = ttk.Combobox(self.top, textvariable=self.symbol_var, font=("Roboto", 10), style="primary.TCombobox")
        self.symbol_entry['values'] = sorted(parent.symbols_cache)
        self.symbol_entry.pack(padx=10)

        ttk.Label(self.top, text="Profit (+) / Loss (-):", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.profit_var = tk.StringVar(value=str(trade[3]))
        self.profit_entry = ttk.Entry(self.top, textvariable=self.profit_var, font=("Roboto", 10), style="primary.TEntry")
        self.profit_entry.pack(padx=10)

        ttk.Label(self.top, text="Note:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.note_var = tk.StringVar(value=trade[4] or "")
        self.note_entry = ttk.Entry(self.top, textvariable=self.note_var, font=("Roboto", 10), style="primary.TEntry")
        self.note_entry.pack(padx=10)

        ttk.Label(self.top, text="Tag:", font=("Roboto", 11)).pack(pady=10, padx=10)
        self.tag_var = tk.StringVar(value=trade[5] or "")
        self.tag_entry = ttk.Combobox(self.top, textvariable=self.tag_var, font=("Roboto", 10), style="primary.TCombobox")
        self.tag_entry['values'] = sorted(parent.tags_cache)
        self.tag_entry.pack(padx=10)

        ttk.Button(self.top, text="Update ✅", command=self.on_add, style="primary.TButton").pack(pady=15, padx=10)
        ttk.Button(self.top, text="Cancel ❌", command=self.top.destroy, style="secondary.TButton").pack(pady=5, padx=10)

        self.result = None

if __name__ == "__main__":
    init_db()
    app = TradeManagerApp()
    app.mainloop()