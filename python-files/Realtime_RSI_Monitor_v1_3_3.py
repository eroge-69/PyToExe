#!/usr/bin/env python3
# Realtime_RSI_Monitor_v1_3_3.py
# Hotfix over v1.3.2:
# - Fixed SyntaxError (unmatched ')' in buttons row)
# - All features identical to v1.3.2 (status chip near Source, centered Help, etc.)

import threading, time, sys, json, queue
from datetime import datetime, timezone

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

_have_mplfinance = True
try:
    import mplfinance as mpf
except Exception:
    _have_mplfinance = False

try:
    import winsound; _can_beep = True
except Exception:
    _can_beep = False

try:
    import yfinance as yf; _have_yf = True
except Exception:
    _have_yf = False

try:
    import requests; _have_requests = True
except Exception:
    _have_requests = False

try:
    import websocket; _have_ws = True
except Exception:
    _have_ws = False


APP_VERSION = "v1.3.3"
APP_BANNER = f"Realtime RSI Monitor {APP_VERSION} — by Ronald"
APP_NAME = APP_BANNER
POLL_SECONDS_DEFAULT = 12
RSI_LENGTH_DEFAULT = 14
INTERVALS = ["1m", "2m", "3m", "5m", "15m", "30m", "60m"]
SOURCES = ["Auto", "Yahoo", "Binance", "Binance (WS)"]

# ---------- Core calc ----------
def compute_rsi(close: pd.Series, length: int = RSI_LENGTH_DEFAULT) -> pd.Series:
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0.0)
    loss = (-delta.where(delta < 0, 0)).fillna(0.0)
    avg_gain = gain.ewm(alpha=1/length, min_periods=length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/length, min_periods=length, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0.0)

def detect_crosses(rsi: pd.Series, low_th: float, high_th: float):
    if len(rsi) < 2: return [], []
    prev = rsi.shift(1)
    cross_up = list(rsi[(prev <= low_th) & (rsi > low_th)].index)
    cross_dn = list(rsi[(prev >= high_th) & (rsi < high_th)].index)
    return cross_up, cross_dn

def _flatten_ohlcv(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["Open","High","Low","Close","Volume"])
    if isinstance(df.columns, pd.MultiIndex):
        lvl0 = df.columns.get_level_values(0)
        if len(lvl0) and (ticker in set(lvl0)):
            try: df = df[ticker]
            except Exception: pass
        else:
            try: df.columns = [c[-1] if isinstance(c, tuple) else c for c in df.columns]
            except Exception: pass
    for c in ["Open","High","Low","Close","Volume"]:
        if c not in df.columns: df[c] = np.nan
    return df[["Open","High","Low","Close","Volume"]]

def yahoo_download(ticker: str, interval: str) -> pd.DataFrame:
    if not _have_yf: return pd.DataFrame()
    period_candidates = {
        "1m":["2d","5d","7d"], "2m":["5d","7d","30d"], "3m":["5d","7d","30d"],
        "5m":["7d","30d","60d"], "15m":["30d","60d"], "30m":["60d"], "60m":["60d"]
    }
    for period in period_candidates.get(interval, ["7d"]):
        try:
            df = yf.download(ticker, period=period, interval=interval if interval!="3m" else "5m",
                             progress=False, auto_adjust=False, threads=False, group_by="column", prepost=True)
            df = _flatten_ohlcv(df, ticker).dropna(subset=["Close"])
            if not df.empty:
                if df.index.tz is None: df.index = df.index.tz_localize(timezone.utc)
                return df
        except Exception: continue
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="7d", interval=interval if interval!="3m" else "5m", auto_adjust=False, prepost=True)
        if isinstance(df, pd.DataFrame) and not df.empty:
            df = _flatten_ohlcv(df, ticker).dropna(subset=["Close"])
            if not df.empty:
                if df.index.tz is None: df.index = df.index.tz_localize(timezone.utc)
                return df
    except Exception: pass
    return pd.DataFrame()

