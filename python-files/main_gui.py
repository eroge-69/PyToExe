
import sys, threading, time, yaml
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QDoubleSpinBox, QComboBox, QPushButton, QTextEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject
from bot.brokers import MT5Broker
from bot.strategy import TrendFalseBreakoutStrategy, StrategyParams
from bot.utils import position_size_by_price, RiskConfig, setup_logger

class LogEmitter(QObject):
    text = Signal(str)

class BotThread(threading.Thread):
    def __init__(self, cfg, emitter):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.emitter = emitter
        self._stop = threading.Event()

    def log(self, msg):
        self.emitter.text.emit(msg)

    def run(self):
        try:
            mt5cfg = self.cfg["mt5"]
            broker = MT5Broker(symbol=mt5cfg["symbol"], lot=mt5cfg["lot"], slippage_points=mt5cfg.get("slippage_points",20))
            sp = StrategyParams(
                ma_fast=self.cfg["ma_fast"],
                ma_slow=self.cfg["ma_slow"],
                rsi_period=self.cfg["rsi_period"],
                atr_period=self.cfg["atr_period"],
                rr=self.cfg["take_profit_rr"]
            )
            strat = TrendFalseBreakoutStrategy(sp)
            risk = RiskConfig(self.cfg["risk_per_trade_pct"], self.cfg["max_daily_loss_pct"])

            tf = self.cfg["timeframe"]
            self.log(f"Started: symbol={mt5cfg['symbol']} timeframe={tf}")

            while not self._stop.is_set():
                df = broker.fetch_ohlcv(mt5cfg["symbol"], tf, limit=400)
                df = strat.prepare(df)
                sig = strat.signal(df)
                if sig:
                    balance = broker.get_balance()
                    qty = position_size_by_price(balance, sig["entry"], sig["sl"], risk.risk_per_trade_pct)
                    if qty > 0:
                        res = broker.create_order_with_sl_tp(sig["side"], qty, sl=sig["sl"], tp=sig["tp"])
                        self.log(f"ORDER {sig['side'].upper()} ticket={res['ticket']} entry≈{sig['entry']:.5f} SL={sig['sl']:.5f} TP={sig['tp']:.5f} qty={qty:.2f}")
                time.sleep(10)
        except Exception as e:
            self.log(f"Error: {e}")

    def stop(self):
        self._stop.set()

class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forex MT5 Auto-Trading GUI")
        self.resize(520, 520)

        with open("config.yaml","r",encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)

        form = QFormLayout()

        self.symbol = QLineEdit(self.cfg["mt5"]["symbol"])
        self.tf = QComboBox(); self.tf.addItems(["1m","5m","15m","30m","1h","4h"]); self.tf.setCurrentText(self.cfg["timeframe"])
        self.risk = QDoubleSpinBox(); self.risk.setRange(0.1,10.0); self.risk.setSingleStep(0.1); self.risk.setValue(self.cfg["risk_per_trade_pct"])
        self.rr = QDoubleSpinBox(); self.rr.setRange(1.0,5.0); self.rr.setSingleStep(0.5); self.rr.setValue(self.cfg["take_profit_rr"])
        self.lot = QDoubleSpinBox(); self.lot.setRange(0.01,10.0); self.lot.setSingleStep(0.01); self.lot.setValue(self.cfg["mt5"]["lot"])

        form.addRow("Symbol:", self.symbol)
        form.addRow("Timeframe:", self.tf)
        form.addRow("Risk %:", self.risk)
        form.addRow("RR (TP multiple):", self.rr)
        form.addRow("Lot (fallback):", self.lot)

        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop"); self.stop_btn.setEnabled(False)
        self.log_view = QTextEdit(); self.log_view.setReadOnly(True)

        v = QVBoxLayout(self)
        v.addLayout(form)
        v.addWidget(self.start_btn)
        v.addWidget(self.stop_btn)
        v.addWidget(QLabel("Logs:"))
        v.addWidget(self.log_view, 1)

        self.thread = None
        self.emitter = LogEmitter()
        self.emitter.text.connect(self.on_log)

        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)

    def on_log(self, txt:str):
        self.log_view.append(txt)

    def start_bot(self):
        if self.thread and self.thread.is_alive():
            QMessageBox.information(self, "Info", "Bot already running."); return
        # update cfg from UI
        self.cfg["mt5"]["symbol"] = self.symbol.text().strip()
        self.cfg["timeframe"] = self.tf.currentText()
        self.cfg["risk_per_trade_pct"] = float(self.risk.value())
        self.cfg["take_profit_rr"] = float(self.rr.value())
        self.cfg["mt5"]["lot"] = float(self.lot.value())

        self.thread = BotThread(self.cfg, self.emitter)
        self.thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.on_log("Bot started.")

    def stop_bot(self):
        if self.thread:
            self.thread.stop()
            self.thread.join(timeout=2.0)
            self.thread = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.on_log("Bot stopped.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWin()
    w.show()
    sys.exit(app.exec())
