import ccxt
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

# ========== [1] جلب البيانات من Pocket Option ==========
def fetch_data(symbol, timeframe='15m', limit=100):
    pocket_option = ccxt.pocketoption({
        'apiKey': 'YOUR_API_KEY',
        'secret': 'YOUR_SECRET',
    })
    ohlcv = pocket_option.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# ========== [2] حساب الدعم والمقاومة (Peaks & Valleys) ==========
def calculate_support_resistance(df, window=5):
    # العثور على القمم (المقاومة)
    peaks = argrelextrema(df['high'].values, np.greater, order=window)[0]
    # العثور على القيعان (الدعم)
    valleys = argrelextrema(df['low'].values, np.less, order=window)[0]
    
    df['resistance'] = np.nan
    df['support'] = np.nan
    
    for peak in peaks:
        df.loc[df.index[peak], 'resistance'] = df['high'].iloc[peak]
    
    for valley in valleys:
        df.loc[df.index[valley], 'support'] = df['low'].iloc[valley]
    
    return df

# ========== [3] حساب المؤشرات الفنية ==========
def calculate_indicators(df):
    # المتوسطات المتحركة
    df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['EMA_50'] = ta.trend.ema_indicator(df['close'], window=50)
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['close'])
    df['MACD_Line'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    
    return df

# ========== [4] توليد إشارات التداول مع الدعم/المقاومة ==========
def generate_signals(df):
    signals = []
    
    for i in range(1, len(df)):
        current_close = df['close'].iloc[i]
        current_support = df['support'].iloc[i]
        current_resistance = df['resistance'].iloc[i]
        
        # إشارة شراء (CALL) - السعر قريب من الدعم + تأكيد المؤشرات
        if (
            df['EMA_20'].iloc[i] > df['EMA_50'].iloc[i] and
            df['RSI'].iloc[i] > 30 and df['RSI'].iloc[i] < 70 and
            df['MACD_Line'].iloc[i] > df['MACD_Signal'].iloc[i] and
            (current_close <= current_support * 1.005)  # ±0.5% من الدعم
        ):
            signals.append(('BUY', df.index[i]))
        
        # إشارة بيع (PUT) - السعر قريب من المقاومة + تأكيد المؤشرات
        elif (
            df['EMA_20'].iloc[i] < df['EMA_50'].iloc[i] and
            df['RSI'].iloc[i] < 70 and df['RSI'].iloc[i] > 30 and
            df['MACD_Line'].iloc[i] < df['MACD_Signal'].iloc[i] and
            (current_close >= current_resistance * 0.995)  # ±0.5% من المقاومة
        ):
            signals.append(('SELL', df.index[i]))
    
    return signals

# ========== [5] تنفيذ الصفقات ==========
def place_trade(symbol, signal_type, amount=10):
    try:
        pocket_option = ccxt.pocketoption({
            'apiKey': 'YOUR_API_KEY',
            'secret': 'YOUR_SECRET',
        })
        
        if signal_type == 'BUY':
            order = pocket_option.create_order(symbol, 'CALL', amount, params={'duration': 15})  # مدة 15 دقيقة
        elif signal_type == 'SELL':
            order = pocket_option.create_order(symbol, 'PUT', amount, params={'duration': 15})
        
        print(f"✅ تم تنفيذ الصفقة: {symbol} - {signal_type}")
        return order
    except Exception as e:
        print(f"❌ فشل في تنفيذ الصفقة: {e}")

# ========== [6] تصور البيانات ==========
def plot_data(df, symbol):
    plt.figure(figsize=(14, 7))
    plt.plot(df['close'], label='السعر', color='blue')
    plt.plot(df['EMA_20'], label='EMA 20', color='orange')
    plt.plot(df['EMA_50'], label='EMA 50', color='red')
    
    # رسم الدعم والمقاومة
    plt.scatter(df.index, df['support'], color='green', label='دعم', marker='^')
    plt.scatter(df.index, df['resistance'], color='red', label='مقاومة', marker='v')
    
    plt.title(f'تحليل {symbol} - إطار 15 دقيقة')
    plt.legend()
    plt.show()

# ========== [7] التشغيل الرئيسي ==========
symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'Gold', 'Oil', 'S&P500', 'DAX', 'Nasdaq']
timeframe = '15m'

for symbol in symbols:
    print(f"جاري تحليل {symbol}...")
    df = fetch_data(symbol, timeframe)
    df = calculate_support_resistance(df)
    df = calculate_indicators(df)
    signals = generate_signals(df)
    
    if signals:
        for signal in signals:
            place_trade(symbol, signal[0])
    
    plot_data(df, symbol)  # عرض الرسم البياني