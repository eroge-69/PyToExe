import yfinance as yf
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score
import joblib

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_btc_data(days=730):
    df = yf.download("BTC-USD", period=f"{days}d", interval="1d", auto_adjust=False)
    df.dropna(inplace=True)

    df['Return'] = df['Close'].pct_change()
    df['Direction'] = df['Return'].shift(-1).apply(lambda x: 1 if x > 0 else 0)
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['RSI'] = compute_rsi(df['Close'], 14)
    df['Momentum'] = df['Close'] - df['Close'].shift(10)
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['Volatility'] = df['Close'].rolling(window=10).std()
    df['Lag_1'] = df['Return'].shift(1)
    df['Lag_2'] = df['Return'].shift(2)
    df['Lag_3'] = df['Return'].shift(3)

    df.dropna(inplace=True)
    return df

def train_xgboost_with_tuning():
    df = get_btc_data()

    features = ['SMA_10', 'SMA_50', 'RSI', 'Momentum', 'MACD', 'Volatility', 'Lag_1', 'Lag_2', 'Lag_3']
    X = df[features]
    y = df['Direction']

    tscv = TimeSeriesSplit(n_splits=5)
    model = xgb.XGBClassifier(eval_metric='logloss', use_label_encoder=False)

    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.8, 1.0]
    }

    grid_search = GridSearchCV(model, param_grid, cv=tscv, scoring='accuracy', n_jobs=-1, verbose=1)
    grid_search.fit(X, y)

    best_model = grid_search.best_estimator_
    predictions = best_model.predict(X)
    accuracy = accuracy_score(y, predictions)

    print("🔥 Best Parameters:", grid_search.best_params_)
    print(f"✅ Final Accuracy: {accuracy:.2f}")

    joblib.dump(best_model, "btc_model.pkl")

if __name__ == "__main__":
    train_xgboost_with_tuning()
