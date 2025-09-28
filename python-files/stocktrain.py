import sys
import akshare as ak
import pandas as pd
import numpy as np
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplfinance as mpf
from datetime import datetime

class StockTrainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cash = 100000  # 初始资金
        self.holdings = 0  # 持有股数
        self.bought_price = 0  # 买入均价
        self.trade_log = []  # 交易记录
        self.current_stock = None
        self.data = None
        self.session_start_cash = self.cash
        self.init_ui()
        self.load_random_stock()

    def init_ui(self):
        self.setWindowTitle("炒股训练模拟器 v1.0")
        self.setGeometry(100, 100, 1200, 800)

        # 主窗口
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        # 顶部信息栏
        info_layout = QHBoxLayout()
        self.label_info = QLabel("股票：")
        self.label_time = QLabel("时间范围：")
        self.label_cash = QLabel(f"资金：¥{self.cash:,}")
        info_layout.addWidget(self.label_info)
        info_layout.addWidget(self.label_time)
        info_layout.addStretch()
        info_layout.addWidget(self.label_cash)
        main_layout.addLayout(info_layout)

        # 控制按钮
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("新训练")
        self.btn_buy = QPushButton("买入")
        self.btn_sell = QPushButton("卖出")
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_buy)
        btn_layout.addWidget(self.btn_sell)
        main_layout.addLayout(btn_layout)

        # K线图
        self.fig = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)

        # 持仓信息
        status_layout = QHBoxLayout()
        self.label_holdings = QLabel("持仓：0股")
        self.label_profit = QLabel("收益率：0.00%")
        self.label_action = QLabel("当前操作：无")
        status_layout.addWidget(self.label_holdings)
        status_layout.addWidget(self.label_profit)
        status_layout.addWidget(self.label_action)
        main_layout.addLayout(status_layout)

        # 交易记录
        self.trade_text = QTextEdit()
        self.trade_text.setMaximumHeight(150)
        self.trade_text.setReadOnly(True)
        main_layout.addWidget(self.trade_text)

        main_widget.setLayout(main_layout)

        # 连接信号
        self.btn_new.clicked.connect(self.load_random_stock)
        self.btn_buy.clicked.connect(self.buy_stock)
        self.btn_sell.clicked.connect(self.sell_stock)

    def load_random_stock(self):
        # 随机选择A股或港股
        if random.choice([True, False]):
            # A股示例（可扩展为随机选择）
            codes = ["600519", "000858", "000001", "601398", "601857", "000568", "000895", "002415", "000651", "000860"]
            code = random.choice(codes)
            market = ".SH" if code.startswith("6") else ".SZ"
            full_code = code + market
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20200101", end_date="20231231")
        else:
            # 港股示例
            codes = ["00700", "00941", "00388", "02318", "00005", "01810", "09988", "09618", "09866", "09961"]
            code = random.choice(codes)
            full_code = code + ".HK"
            df = ak.stock_hk_hist(symbol=code, period="daily", start_date="20200101", end_date="20231231")

        if df is None or df.empty:
            QMessageBox.warning(self, "错误", "获取数据失败，请重试")
            return

        # 随机截取一年数据（250个交易日）
        if len(df) < 250:
            QMessageBox.warning(self, "错误", "数据不足一年")
            return

        start_idx = random.randint(0, len(df) - 250)
        df = df.iloc[start_idx:start_idx + 250].copy()

        # 格式化数据
        df = df.set_index(pd.to_datetime(df["日期"]))
        df = df[["开盘", "最高", "最低", "收盘", "成交量"]].rename(
            columns={"开盘": "Open", "最高": "High", "最低": "Low", "收盘": "Close", "成交量": "Volume"}
        )
        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

        self.current_stock = full_code
        self.data = df

        # 重置状态
        self.cash = 100000
        self.holdings = 0
        self.bought_price = 0
        self.trade_log = []
        self.session_start_cash = self.cash

        # 更新UI
        start_date = df.index[0].strftime('%Y-%m-%d')
        end_date = df.index[-1].strftime('%Y-%m-%d')
        self.label_info.setText(f"股票：{full_code}")
        self.label_time.setText(f"时间范围：{start_date} ~ {end_date}")
        self.update_ui()

        # 绘制K线图
        self.fig.clear()
        ax = self.fig.add_subplot()
        mpf.plot(
            self.data,
            type='candle',
            ax=ax,
            volume=True,
            style='charles',
            title=f'{full_code} 日K线图',
            ylabel='价格',
            ylabel_lower='成交量'
        )
        self.canvas.draw()

    def buy_stock(self):
        if self.holdings > 0:
            QMessageBox.warning(self, "提示", "已持有股票，不能重复买入")
            return
        if self.cash <= 0:
            QMessageBox.warning(self, "提示", "资金不足")
            return

        current_price = float(self.data.iloc[-1]["Close"])
        shares = int(self.cash // current_price)
        if shares == 0:
            QMessageBox.warning(self, "提示", "资金不足，无法买入")
            return

        cost = shares * current_price
        self.cash -= cost
        self.holdings = shares
        self.bought_price = current_price

        # 记录交易
        date = self.data.index[-1].strftime('%Y-%m-%d')
        self.trade_log.append({
            "date": date,
            "action": "买入",
            "price": current_price,
            "shares": shares,
            "amount": cost,
            "cash": self.cash
        })

        self.label_action.setText(f"买入 {shares} 股 @ ¥{current_price:.2f}")
        self.update_ui()

    def sell_stock(self):
        if self.holdings == 0:
            QMessageBox.warning(self, "提示", "未持有股票")
            return

        current_price = float(self.data.iloc[-1]["Close"])
        proceeds = self.holdings * current_price
        self.cash += proceeds

        # 记录交易
        date = self.data.index[-1].strftime('%Y-%m-%d')
        profit = proceeds - (self.holdings * self.bought_price)
        self.trade_log.append({
            "date": date,
            "action": "卖出",
            "price": current_price,
            "shares": self.holdings,
            "amount": proceeds,
            "profit": profit,
            "cash": self.cash
        })

        self.label_action.setText(f"卖出 {self.holdings} 股 @ ¥{current_price:.2f}，盈亏 ¥{profit:.2f}")
        self.holdings = 0
        self.bought_price = 0

        # 检查胜负
        final_profit_rate = (self.cash - self.session_start_cash) / self.session_start_cash
        if final_profit_rate >= 0.5:
            QMessageBox.information(self, "胜利", f"恭喜！收益率 {final_profit_rate*100:.2f}%，挑战成功！\n目标：>50%")
        else:
            QMessageBox.information(self, "挑战结束", f"收益率 {final_profit_rate*100:.2f}%，再接再厉！\n目标：>50%")

        self.update_ui()

    def update_ui(self):
        self.label_cash.setText(f"资金：¥{self.cash:,.2f}")
        self.label_holdings.setText(f"持仓：{self.holdings}股")
        profit_rate = (self.cash - self.session_start_cash) / self.session_start_cash
        self.label_profit.setText(f"收益率：{profit_rate*100:.2f}%")

        # 更新交易记录显示
        log_text = ""
        for record in self.trade_log[-10:]:  # 显示最近10条
            action = record["action"]
            date = record["date"]
            price = record["price"]
            shares = record["shares"]
            amount = record["amount"]
            profit = record.get("profit", 0)
            log_text += f"{date} {action} {shares}股 @ ¥{price:.2f}, 金额 ¥{amount:.2f}"
            if profit != 0:
                log_text += f", 盈亏 ¥{profit:.2f}"
            log_text += "\n"
        self.trade_text.setPlainText(log_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockTrainApp()
    window.show()
    sys.exit(app.exec_())