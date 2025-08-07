# Additional features added: selectable timeframes, chart preview, Discord/webhook ready

import traceback
import tkinter.scrolledtext as scrolledtext
from tkinter import filedialog
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import io

# ... other imports remain unchanged

# Replace TIMEFRAME and SYMBOLS with dynamic lists
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
TIMEFRAMES = ['1h', '4h', '1d']

selected_timeframe = tk.StringVar(value='4h')
selected_symbols = []

# Update fetch_data to accept timeframe

def fetch_data(symbol, timeframe):
    if not ccxt:
        raise ImportError("The 'ccxt' module is required to fetch market data. Please run 'pip install ccxt'")
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Datetime'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Datetime', inplace=True)
    return df

# Update scan_market to use selected timeframe and coins

def scan_market():
    if not is_connected():
        app.after(0, lambda: messagebox.showwarning("Connection Error", "No internet connection. Check your network."))
        return

    results = []
    for symbol in selected_symbols:
        try:
            df = fetch_data(symbol, selected_timeframe.get())
            df = apply_indicators(df)
            if check_signal(df):
                msg = f"🚨 BUY Signal for {symbol} ({selected_timeframe.get()})\nDatetime: {df.index[-1]}\nPrice: {df['Close'].iloc[-1]:.2f}"
                send_telegram(msg)
                send_email(subject=f"Buy Signal for {symbol}", message=msg)
                chart_path = plot_chart(df, symbol)
                display_chart(chart_path)
                results.append({'Symbol': symbol, 'Datetime': df.index[-1], 'Price': df['Close'].iloc[-1]})
                app.after(0, lambda s=symbol, p=chart_path: messagebox.showinfo("Signal Alert", f"Buy signal for {s}!\nChart saved: {p}"))
                app.after(0, lambda m=msg: log_output(m))
        except Exception as e:
            print(traceback.format_exc())
            app.after(0, lambda s=symbol, err=e: messagebox.showerror("Error", f"Error scanning {s}: {err}"))
            app.after(0, lambda: log_output(traceback.format_exc()))

    if EXPORT_CSV and results:
        pd.DataFrame(results).to_csv("signals_export.csv", index=False)
        app.after(0, lambda: log_output("Signals exported to CSV."))

# GUI Updates
# Chart preview image panel
chart_img_panel = tk.Label(app)
chart_img_panel.pack(pady=5)

def display_chart(image_path):
    img = Image.open(image_path)
    img = img.resize((400, 250), Image.ANTIALIAS)
    img_tk = ImageTk.PhotoImage(img)
    chart_img_panel.config(image=img_tk)
    chart_img_panel.image = img_tk

# Create coin selectors
symbol_label = tk.Label(app, text="Select Coins:")
symbol_label.pack()

symbol_vars = {}
for sym in SYMBOLS:
    var = tk.BooleanVar()
    chk = tk.Checkbutton(app, text=sym, variable=var)
    chk.pack(anchor='w')
    symbol_vars[sym] = var

# Timeframe dropdown
timeframe_label = tk.Label(app, text="Select Timeframe:")
timeframe_label.pack()

timeframe_menu = ttk.Combobox(app, textvariable=selected_timeframe, values=TIMEFRAMES)
timeframe_menu.pack()

def start_scan():
    global EXPORT_CSV, selected_symbols
    EXPORT_CSV = export_var.get()
    selected_symbols = [sym for sym, v in symbol_vars.items() if v.get()]
    if not selected_symbols:
        messagebox.showwarning("No Coins Selected", "Please select at least one coin to scan.")
        return
    threading.Thread(target=scan_market).start()
