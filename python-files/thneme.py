# scanner.py

import sys
import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QDoubleSpinBox, QGroupBox,
    QHeaderView, QCheckBox, QFrame, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen


# ===================== 🔔 COMPACT BADGE WITH PULSE ANIMATION =====================
class CompactBadge(QLabel):
    """Clickable badge with fire pulse animation for alerts"""
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__("0")
        self.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.setStyleSheet(self.style_normal())
        self.setFixedSize(28, 28)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()
        self.setToolTip("Click to open full analysis")

        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.pulse)
        self.pulse_state = False
        self.is_pulsing = False

    def style_normal(self):
        return """
            QLabel {
                background-color: #d32f2f;
                color: white;
                border-radius: 14px;
                border: 1px solid #b71c1c;
                font-weight: bold;
            }
        """

    def style_pulsed(self):
        return """
            QLabel {
                background-color: #ff1744;
                color: white;
                border-radius: 14px;
                border: 2px solid #ffeb3b;
                font-weight: bold;
            }
        """

    def start_pulse(self):
        if not self.is_pulsing:
            self.is_pulsing = True
            self.anim_timer.start(600)

    def stop_pulse(self):
        self.is_pulsing = False
        self.anim_timer.stop()
        self.setStyleSheet(self.style_normal())
        self.setFixedSize(28, 28)

    def pulse(self):
        if self.pulse_state:
            self.setStyleSheet(self.style_pulsed())
            self.setFixedSize(30, 30)
        else:
            self.setStyleSheet(self.style_normal())
            self.setFixedSize(28, 28)
        self.pulse_state = not self.pulse_state

    def mousePressEvent(self, ev):
        self.clicked.emit()


# ===================== 📊 PRICE METER (TREND BAR) =====================
class PriceMeter(QFrame):
    """Horizontal bar showing price trend: green (up), red (down), gray (neutral)"""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(18)
        self.price = 0.0
        self.trend = 0  # 1=up, -1=down, 0=neutral
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)

    def update_price(self, price):
        if price > self.price:
            self.trend = 1
        elif price < self.price:
            self.trend = -1
        else:
            self.trend = 0
        self.price = price
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.contentsRect()

        if self.trend == 1:
            color = QColor(0, 180, 0)  # Green
        elif self.trend == -1:
            color = QColor(180, 0, 0)  # Red
        else:
            color = QColor(80, 80, 80)  # Gray

        painter.setBrush(color)
        painter.setPen(QPen(color.darker(150), 1))
        painter.drawRect(rect)


# ===================== 📈 DETAIL POPUP WINDOW =====================
class DetailPopup(QDialog):
    """Popup showing full candle analysis across timeframes"""
    def __init__(self, symbol, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"🔍 {symbol} - Full Analysis")
        self.resize(820, 520)
        self.setModal(False)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)

        # Live Price Meter
        self.price_meter = PriceMeter()
        self.price_meter.setFixedHeight(20)
        layout.addWidget(self.price_meter)

        # Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Timeframe", "Status", "Time Left", "Time", "Open", "High", "Low", "Close"
        ])
        self.table.setRowCount(len(TIMEFRAMES))
        self.table.setFont(QFont("Courier", 10))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for i in range(len(TIMEFRAMES)):
            self.table.setRowHeight(i, 32)
        layout.addWidget(self.table)

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(34)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

        self.symbol = symbol
        self.populate_table()

    def populate_table(self):
        for row, tf in enumerate(TIMEFRAMES.keys()):
            item = QTableWidgetItem(tf)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item)
            for col in range(1, 8):
                item = QTableWidgetItem("...")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

    def update_data(self, results, price):
        for row, (tf, data) in enumerate(results.items()):
            status_item = QTableWidgetItem(data["status"])
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, status_item)

            self.table.setItem(row, 2, QTableWidgetItem(data["time_left"]))
            self.table.setItem(row, 3, QTableWidgetItem(data["time"]))
            self.table.setItem(row, 4, QTableWidgetItem(data["O"]))
            self.table.setItem(row, 5, QTableWidgetItem(data["H"]))
            self.table.setItem(row, 6, QTableWidgetItem(data["L"]))
            self.table.setItem(row, 7, QTableWidgetItem(data["C"]))
        self.price_meter.update_price(price)


