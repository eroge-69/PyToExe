#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pro Trading Scanner & Trade Planner (PyQt5)
Application d'analyse boursière avec plan de trade intégré.
"""

import sys, os, math, traceback
from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

APP_NAME = "Pro Trading Scanner"

# ==== Indicateurs techniques ====

def sma(s, n): return s.rolling(n).mean()
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(n).mean()
    ma_down = down.rolling(n).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def macd(s, fast=12, slow=26, signal=9):
    e1 = ema(s, fast); e2 = ema(s, slow)
    line = e1 - e2
    signal_line = ema(line, signal)
    hist = line - signal_line
    return line, signal_line, hist

def atr(df, n=14):
    h, l, c = df['High'], df['Low'], df['Close']
    prev_c = c.shift(1)
    tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ==== Score automatique ====

def score_row(df):
    if len(df) < 60:
        return None
    close = df['Close']
    ret_5 = close.pct_change(5).iloc[-1]
    ret_20 = close.pct_change(20).iloc[-1]
    sma20 = sma(close, 20); sma50 = sma(close, 50); sma200 = sma(close, 200)
    above_sma20 = (close.iloc[-1] > sma20.iloc[-1]) if not pd.isna(sma20.iloc[-1]) else False
    above_sma50 = (close.iloc[-1] > sma50.iloc[-1]) if not pd.isna(sma50.iloc[-1]) else False
    trend_200 = (sma200.iloc[-1] - sma200.iloc[-10]) / (sma200.iloc[-10]) if not pd.isna(sma200.iloc[-10]) else 0.0
    rsi14 = rsi(close, 14).iloc[-1]
    macd_line, macd_sig, macd_hist = macd(close)
    macd_recent = macd_hist.iloc[-3:]
    macd_rising = int(macd_recent.is_monotonic_increasing) if macd_recent.notna().all() else 0
    hh = df['High'].rolling(55).max().iloc[-1]
    breakout = int(close.iloc[-1] >= hh * 0.999) if not pd.isna(hh) else 0
    a = atr(df, 14).iloc[-1]
    atr_pct = a / close.iloc[-1] if a and close.iloc[-1] else np.nan
    def nz(x): return 0.0 if (x is None or np.isnan(x)) else float(x)
    m_trend = max(0.0, min(1.0, 0.5 + trend_200*10))
    m_mom = max(0.0, min(1.0, 0.5* nz(ret_5) * 10 + 0.5* nz(ret_20) * 5 + 0.5))
    m_rsi = 1 - abs((nz(rsi14) - 50)/50)
    m_macd = 1.0 if macd_rising else 0.4
    m_breakout = 1.0 if breakout else 0.2
    m_vol = 1 - max(0.0, min(1.0, nz(atr_pct)*4))
    m_structure = (0.5 if above_sma20 else 0.2) + (0.5 if above_sma50 else 0.2)
    score = (0.25*m_trend + 0.25*m_mom + 0.15*m_rsi + 0.15*m_macd + 0.15*m_breakout + 0.05*m_vol + 0.05*m_structure)
    metrics = {
        'score': round(score, 4),
        'ret_5': round(nz(ret_5), 4),
        'ret_20': round(nz(ret_20), 4),
        'rsi14': round(nz(rsi14), 2),
        'atr_pct': round(nz(atr_pct), 4),
        'breakout': breakout,
        'above_sma20': int(above_sma20),
        'above_sma50': int(above_sma50),
    }
    return metrics

# ==== Téléchargement des données ====

def download_ticker(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, threads=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df = df.reset_index()
        keep = ['Date','Open','High','Low','Close','Volume']
        df = df[keep].dropna()
        return df
    except Exception:
        return None

# ==== Graphique Matplotlib intégré ====

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#0e1116")
        self.ax_price = self.fig.add_subplot(3,1,1)
        self.ax_macd = self.fig.add_subplot(3,1,2, sharex=self.ax_price)
        self.ax_rsi = self.fig.add_subplot(3,1,3, sharex=self.ax_price)
        super().__init__(self.fig)
        self.fig.tight_layout(pad=2.0)

    def plot_df(self, df, title=""):
        self.ax_price.clear(); self.ax_macd.clear(); self.ax_rsi.clear()
        self.ax_price.set_facecolor("#0e1116")
        self.ax_macd.set_facecolor("#0e1116")
        self.ax_rsi.set_facecolor("#0e1116")
        dates = mdates.date2num(pd.to_datetime(df['Date']))
        self.ax_price.plot_date(dates, df['Close'], '-', linewidth=1.2, label="Close")
        self.ax_price.fill_between(dates, df['Low'], df['High'], alpha=0.08)
        close = df['Close']
        sma20 = sma(close,20); ema20 = ema(close,20); sma50=sma(close,50)
        self.ax_price.plot_date(dates, sma20, '-', linewidth=0.9, label="SMA20")
        self.ax_price.plot_date(dates, sma50, '-', linewidth=0.9, label="SMA50")
        self.ax_price.plot_date(dates, ema20, '-', linewidth=0.9, label="EMA20")
        self.ax_price.legend(loc="upper left", fontsize="small")
        self.ax_price.set_title(title, color="white")
        self.ax_price.set_ylabel("Prix", color="white")
        macd_line, macd_signal, hist = macd(close)
        self.ax_macd.bar(dates, hist, width=0.6, alpha=0.6)
        self.ax_macd.plot_date(dates, macd_line, '-', linewidth=0.9, label="MACD")
        self.ax_macd.plot_date(dates, macd_signal, '-', linewidth=0.9, label="Signal")
        self.ax_macd.legend(loc="upper left", fontsize="small")
        r = rsi(close,14)
        self.ax_rsi.plot_date(dates, r, '-', linewidth=0.9, label="RSI14")
        self.ax_rsi.axhline(70, linestyle='--', alpha=0.4)
        self.ax_rsi.axhline(30, linestyle='--', alpha=0.4)
        self.ax_rsi.set_ylim(0,100)
        self.ax_rsi.legend(loc="upper left", fontsize="small")
        self.ax_rsi.xaxis_date()
        self.ax_rsi.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        for lbl in self.ax_rsi.get_xticklabels():
            lbl.set_rotation(30); lbl.set_ha('right')
        self.fig.tight_layout(pad=2.0)
        self.draw_idle()

# ==== Trade Planner (Dock) ====

class TradePlanner(QtWidgets.QWidget):
    planGenerated = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setObjectName("TradePlanner")
        self._build_ui()
        self._apply_style()
    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QGridLayout()
        self.sym = QtWidgets.QLineEdit(); self.sym.setPlaceholderText("Ticker ex: AAPL")
        self.entry = QtWidgets.QDoubleSpinBox(); self.entry.setMaximum(1e9); self.entry.setDecimals(4)
        self.stop = QtWidgets.QDoubleSpinBox(); self.stop.setMaximum(1e9); self.stop.setDecimals(4)
        self.tp = QtWidgets.QDoubleSpinBox(); self.tp.setMaximum(1e9); self.tp.setDecimals(4)
        self.capital = QtWidgets.QDoubleSpinBox(); self.capital.setMaximum(1e12); self.capital.setValue(10000)
        self.risk_pct = QtWidgets.QDoubleSpinBox(); self.risk_pct.setDecimals(2); self.risk_pct.setSuffix(" %"); self.risk_pct.setValue(1.0); self.risk_pct.setMaximum(100)
        form.addWidget(QtWidgets.QLabel("Symbole"),0,0); form.addWidget(self.sym,0,1)
        form.addWidget(QtWidgets.QLabel("Entrée"),1,0); form.addWidget(self.entry,1,1)
        form.addWidget(QtWidgets.QLabel("Stop Loss"),2,0); form.addWidget(self.stop,2,1)
        form.addWidget(QtWidgets.QLabel("Take Profit"),3,0); form.addWidget(self.tp,3,1)
        form.addWidget(QtWidgets.QLabel("Capital"),4,0); form.addWidget(self.capital,4,1)
        form.addWidget(QtWidgets.QLabel("Risque (%)"),5,0); form.addWidget(self.risk_pct,5,1)
        layout.addLayout(form)
        self.compute_btn = QtWidgets.QPushButton("Calculer le plan")
        self.compute_btn.clicked.connect(self.compute_plan)
        layout.addWidget(self.compute_btn)
        self.result = QtWidgets.QTextEdit(); self.result.setReadOnly(True); self.result.setMinimumHeight(180)
        layout.addWidget(self.result)
        copy_btn = QtWidgets.QPushButton("Copier le plan (pour l'autre chat)")
        copy_btn.clicked.connect(self.copy_plan)
        layout.addWidget(copy_btn)
    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#TradePlanner { background-color: #0e1116; color: #e6e9ef; }
            QLineEdit, QDoubleSpinBox, QTextEdit { background:#161a20; color:#e6e9ef; border:1px solid #2b2f36; border-radius:8px; padding:6px; }
            QPushButton { background:#2d74da; color:white; border:none; padding:8px 12px; border-radius:8px; font-weight:600; }
            QPushButton:hover { background:#3c84ea; }
            QLabel { color:#b8bcc6; }
        """)
    def compute_plan(self):
        try:
            sym = self.sym.text().strip().upper() or "SYMB"
            entry = float(self.entry.value())
            stop = float(self.stop.value())
            tp = float(self.tp.value())
            capital = float(self.capital.value())
            risk_pct = float(self.risk_pct.value())/100.0
            if entry <= 0 or stop <= 0 or tp <= 0:
                raise ValueError("Les prix doivent être > 0")
            if stop >= entry:
                rr = (tp - entry) / (entry - stop) if (entry - stop) > 0 else float('nan')
            else:
                rr = (entry - tp) / (stop - entry) if (stop - entry) > 0 else float('nan')
            risk_amount = capital * risk_pct
            per_unit_risk = abs(entry - stop)
            qty = math.floor(risk_amount / per_unit_risk) if per_unit_risk > 0 else 0
            pnl_at_tp = (tp - entry) * qty
            pnl_at_sl = (stop - entry) * qty
            direction = "LONG" if tp > entry else "SHORT"
            text = f"""[Plan de trade]
Symbole: {sym}
Direction: {direction}
Entrée: {entry:.4f}
Stop Loss: {stop:.4f}
Take Profit: {tp:.4f}
Taille de position (approx): {qty} unités
Risque: {risk_pct*100:.2f}% du capital ({risk_amount:.2f})
R:R estimé: {rr:.2f}
PnL à TP: {pnl_at_tp:.2f}
PnL à SL: {pnl_at_sl:.2f}
Notes: Respecter le plan, pas de revenge trading."""
            self.result.setPlainText(text)
            self.planGenerated.emit(text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", str(e))
    def copy_plan(self):
        QtWidgets.QApplication.clipboard().setText(self.result.toPlainText())

# ==== Fenêtre principale ====

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 820)
        self.favorites = set()
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Barre de contrôle
        top = QtWidgets.QHBoxLayout()
        self.btn_scan = QtWidgets.QPushButton("Recherche automatique")
        self.btn_fav = QtWidgets.QPushButton("Favoris")
        self.btn_deep = QtWidgets.QPushButton("Analyse profonde")
        self.btn_trade = QtWidgets.QPushButton("Trade")
        self.interval = QtWidgets.QComboBox(); self.interval.addItems(["1d","1h","4h","1wk"])
        self.period = QtWidgets.QComboBox(); self.period.addItems(["6mo","1y","2y","5y"])
        self.search = QtWidgets.QLineEdit(); self.search.setPlaceholderText("Filtrer par ticker...")

        for w in [self.btn_scan,self.btn_fav,self.btn_deep,self.btn_trade,
                  QtWidgets.QLabel("Intervalle"), self.interval,
                  QtWidgets.QLabel("Période"), self.period, self.search]:
            if isinstance(w, QtWidgets.QLabel):
                w.setStyleSheet("color:#b8bcc6;")
            top.addWidget(w)
        top.addStretch()
        layout.addLayout(top)

        # Table
        self.table = QtWidgets.QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(["Ticker","Score","ret_5","ret_20","RSI","ATR%","Breakout",">SMA20",">SMA50","Action"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        layout.addWidget(self.table)

        # Graph
        self.canvas = MplCanvas(self, width=9, height=5, dpi=100)
        layout.addWidget(self.canvas)

        # Trade Planner
        self.trade = TradePlanner()
        dock = QtWidgets.QDockWidget("Trade Planner")
        dock.setWidget(self.trade)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

        # Connexions
        self.btn_scan.clicked.connect(self.scan_universe)
        self.btn_fav.clicked.connect(self.show_favorites)
        self.btn_deep.clicked.connect(self.deep_analysis)
        self.btn_trade.clicked.connect(lambda: dock.raise_())
        self.search.textChanged.connect(self._filter_table)
        self.table.itemSelectionChanged.connect(self._on_table_select)

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background:#0e1116; }
            QPushButton { background:#2d74da; color:white; border:none; padding:8px 12px; border-radius:8px; font-weight:600; }
            QPushButton:hover { background:#3c84ea; }
            QTableWidget { background:#12161f; color:#e6e9ef; gridline-color:#2b2f36; selection-background-color:#1f2632; }
            QHeaderView::section { background:#161a20; color:#b8bcc6; padding:6px; border:0; }
            QComboBox, QLineEdit { background:#161a20; color:#e6e9ef; border:1px solid #2b2f36; border-radius:6px; padding:6px; }
        """)

    def _load_universe(self):
        path = os.path.join(os.path.dirname(__file__), "sample_universe.txt")
        if not os.path.exists(path):
            return ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","AMD","NFLX","INTC","IBM","ORCL","BA","JNJ","PG","KO","PEP","XOM","CVX","BTC-USD","ETH-USD"]
        with open(path, "r", encoding="utf-8") as f:
            tickers = [ln.strip() for ln in f if ln.strip()]
        return tickers[:300]

    def scan_universe(self):
        try:
            self.table.setRowCount(0)
            tickers = self._load_universe()
            period = self.period.currentText(); interval = self.interval.currentText()
            for t in tickers:
                df = download_ticker(t, period=period, interval=interval)
                if df is None or len(df) < 60:
                    continue
                metrics = score_row(df)
                if not metrics:
                    continue
                r = self.table.rowCount(); self.table.insertRow(r)
                self.table.setItem(r,0,QtWidgets.QTableWidgetItem(t))
                self.table.setItem(r,1,QtWidgets.QTableWidgetItem(str(metrics['score'])))
                self.table.setItem(r,2,QtWidgets.QTableWidgetItem(str(metrics['ret_5'])))
                self.table.setItem(r,3,QtWidgets.QTableWidgetItem(str(metrics['ret_20'])))
                self.table.setItem(r,4,QtWidgets.QTableWidgetItem(str(metrics['rsi14'])))
                self.table.setItem(r,5,QtWidgets.QTableWidgetItem(str(metrics['atr_pct'])))
                self.table.setItem(r,6,QtWidgets.QTableWidgetItem(str(metrics['breakout'])))
                self.table.setItem(r,7,QtWidgets.QTableWidgetItem(str(metrics['above_sma20'])))
                self.table.setItem(r,8,QtWidgets.QTableWidgetItem(str(metrics['above_sma50'])))
                fav_btn = QtWidgets.QPushButton("★" if t in self.favorites else "☆")
                fav_btn.clicked.connect(lambda _, sym=t, btn=fav_btn: self._toggle_fav(sym, btn))
                self.table.setCellWidget(r,9,fav_btn)
            self.table.sortItems(1, QtCore.Qt.DescendingOrder)
        except Exception:
            traceback.print_exc()

    def show_favorites(self):
        for r in range(self.table.rowCount()):
            item = self.table.item(r,0)
            self.table.setRowHidden(r, item.text() not in self.favorites)

    def deep_analysis(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        t = self.table.item(rows[0].row(),0).text()
        df = download_ticker(t, period="1y", interval="1d")
        if df is None: return
        self.canvas.plot_df(df, title=f"Analyse {t}")

    def _filter_table(self, text):
        text = text.strip().upper()
        for r in range(self.table.rowCount()):
            item = self.table.item(r,0)
            self.table.setRowHidden(r, text not in item.text().upper())

    def _on_table_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        t = self.table.item(rows[0].row(),0).text()
        df = download_ticker(t, period=self.period.currentText(), interval=self.interval.currentText())
        if df is None: return
        self.canvas.plot_df(df, title=t)

    def _toggle_fav(self, sym, btn):
        if sym in self.favorites: self.favorites.remove(sym); btn.setText("☆")
        else: self.favorites.add(sym); btn.setText("★")

# ==== Main ====

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    w = MainWindow(); w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
