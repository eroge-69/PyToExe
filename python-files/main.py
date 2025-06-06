
import sys
import pandas as pd
import yfinance as yf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GraphAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("โปรเจคIQ - โปรแกรมวิเคราะห์กราฟ")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.label = QLabel("กรอกสัญลักษณ์หุ้น (เช่น AAPL, BTC-USD):")
        self.symbol_input = QLineEdit()
        self.analyze_button = QPushButton("วิเคราะห์")
        self.analyze_button.clicked.connect(self.analyze)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.label)
        layout.addWidget(self.symbol_input)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def analyze(self):
        symbol = self.symbol_input.text()
        if not symbol:
            return

        df = yf.download(symbol, period="3mo", interval="1d")
        if df.empty:
            self.label.setText("ไม่พบข้อมูลสำหรับสัญลักษณ์นี้")
            return

        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["RSI"] = self.calculate_rsi(df["Close"], 14)

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(211)
        ax.plot(df.index, df["Close"], label="ราคา")
        ax.plot(df.index, df["MA20"], label="MA 20 วัน", linestyle="--")
        ax.set_title(f"กราฟราคาของ {symbol}")
        ax.legend()

        ax2 = self.canvas.figure.add_subplot(212)
        ax2.plot(df.index, df["RSI"], label="RSI", color="purple")
        ax2.axhline(70, color="red", linestyle="--")
        ax2.axhline(30, color="green", linestyle="--")
        ax2.set_title("RSI Indicator")
        ax2.legend()

        self.canvas.draw()

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphAnalyzer()
    window.show()
    sys.exit(app.exec_())