# ===================== 🌍 SUPPORTED SYMBOLS & TIMEFRAMES =====================
SUPPORTED_SYMBOLS = [
    "BTCUSDm", "ETHUSDm", "XAUUSDm", "USDKRWm", "USDCADm", "EURGBPm", "USDJPYm",
    "USDCNHm", "USDHKDm", "EURUSDm", "USDCHFm", "AUDUSDm", "GBPUSDm", "NZDUSDm"
]

TIMEFRAMES = {
    "1min": (mt5.TIMEFRAME_M1, 60),
    "5min": (mt5.TIMEFRAME_M5, 300),
    "10min": (mt5.TIMEFRAME_M10, 600),
    "15min": (mt5.TIMEFRAME_M15, 900),
    "30min": (mt5.TIMEFRAME_M30, 1800),
    "1hr": (mt5.TIMEFRAME_H1, 3600),
    "4hr": (mt5.TIMEFRAME_H4, 14400),
    "Daily": (mt5.TIMEFRAME_D1, 86400),
}


# ===================== 🧵 BACKGROUND WORKER THREAD =====================
class ScannerWorker(QThread):
    update_signal = pyqtSignal(str, dict, int)  # symbol, results, count

    def __init__(self):
        super().__init__()
        self.symbols = SUPPORTED_SYMBOLS[:]
        self.tolerance = 0.005
        self.running = True

    def set_tolerance(self, value):
        self.tolerance = value

    def run(self):
        if not mt5.initialize():
            print("❌ FAILED TO CONNECT TO MT5")
            print("👉 Is MetaTrader 5 open and logged in?")
            return

        print("✅ MT5 Connected. Starting scan...")

        try:
            available_symbols = {s.name for s in mt5.symbols_get()}
        except Exception as e:
            print(f"Failed to get symbol list: {e}")
            return

        valid_symbols = [s for s in self.symbols if s in available_symbols]
        invalid = [s for s in self.symbols if s not in available_symbols]
        if invalid:
            print(f"⚠️ Symbols not found: {invalid}")

        self.symbols = valid_symbols

        while self.running:
            for symbol in self.symbols:
                try:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick is None:
                        time.sleep(0.1)
                        continue

                    results = {}
                    count = 0
                    now = datetime.now()

                    for name, (tf, duration) in TIMEFRAMES.items():
                        rates = mt5.copy_rates_from_pos(symbol, tf, 0, 1)
                        if rates is None or len(rates) == 0:
                            continue

                        candle = rates[0]
                        o, h, l, c = candle['open'], candle['high'], candle['low'], candle['close']
                        candle_time = datetime.fromtimestamp(candle['time'])
                        next_time = candle_time + timedelta(seconds=duration)
                        delta = next_time - now
                        mm, ss = divmod(max(0, int(delta.total_seconds())), 60)
                        time_left = f"{mm:02d}:{ss:02d}"

                        price = tick.bid
                        candle_range = h - l

                        if candle_range == 0:
                            status = "..."
                        elif c >= o:  # Bullish: Open ≈ Low
                            if (o - l) / candle_range <= self.tolerance:
                                status = "Bull"
                                count += 1
                            else:
                                status = "None"
                        else:  # Bearish: Open ≈ High
                            if (h - o) / candle_range <= self.tolerance:
                                status = "Bear"
                                count += 1
                            else:
                                status = "None"

                        # Format prices
                        if "JPY" in symbol:
                            fmt = ".3f"
                        elif any(x in symbol for x in ["BTC", "ETH", "XAU"]):
                            fmt = ".2f"
                        else:
                            fmt = ".5f"

                        results[name] = {
                            "status": status,
                            "time_left": time_left,
                            "time": candle_time.strftime('%H:%M'),
                            "O": f"{o:{fmt}}",
                            "H": f"{h:{fmt}}",
                            "L": f"{l:{fmt}}",
                            "C": f"{c:{fmt}}",
                            "price": price
                        }

                    self.update_signal.emit(symbol, results, count)

                except Exception as e:
                    print(f"Error {symbol}: {e}")

            time.sleep(0.8)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


# ===================== 🖼️ MAIN WINDOW =====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 Marubozu Scanner [Live Candle Alerts]")
        self.setGeometry(50, 50, 1366, 768)
        self.setMinimumSize(1000, 600)
        self.dark_mode = True  # ✅ Dark theme by de