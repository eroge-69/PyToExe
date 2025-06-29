# Simple Trading Console Version with Auto-Trading Template

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import datetime

try:
    import yfinance as yf
    LIVE_DATA = True
except ImportError:
    LIVE_DATA = False
    print("⚠️ yfinance not installed. Running with simulated data.")

# === Data Loading ===
def load_nifty_data():
    if LIVE_DATA:
        data = yf.download("^NSEI", start="2013-01-01")
        data = data.rename(columns={"Adj Close": "Close"})
    else:
        dates = pd.date_range(start="2013-01-01", periods=2520, freq="B")
        np.random.seed(101)
        data = pd.DataFrame(index=dates)
        data['Close'] = np.cumsum(np.random.randn(len(dates)) * 5 + 50) + 7500
        data['Open'] = data['Close'] + np.random.randn(len(dates)) * 2
        data['High'] = data[['Open', 'Close']].max(axis=1) + np.random.rand(len(dates)) * 2
        data['Low'] = data[['Open', 'Close']].min(axis=1) - np.random.rand(len(dates)) * 2
        data['Volume'] = np.random.randint(1000000, 5000000, size=len(dates))
    return data.dropna()

# === Indicators ===
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def add_technical_indicators(df):
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['RSI'] = compute_rsi(df['Close'])
    df['Volatility'] = df['Close'].rolling(window=10).std()
    df['Return'] = df['Close'].pct_change()
    df['Gap'] = df['Open'] - df['Close'].shift(1)
    df['Target'] = np.where(df['Return'].shift(-1) > 0, 1, 0)
    df.dropna(inplace=True)
    return df

# === Model Training ===
def train_model(df):
    features = ['MA10', 'MA50', 'RSI', 'Volatility', 'Gap']
    X = df[features]
    y = df['Target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Model Accuracy: {acc:.2f}")
    return model

# === Strategy Rules ===
def recommend_strategy(row):
    if row['RSI'] < 30 and row['Volatility'] > 10:
        return "Swing Trading"
    elif row['RSI'] > 70 and row['MA10'] > row['MA50']:
        return "Trend Following"
    elif row['Gap'] > 1 and row['Volatility'] < 5:
        return "Gap Trading"
    elif row['MA10'] > row['MA50'] and row['Return'] > 0.01:
        return "Momentum Trading"
    elif row['MA10'] < row['MA50'] and row['Volatility'] < 5:
        return "Range Trading"
    elif row['Gap'] > 2 and row['Volume'] > 4000000:
        return "News Trading"
    elif row['Volatility'] < 3 and row['Return'] < 0.002:
        return "Scalping"
    elif row['RSI'] < 40 and row['MA50'] > row['MA10']:
        return "Position Trading"
    elif abs(row['Return']) > 0.03 and row['Gap'] > 2:
        return "Breakout Trading"
    elif row['Return'] > 0.02 and row['Volume'] > 4500000:
        return "Algorithmic Trading"
    elif row['Return'] < -0.03:
        return "Arbitrage Trading"
    elif row['Volatility'] < 2 and abs(row['MA10'] - row['MA50']) < 5:
        return "Pairs Trading"
    else:
        return "Hold"

# === Backtest + Equity ===
def backtest_strategies(df):
    strategies = []
    pnl = []
    equity_curve = [1]
    for i in range(1, len(df) - 1):
        row = df.iloc[i]
        strategy = recommend_strategy(row)
        daily_return = df.iloc[i + 1]['Return']
        profit = daily_return if strategy != "Hold" else 0
        strategies.append(strategy)
        pnl.append(profit)
        equity_curve.append(equity_curve[-1] * (1 + profit))

    df = df.iloc[1:-1].copy()
    df['Strategy'] = strategies
    df['StrategyPnL'] = pnl
    df['Equity'] = equity_curve[1:]
    return df

# === Main App ===
def main():
    print("📊 Simple Trading - Nifty Trend & Strategy Detector")
    df = load_nifty_data()
    df = add_technical_indicators(df)
    model = train_model(df)

    latest = df.iloc[-1]
    strategy = recommend_strategy(latest)
    print("\n📈 Suggested Strategy for Today:")
    print(f"Strategy: {strategy}")
    print(f"RSI: {latest['RSI']:.2f}, MA10: {latest['MA10']:.2f}, MA50: {latest['MA50']:.2f}, Volatility: {latest['Volatility']:.2f}, Gap: {latest['Gap']:.2f}, Return: {latest['Return']:.4f}, Volume: {latest['Volume']}")

    
    df = backtest_strategies(df)

    print("\n📌 Strategy Frequency:")
    print(df['Strategy'].value_counts())

    print("\n📉 Equity Curve Summary:")
    print(df['Equity'].describe())

    df['Equity'].plot(title="Equity Curve", figsize=(10, 5))
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    df.to_csv("simple_trading_backtest.csv")
    print("\n✅ Backtest results saved to 'simple_trading_backtest.csv'")

if __name__ == "__main__":
    main()
