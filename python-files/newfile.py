"""
The MIT License (MIT)

Copyright (c) <year> <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# مرحله 1: دریافت داده‌ها
def fetch_data(crypto_id, currency='usd', days='1'):
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency={currency}&days={days}'
        response = requests.get(url)
        data = response.json()
        
        # پردازش داده‌ها به DataFrame
        prices = data['prices']  # لیست قیمت‌ها
        df = pd.DataFrame(prices, columns=['timestamp', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open'] = df['close']  # در اینجا فقط برای سازگاری، می‌توانیم مقدار close را به open نسبت دهیم
        df['high'] = df['close']  # فرض بر اینکه high برابر با close است
        df['low'] = df['close']  # فرض بر اینکه low برابر با close است
        df['volume'] = 0  # فرض بر اینکه حجم را نداریم
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# مرحله 2: پردازش داده‌ها
def prepare_data(data):
    data['return'] = data['close'].pct_change()
    data['direction'] = np.where(data['return'] > 0, 1, 0)
    return data.dropna()

# مرحله 3: پیش‌بینی
def predict(data):
    if len(data) < 2:  # Ensure there is enough data
        print("Not enough data to predict.")
        return None
    X = np.array(range(len(data))).reshape(-1, 1)  # زمان به عنوان ویژگی
    y = data['close'].values
    model = LinearRegression()
    model.fit(X, y)
    future = np.array([[len(data) + i] for i in range(1, 5)])  # پیش‌بینی 4 ساعت آینده
    predictions = model.predict(future)
    return predictions

# مرحله 4: رسم نمودار
def plot_data(data, predictions):
    plt.figure(figsize=(14, 7))
    plt.plot(data['timestamp'], data['close'], label='Close Price', color='blue')
    future_times = [data['timestamp'].iloc[-1] + pd.Timedelta(hours=i) for i in range(1, 5)]
    plt.plot(future_times, predictions, label='Predicted Prices', color='red', marker='o')
    plt.title('Cryptocurrency Price Prediction')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

# استفاده از توابع
crypto_id = 'bitcoin'  # مثال: بیت کوین
data = fetch_data(crypto_id)

if data is not None:
    processed_data = prepare_data(data)
    predictions = predict(processed_data)
    if predictions is not None:
        plot_data(processed_data, predictions)