_BINANCE_INTERVAL_MAP = {"1m":"1m","2m":"1m","3m":"3m","5m":"5m","15m":"15m","30m":"30m","60m":"1h"}

def _to_binance_symbol(ticker: str) -> str:
    t = ticker.upper().replace("-", "")
    if t.endswith("USD") and not t.endswith("USDT"): return t + "T"
    return t

def binance_download(ticker: str, interval: str, limit: int = 1000) -> pd.DataFrame:
    if not _have_requests: return pd.DataFrame()
    symbol = _to_binance_symbol(ticker)
    bint = _BINANCE_INTERVAL_MAP.get(interval, "1m")
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": bint, "limit": min(limit, 1000)}
    try:
        r = requests.get(url, params=params, timeout=10); r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data)==0: return pd.DataFrame()
        cols = ["Open time","Open","High","Low","Close","Volume","Close time","Quote asset volume","Trades","Taker buy base","Taker buy quote","Ignore"]
        df = pd.DataFrame(data, columns=cols)
        for c in ["Open","High","Low","Close","Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["Open time"] = pd.to_datetime(df["Open time"], unit="ms", utc=True)
        df = df.rename(columns={"Open time":"Date"}).set_index("Date")
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        if interval=="2m":
            df = df.resample("2T").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
        return df
    except Exception:
        return pd.DataFrame()

def looks_like_crypto(ticker: str) -> bool:
    t = ticker.upper()
    return any(s in t for s in ["BTC","ETH","SOL","ADA","USDT","USD"]) and "." not in t

# ---------- Workers ----------
class DataWorkerREST(threading.Thread):
    def __init__(self, ticker, interval, source, poll_seconds, out_queue):
        super().__init__(daemon=True)
        self.ticker, self.interval, self.source = ticker, interval, source
        self.poll_seconds = max(5, int(poll_seconds))
        self.out_queue = out_queue
        self._stop = threading.Event()
    def stop(self): self._stop.set()
    def fetch_once(self):
        if self.source=="Yahoo": return yahoo_download(self.ticker, self.interval)
        if self.source=="Binance": return binance_download(self.ticker, self.interval)
        df = yahoo_download(self.ticker, self.interval)
        if df is not None and not df.empty: return df
        if looks_like_crypto(self.ticker): return binance_download(self.ticker, self.interval)
        return pd.DataFrame()
    def run(self):
        last_idx_hash=None
        while not self._stop.is_set():
            try:
                df = self.fetch_once()
                if df is not None and not df.empty:
                    idx_hash = (df.index[-1], float(df["Close"].iloc[-1]))
                    if idx_hash != last_idx_hash:
                        self.out_queue.put(pd.DataFrame({"__status__":[f"REST_OK|{time.time()}"]}))
                        self.out_queue.put(df); last_idx_hash = idx_hash
                else:
                    src=self.source
                    if src=="Auto" and looks_like_crypto(self.ticker): src="Auto(Yahoo→Binance)"
                    self.out_queue.put(pd.DataFrame({"__error__":[f"No data from {src} for {self.ticker} {self.interval}."]}))
            except Exception as e:
                self.out_queue.put(pd.DataFrame({"__error__":[f"{type(e).__name__}: {e}"]}))
            for _ in range(self.poll_seconds):
                if self._stop.is_set(): break
                time.sleep(1)

class DataWorkerWS(threading.Thread):
    def __init__(self, ticker, interval, out_queue):
        super().__init__(daemon=True)
        self.ticker, self.interval = ticker, interval
        self.symbol = _to_binance_symbol(ticker).upper()
        self.out_queue = out_queue
        self._stop = threading.Event()
        self.ws = None
        self.df = pd.DataFrame()
    def stop(self):
        self._stop.set()
        try:
            if self.ws: self.ws.close()
        except Exception: pass
    def _on_message(self, ws, message):
        try:
            msg = json.loads(message); 
            if "k" not in msg: return
            k = msg["k"]; t_open = pd.to_datetime(k["t"], unit="ms", utc=True)
            self.df.loc[t_open, ["Open","High","Low","Close","Volume"]] = [float(k["o"]), float(k["h"]), float(k["l"]), float(k["c"]), float(k["v"])]
            self.out_queue.put(pd.DataFrame({"__status__":[f"WS_OK|{time.time()}"]}))
            if self.interval=="2m":
                send_df = self.df.sort_index().resample("2T").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
            else:
                send_df = self.df.sort_index()
            self.out_queue.put(send_df.tail(1000))
        except Exception as e:
            self.out_queue.put(pd.DataFrame({"__error__":[f"WS parse error: {e}"]}))
    def _on_error(self, ws, error):
        self.out_queue.put(pd.DataFrame({"__error__":[f"WS error: {error}"]}))
    def _on_close(self, ws, status_code, msg):
        if not self._stop.is_set():
            for i in range(3,0,-1):
                self.out_queue.put(pd.DataFrame({"__status__":[f"WS_RECONNECT|{i}"]}))
                time.sleep(1)
            threading.Thread(target=self._run_ws, daemon=True).start()
    def _on_open(self, ws):
        self.out_queue.put(pd.DataFrame({"__status__":[f"WS_OPEN|{time.time()}"]}))
    def _run_ws(self):
        stream_interval = _BINANCE_INTERVAL_MAP.get(self.interval, "1m")
        stream = f"{self.symbol.lower()}@kline_{stream_interval}"
        url = f"wss://stream.binance.com:9443/ws/{stream}"
        self.ws = websocket.WebSocketApp(url, on_message=self._on_message, on_error=self._on_error, on_close=self._on_close, on_open=self._on_open)
        self.ws.run_forever(ping_interval=15, ping_timeout=10, reconnect=5)
    def run(self):
        self.df = binance_download(self.ticker, self.interval, limit=720)
        if self.df is not None and not self.df.empty: self.out_queue.put(self.df.copy())
        if not _have_ws:
            self.out_queue.put(pd.DataFrame({"__error__":["websocket-client not installed. pip install websocket-client"]})); return
        self._run_ws()

# ---------- App ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME); self.geometry("1420x980")

        # menu + F1
        menubar = tk.Menu(self)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Open Help (F1)", command=self.show_help, accelerator="F1")
        helpmenu.add_separator()
        helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", APP_BANNER))
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)
        self.bind("<F1>", lambda e: self.show_help())

        self._worker = None
        self._queue = queue.Queue()
        self._df = pd.DataFrame()
        self._signals = []  # (ts, type, price, rsi)
        self._highlight_ts = None  # selection highlight

        # status
        self._mode = "IDLE"
        self._last_update_ts = 0.0
        self._ws_reconnect_countdown = None

        # hover
        self._hover_items = []
        self._hover_after_id = None
        self._hover_target = None
        self._hover_annot = None
        self._hover_radius_px = 18  # hit radius

        # --- Controls: two rows ---
        top = ttk.Frame(self); top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10,0))
        # buttons row
        btnrow = ttk.Frame(top); btnrow.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(btnrow, text="Start", command=self.start_worker).pack(side=tk.LEFT, padx=(0,6))
        ttk.Button(btnrow, text="Stop", command=self.stop_worker).pack(side=tk.LEFT, padx=6)
        ttk.Button(btnrow, text="Save PNG", command=self.save_png).pack(side=tk.LEFT, padx=6)
        ttk.Button(btnrow, text="Save CSV", command=self.save_csv).pack(side=tk.LEFT, padx=6)
        ttk.Button(btnrow, text="Help", command=self.show_help).pack(side=tk.LEFT, padx=6)

        # settings row
        setrow = ttk.Frame(top); setrow.pack(side=tk.TOP, fill=tk.X, pady=(8,0))
        ttk.Label(setrow, text="Ticker:").pack(side=tk.LEFT)
        self.var_ticker = tk.StringVar(value="BTC-USD")
        ttk.Entry(setrow, textvariable=self.var_ticker, width=15).pack(side=tk.LEFT, padx=(5,10))

        ttk.Label(setrow, text="Interval:").pack(side=tk.LEFT)
        self.var_interval = tk.StringVar(value="1m")
        ttk.Combobox(setrow, textvariable=self.var_interval, values=INTERVALS, width=6, state="readonly").pack(side=tk.LEFT, padx=(5,10))

        ttk.Label(setrow, text="Source:").pack(side=tk.LEFT)
        self.var_source = tk.StringVar(value="Binance (WS)")
        ttk.Combobox(setrow, textvariable=self.var_source, values=SOURCES, width=12, state="readonly").pack(side=tk.LEFT, padx=(5,6))

        # status chip next to Source
        self.lbl_chip_led = ttk.Label(setrow, text="●", width=2); self.lbl_chip_led.pack(side=tk.LEFT)
        self.lbl_chip_text = ttk.Label(setrow, text="Idle"); self.lbl_chip_text.pack(side=tk.LEFT, padx=(2,12))

        ttk.Label(setrow, text="RSI length:").pack(side=tk.LEFT)
        self.var_rsi_len = tk.StringVar(value=str(RSI_LENGTH_DEFAULT))
        ttk.Entry(setrow, textvariable=self.var_rsi_len, width=5).pack(side=tk.LEFT, padx=(5,10))

        ttk.Label(setrow, text="Lower:").pack(side=tk.LEFT)
        self.var_low = tk.StringVar(value="30")
        ttk.Entry(setrow, textvariable=self.var_low, width=4).pack(side=tk.LEFT, padx=(3,8))

        ttk.Label(setrow, text="Upper:").pack(side=tk.LEFT)
        self.var_high = tk.StringVar(value="70")
        ttk.Entry(setrow, textvariable=self.var_high, width=4).pack(side=tk.LEFT, padx=(3,8))

        ttk.Label(setrow, text="Poll s:").pack(side=tk.LEFT)
        self.var_poll = tk.StringVar(value=str(POLL_SECONDS_DEFAULT))
        ttk.Entry(setrow, textvariable=self.var_poll, width=5).pack(side=tk.LEFT, padx=(5,10))

        self.var_confirm = tk.BooleanVar(value=True)
        ttk.Checkbutton(setrow, text="Confirm on close", variable=self.var_confirm).pack(side=tk.LEFT, padx=(5,10))

        self.var_beep = tk.BooleanVar(value=True)
        ttk.Checkbutton(setrow, text="Beep on signal", variable=self.var_beep).pack(side=tk.LEFT, padx=(5,10))

        # --- Content area ---
        content = ttk.Frame(self); content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Signals (right) with scrollbar
        side = ttk.Frame(content); side.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Label(side, text="Signals").pack(anchor="w")
        side_list_frame = ttk.Frame(side); side_list_frame.pack(fill=tk.Y, expand=True)
        self.listbox = tk.Listbox(side_list_frame, width=68)
        vsb = ttk.Scrollbar(side_list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=vsb.set)
        self.listbox.grid(row=0, column=0, sticky="ns")
        vsb.grid(row=0, column=1, sticky="ns")
        side_list_frame.rowconfigure(0, weight=1)
        self.listbox.bind("<<ListboxSelect>>", self._on_signal_select)

        # Plot (left)
        plot_frame = ttk.Frame(content); plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(13.9, 7.2), dpi=100)
        self.ax_price = self.fig.add_subplot(2,1,1)
        self.ax_rsi = self.fig.add_subplot(2,1,2, sharex=self.ax_price)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("figure_leave_event", self._on_leave)

        # periodic chip update
        self.after(1000, self._update_status_chip)
        self.after(250, self._poll_queue)

    # ----- File ops -----
    def save_png(self):
        try:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"RSI_{self.var_ticker.get()}_{self.var_interval.get()}_{now}.png"
            self.fig.savefig(fname, bbox_inches="tight")
            messagebox.showinfo(APP_NAME, f"Saved: {fname}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to save: {e}")

    def save_csv(self):
        if not self._signals:
            messagebox.showinfo(APP_NAME, "No signals yet."); return
        try:
            df = pd.DataFrame(self._signals, columns=["timestamp","type","price","rsi"])
            df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(str)
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile=f"signals_{self.var_ticker.get()}_{self.var_interval.get()}.csv")
            if path:
                df.to_csv(path, index=False); messagebox.showinfo(APP_NAME, f"Saved: {path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to save CSV: {e}")

    # ----- Worker control -----
    def start_worker(self):
        if getattr(self, "_worker", None) is not None:
            messagebox.showinfo(APP_NAME, "Already running."); return
        ticker = self.var_ticker.get().strip()
        if not ticker: messagebox.showwarning(APP_NAME, "Please enter a ticker."); return
        try:
            int(self.var_rsi_len.get()); int(self.var_poll.get()); float(self.var_low.get()); float(self.var_high.get())
        except Exception:
            messagebox.showwarning(APP_NAME, "RSI length, thresholds and Poll seconds must be numeric."); return

        self._signals.clear(); self.listbox.delete(0, tk.END); self._df = pd.DataFrame()
        src = self.var_source.get()
        if src == "Binance (WS)":
            self._worker = DataWorkerWS(ticker, self.var_interval.get(), self._queue)
            self._mode = "WS"
        else:
            self._worker = DataWorkerREST(ticker, self.var_interval.get(), src, int(self.var_poll.get()), self._queue)
            self._mode = "REST"
        self._worker.start()
        self.title(f"{APP_BANNER} — {ticker} [{self.var_interval.get()}] via {src}")
        self._last_update_ts = 0.0

    def stop_worker(self):
        if self._worker:
            try: self._worker.stop()
            except Exception: pass
            self._worker = None
        self._mode = "IDLE"

    # ----- Queue polling & status -----
    def _poll_queue(self):
        try:
            while True:
                df = self._queue.get_nowait()
                if "__status__" in df.columns:
                    msg = str(df["__status__"].iloc[0])
                    if msg.startswith("WS_OK") or msg.startswith("REST_OK") or msg.startswith("WS_OPEN"):
                        self._last_update_ts = time.time()
                        self._ws_reconnect_countdown = None
                    elif msg.startswith("WS_RECONNECT"):
                        try: self._ws_reconnect_countdown = int(msg.split("|")[1])
                        except Exception: self._ws_reconnect_countdown = None
                    continue
                if "__error__" in df.columns:
                    self.status_message(df["__error__"].iloc[0]); continue
                self._df = df; self._last_update_ts = time.time()
                self.redraw()
        except queue.Empty:
            pass
        self.after(500, self._poll_queue)

    def _update_status_chip(self):
        now = time.time(); age = now - self._last_update_ts if self._last_update_ts else None
        if self._mode == "IDLE":
            color, text = "#888", "Idle"
        elif age is None:
            color, text = "#e67e22", f"{self._mode} …"
        else:
            if age < 5: color = "#2ecc71"
            elif age < 15: color = "#f1c40f"
            else: color = "#e74c3c"
            text = f"{self._mode} {int(age)}s"
            if self._ws_reconnect_countdown is not None:
                text += f" | retry {self._ws_reconnect_countdown}s"
        self.lbl_chip_led.configure(foreground=color)
        self.lbl_chip_text.configure(text=text)
        self.after(1000, self._update_status_chip)

    def status_message(self, msg: str):
        try: self.listbox.insert(0, msg)
        except Exception: pass

    # ----- Hover helpers -----
    def _cancel_hover_timer(self):
        if self._hover_after_id is not None:
            try: self.after_cancel(self._hover_after_id)
            except Exception: pass
            self._hover_after_id = None

    def _hide_annot(self):
        if self._hover_annot is not None:
            self._hover_annot.remove()
            self._hover_annot = None
            self.canvas.draw_idle()

    def _on_leave(self, event):
        self._cancel_hover_timer(); self._hide_annot(); self._hover_target = None

    def _on_motion(self, event):
        if event.inaxes not in (self.ax_price, self.ax_rsi):
            self._cancel_hover_timer(); self._hide_annot(); self._hover_target=None; return
        ex, ey = event.x, event.y
        nearest = None; best = 1e9
        for item in self._hover_items:
            if item["ax"] is not event.inaxes: continue
            dx, dy = item["ax"].transData.transform((item["x"], item["y"]))
            d = ((dx-ex)**2 + (dy-ey)**2)**0.5
            if d < best:
                best = d; nearest = item
        if nearest and best < self._hover_radius_px:
            if self._hover_target is not nearest:
                self._hover_target = nearest
                self._cancel_hover_timer()
                self._hover_after_id = self.after(800, self._show_tooltip)
        else:
            self._hover_target = None
            self._cancel_hover_timer()
            self._hide_annot()

    def _show_tooltip(self):
        if not self._hover_target: return
        item = self._hover_target
        text = item["text"]; ax = item["ax"]
        self._hide_annot()
        self._hover_annot = ax.annotate(text, xy=(item["x"], item["y"]), xytext=(12, 12),
                                        textcoords="offset points", bbox=dict(boxstyle="round", fc="w", alpha=0.93),
                                        arrowprops=dict(arrowstyle="->", alpha=0.6))
        self.canvas.draw_idle()

    # ----- List selection highlight -----
    def _on_signal_select(self, event):
        sel = self.listbox.curselection()
        if not sel: self._highlight_ts=None; self.redraw(); return
        text = self.listbox.get(sel[0])
        ts_str = text.split(" — ", 1)[0].replace(" UTC", "")
        try:
            ts = pd.to_datetime(ts_str, utc=True)
            self._highlight_ts = ts; self.redraw()
        except Exception:
            self._highlight_ts = None

    # ----- Drawing -----
    def _draw_price(self, df: pd.DataFrame, signals_up, signals_dn):
        self.ax_price.clear()
        self.ax_price.set_title(self.var_ticker.get().strip()); self.ax_price.set_ylabel("Price")
        if df.empty:
            self.ax_price.text(0.5,0.5,"No data", ha="center", va="center", transform=self.ax_price.transAxes); return
        max_bars=300
        df_plot = df.iloc[-max_bars:].copy() if len(df)>max_bars else df.copy()
        if _have_mplfinance:
            mpf.plot(df_plot, type="candle", ax=self.ax_price, volume=False, show_nontrading=True,
                     datetime_format="%H:%M\n%d-%b", xrotation=0)
        else:
            self.ax_price.plot(df_plot.index, df_plot["Close"], linewidth=1.2)
        for win in (20,50):
            if len(df_plot) >= win:
                ma = df_plot["Close"].rolling(win).mean()
                self.ax_price.plot(df_plot.index, ma, linewidth=1.0, alpha=0.9, label=f"MA{win}")
        self.ax_price.legend(loc="upper left", fontsize=8)
        self.ax_price.grid(True, which="both", linestyle="--", alpha=0.2)

        idxset = set(df_plot.index)
        up_x = [t for t in signals_up if t in idxset]
        dn_x = [t for t in signals_dn if t in idxset]
        up_y = [df_plot.loc[t, "Close"] for t in up_x]
        dn_y = [df_plot.loc[t, "Close"] for t in dn_x]
        self.ax_price.scatter(up_x, up_y, marker="^", s=60)
        self.ax_price.scatter(dn_x, dn_y, marker="v", s=60)

        if self._highlight_ts is not None and self._highlight_ts in df_plot.index:
            y = df_plot.loc[self._highlight_ts, "Close"]
            self.ax_price.axvline(self._highlight_ts, linestyle="--", linewidth=1.0, alpha=0.7)
            self.ax_price.scatter([self._highlight_ts], [y], marker="o", s=140)

        # register hover points (price)
        self._hover_items = [it for it in self._hover_items if it["ax"] is not self.ax_price]
        for t,y in zip(up_x, up_y):
            label = f"▲ LONG\n{t.strftime('%Y-%m-%d %H:%M UTC')}\nPrice: {y:.4f}"
            self._hover_items.append({"ax": self.ax_price, "x": t, "y": y, "text": label})
        for t,y in zip(dn_x, dn_y):
            label = f"▼ EXIT/SHORT\n{t.strftime('%Y-%m-%d %H:%M UTC')}\nPrice: {y:.4f}"
            self._hover_items.append({"ax": self.ax_price, "x": t, "y": y, "text": label})

    def _draw_rsi(self, df: pd.DataFrame):
        self.ax_rsi.clear()
        if df.empty:
            self.ax_rsi.text(0.5,0.5,"No data", ha="center", va="center", transform=self.ax_rsi.transAxes); return [], []
        close = df["Close"]
        try:
            rsi_len = max(2, int(self.var_rsi_len.get())); low=float(self.var_low.get()); high=float(self.var_high.get())
        except Exception:
            rsi_len = RSI_LENGTH_DEFAULT; low, high = 30.0, 70.0
        rsi = compute_rsi(close, length=rsi_len)
        rsi_for_signals = rsi.iloc[:-1] if self.var_confirm.get() and len(rsi)>1 else rsi

        self.ax_rsi.plot(rsi.index, rsi, linewidth=1.2)
        self.ax_rsi.axhline(high, linestyle="--", linewidth=0.9)
        self.ax_rsi.axhline(low, linestyle="--", linewidth=0.9)
        self.ax_rsi.set_ylim(0,100)
        self.ax_rsi.fill_between(rsi.index, high, 100, alpha=0.08)
        self.ax_rsi.fill_between(rsi.index, 0, low, alpha=0.08)

        cross_up, cross_dn = detect_crosses(rsi_for_signals, low, high)

        # update signal store & log
        new_signals=[]
        for ts in cross_up:
            price = float(df.loc[ts,"Close"]) if ts in df.index else float(close.iloc[-1])
            val = float(rsi.loc[ts]) if ts in rsi.index else float(rsi.iloc[-1])
            new_signals.append((ts,"RSI_UP",price,val))
        for ts in cross_dn:
            price = float(df.loc[ts,"Close"]) if ts in df.index else float(close.iloc[-1])
            val = float(rsi.loc[ts]) if ts in rsi.index else float(rsi.iloc[-1])
            new_signals.append((ts,"RSI_DN",price,val))
        existing={(s[0],s[1]) for s in self._signals}
        for s in new_signals:
            if (s[0],s[1]) not in existing:
                self._signals.append(s)
                ts_str = pd.to_datetime(s[0]).strftime("%Y-%m-%d %H:%M:%S %Z")
                direction = "▲ LONG" if s[1]=="RSI_UP" else "▼ EXIT/SHORT"
                self.listbox.insert(0, f"{ts_str} — {direction} @ {s[2]:.4f} (RSI {s[3]:.1f})")
                if self.var_beep.get() and _can_beep:
                    try: winsound.Beep(880 if s[1]=='RSI_UP' else 440, 180)
                    except Exception: pass

        # draw markers in RSI
        up_x = [t for t in cross_up if t in rsi.index]
        dn_x = [t for t in cross_dn if t in rsi.index]
        up_y = [rsi.loc[t] for t in up_x]
        dn_y = [rsi.loc[t] for t in dn_x]
        self.ax_rsi.scatter(up_x, up_y, marker="^", s=60)
        self.ax_rsi.scatter(dn_x, dn_y, marker="v", s=60)

        if self._highlight_ts is not None and self._highlight_ts in rsi.index:
            y = rsi.loc[self._highlight_ts]
            self.ax_rsi.axvline(self._highlight_ts, linestyle="--", linewidth=1.0, alpha=0.7)
            self.ax_rsi.scatter([self._highlight_ts], [y], marker="o", s=140)

        self.ax_rsi.set_ylabel(f"RSI({rsi_len})")

        # register hover points (rsi)
        self._hover_items = [it for it in self._hover_items if it["ax"] is not self.ax_rsi]
        for t,y in zip(up_x, up_y):
            label = f"▲ LONG\n{t.strftime('%Y-%m-%d %H:%M UTC')}\nRSI: {y:.1f}"
            self._hover_items.append({"ax": self.ax_rsi, "x": t, "y": y, "text": label})
        for t,y in zip(dn_x, dn_y):
            label = f"▼ EXIT/SHORT\n{t.strftime('%Y-%m-%d %H:%M UTC')}\nRSI: {y:.1f}"
            self._hover_items.append({"ax": self.ax_rsi, "x": t, "y": y, "text": label})

        return up_x + dn_x, up_x + dn_x

    def redraw(self):
        df = self._df
        if df is None or df.empty: return
        max_bars=800
        df = df.iloc[-max_bars:].copy() if len(df)>max_bars else df
        signals_up, signals_dn = self._draw_rsi(df)
        self._draw_price(df, signals_up, signals_dn)
        self.fig.tight_layout(); self.canvas.draw_idle()

    # ----- Help window (centered) -----
    def _add_help_tab(self, nb: ttk.Notebook, title: str, content: str):
        frame = ttk.Frame(nb); nb.add(frame, text=title)
        txt = tk.Text(frame, wrap="word"); vsb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=vsb.set); txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6); vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.insert("1.0", content); txt.configure(state="disabled"); return frame

    def show_help(self):
        w, h = 920, 660
        self.update_idletasks()
        px, py = self.winfo_rootx(), self.winfo_rooty()
        pw, ph = self.winfo_width(), self.winfo_height()
        x = int(px + (pw - w) / 2); y = int(py + (ph - h) / 2)

        help_win = tk.Toplevel(self); help_win.title("Help & Guide — Realtime RSI Monitor")
        help_win.geometry(f"{w}x{h}+{x}+{y}")
        nb = ttk.Notebook(help_win); nb.pack(fill=tk.BOTH, expand=True)

        overview = ("Overview\n-------\nRealtime RSI Monitor shows price + RSI with configurable bands and signals.\n"
                    "Sources: Yahoo, Binance (REST), Binance (WS live). Upper: price + MA20/50. Lower: RSI.\n")
        signals = ("Signals\n-------\n• ▲ Green = RSI crosses UP through Lower → potential LONG.\n• ▼ Red = RSI crosses DOWN through Upper → EXIT/SHORT.\n"
                   "• 'Confirm on close' waits for bar close.\n")
        settings = ("Settings\n--------\nRSI length (14), Lower/Upper bands (30/70), Poll s (REST), Source selection.\n"
                    "Save PNG/CSV to export.\n")
        data_src = ("Data Sources\n------------\nYahoo for equities/ETFs/crypto (1m crypto flaky sometimes). Binance REST robust. WS = live.\n")
        tips = ("Reading Trends\n--------------\nRegimes, divergences, MA context, multi timeframe; manage risk.\n")
        trouble = ("Troubleshooting\n---------------\nNo data? Switch Source/interval. Missing candles? pip install mplfinance.\nWS blocked? firewall/wss.\n")
        about = (f"About\n-----\n{APP_BANNER}\nAuthor: ChatGPT (for Ronald)\n")
        self._add_help_tab(nb, "Overview", overview); self._add_help_tab(nb, "Signals", signals)
        self._add_help_tab(nb, "Settings", settings); self._add_help_tab(nb, "Data Sources", data_src)
        self._add_help_tab(nb, "Reading Trends", tips); self._add_help_tab(nb, "Troubleshooting", trouble)
        self._add_help_tab(nb, "About", about)

        help_win.transient(self); help_win.grab_set(); help_win.focus()


if __name__ == "__main__":
    app = App(); app.mainloop()
