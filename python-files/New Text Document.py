import sys
import pandas as pd
import ta
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog

class SignalBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Binary Signal Bot")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()

        self.label = QLabel("CSV ফাইল লোড করুন")
        self.layout.addWidget(self.label)

        self.btn_load = QPushButton("CSV লোড করুন")
        self.btn_load.clicked.connect(self.load_csv)
        self.layout.addWidget(self.btn_load)

        self.signal_label = QLabel("")
        self.layout.addWidget(self.signal_label)

        self.setLayout(self.layout)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSV ফাইল নির্বাচন করুন", "", "CSV Files (*.csv)")
        if path:
            self.label.setText(f"লোড করা ফাইল: {path}")
            df = pd.read_csv(path)

            # Calculate Indicators
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            bb = ta.volatility.BollingerBands(df['close'], window=20)
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_upper'] = bb.bollinger_hband()

            # Signal Logic
            last = df.iloc[-1]
            signal = ""
            if last['rsi'] < 30 and last['close'] <= last['bb_lower']:
                signal = "CALL 📈"
            elif last['rsi'] > 70 and last['close'] >= last['bb_upper']:
                signal = "PUT 📉"
            else:
                signal = "WAIT ⏳"

            self.signal_label.setText(f"সিগন্যাল: {signal}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalBotApp()
    window.show()
    sys.exit(app.exec_())
