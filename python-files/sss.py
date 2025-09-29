import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import random
from datetime import datetime, timedelta
import talib  # 注意：如果未安装talib，可手动计算MACD

# 如果talib未安装，手动计算MACD函数
def calculate_macd(data, fast=12, slow=26, signal=9):
    exp1 = data['Close'].ewm(span=fast).mean()
    exp2 = data['Close'].ewm(span=slow).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

# 股票代码列表（部分A股和港股示例，可扩展）
stocks = [
    '600000.SS',  # 浦发银行 (A)
    '000001.SZ',  # 平安银行 (A)
    '0700.HK',    # 腾讯控股 (HK)
    '0002.HK',    # 中电控股 (HK)
    '600036.SS',  # 招商银行 (A)
    '000333.SZ',  # 美的集团 (A)
    '1398.HK',    # 工商银行 (HK)
    '3988.HK',    # 中国银行 (HK)
    # 添加更多代码...
]

def get_random_stock_data():
    """随机选择股票并获取一年的历史数据"""
    stock_code = random.choice(stocks)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)  # 多取两年数据以随机选择一段
    data = yf.download(stock_code, start=start_date, end=end_date)
    if data.empty:
        return None
    # 随机选择一段一年的数据
    data = data.reset_index()
    start_idx = random.randint(0, len(data) - 252)  # 约一年的交易日
    end_idx = start_idx + 252
    selected_data = data.iloc[start_idx:end_idx].copy()
    selected_data['Stock'] = stock_code
    return selected_data

def add_indicators(data):
    """添加技术指标：MA5, MA10, MA20, MACD"""
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    try:
        macd, signal, hist = talib.MACD(data['Close'].values)
        data['MACD'] = macd
        data['MACD_Signal'] = signal
        data['MACD_Hist'] = hist
    except:
        # 手动计算
        macd, signal_line, histogram = calculate_macd(data)
        data['MACD'] = macd
        data['MACD_Signal'] = signal_line
        data['MACD_Hist'] = histogram
    return data

def plot_kline(data):
    """绘制K线图和指标"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])

    # K线图
    for i in range(len(data)):
        color = 'green' if data['Close'][i] >= data['Open'][i] else 'red'
        ax1.plot([data['Date'][i], data['Date'][i]], [data['Low'][i], data['High'][i]], color=color, linewidth=1)
        ax1.plot([data['Date'][i-1] if i > 0 else data['Date'][i], data['Date'][i]], 
                 [data['Close'][i-1] if i > 0 else data['Open'][i], data['Open'][i]], color=color, linewidth=2)

    ax1.plot(data['Date'], data['MA5'], label='MA5', color='blue')
    ax1.plot(data['Date'], data['MA10'], label='MA10', color='orange')
    ax1.plot(data['Date'], data['MA20'], label='MA20', color='purple')
    ax1.set_title(f'股票 {data["Stock"].iloc[0]} 日K线图')
    ax1.legend()
    ax1.grid(True)

    # MACD
    ax2.plot(data['Date'], data['MACD'], label='MACD', color='blue')
    ax2.plot(data['Date'], data['MACD_Signal'], label='Signal', color='red')
    ax2.bar(data['Date'], data['MACD_Hist'], label='Histogram', color='gray', alpha=0.3)
    ax2.set_title('MACD')
    ax2.legend()
    ax2.grid(True)

    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def simulate_trading(data):
    """模拟交易：用户输入买入/卖出，计算盈亏"""
    cash = 10000  # 初始资金
    shares = 0  # 持股数量
    buy_price = 0
    trades = []  # 记录交易

    print(f"初始资金: {cash} 元")
    print(f"股票代码: {data['Stock'].iloc[0]}")
    print("交易日数: 252 天 (约1年)")
    print("指令: 输入 'buy' 买入, 'sell' 卖出, 'hold' 持有, 'quit' 退出")

    for i in range(len(data)):
        current_date = data['Date'][i]
        current_price = data['Close'][i]
        print(f"\n日期: {current_date.strftime('%Y-%m-%d')}, 收盘价: {current_price:.2f}")
        print(f"当前持股: {shares} 股, 现金: {cash:.2f} 元")
        if shares > 0:
            print(f"当前持仓价值: {shares * current_price:.2f}, 未实现盈亏: {(current_price - buy_price) * shares:.2f}")

        action = input("您的操作 (buy/sell/hold/quit): ").strip().lower()

        if action == 'quit':
            break
        elif action == 'buy' and cash >= current_price:
            buy_shares = int(cash // current_price)
            cost = buy_shares * current_price
            cash -= cost
            shares += buy_shares
            buy_price = current_price
            trades.append({'date': current_date, 'action': 'buy', 'price': current_price, 'shares': buy_shares, 'cost': cost})
            print(f"买入 {buy_shares} 股, 成本: {cost:.2f}")
        elif action == 'sell' and shares > 0:
            revenue = shares * current_price
            cash += revenue
            profit = (current_price - buy_price) * shares
            trades.append({'date': current_date, 'action': 'sell', 'price': current_price, 'shares': shares, 'revenue': revenue, 'profit': profit})
            print(f"卖出 {shares} 股, 收入: {revenue:.2f}, 盈利: {profit:.2f}")
            shares = 0
        elif action == 'hold':
            pass
        else:
            print("无效操作或资金不足，继续持有")

        # 每10天显示一次图（可选，减少频率）
        if i % 10 == 0:
            plot_kline(data.iloc[:i+1])

    # 结束时计算最终结果
    final_value = cash + shares * data['Close'].iloc[-1]
    total_return = (final_value - 10000) / 10000 * 100
    print(f"\n=== 交易结束 ===")
    print(f"最终资金: {final_value:.2f} 元")
    print(f"总回报率: {total_return:.2f}%")
    if total_return > 50:
        print("胜利！盈利超过50%")
    else:
        print("失败。")

    # 打印交易记录
    print("\n交易记录:")
    for trade in trades:
        print(trade)

    # 显示完整图
    plot_kline(data)

# 主程序
if __name__ == "__main__":
    print("欢迎使用炒股训练软件！")
    while True:
        data = get_random_stock_data()
        if data is not None:
            data = add_indicators(data)
            simulate_trading(data)
            replay = input("\n是否再玩一次？(y/n): ").strip().lower()
            if replay != 'y':
                break
        else:
            print("数据获取失败，重试...")