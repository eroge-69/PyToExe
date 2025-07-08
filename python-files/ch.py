import time
import schedule
from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta

# --- CÀI ĐẶT ---
client = Client()

# Biến toàn cục để lưu danh sách các cặp đủ điều kiện
LONG_LISTED_SYMBOLS = []

def update_symbol_list():
    """
    Bước 1: Lấy và cập nhật danh sách các cặp USDT future đã list trên 6 tháng.
    Hàm này sẽ được chạy 1 lần khi khởi động và sau đó mỗi 24 giờ.
    """
    global LONG_LISTED_SYMBOLS
    print(f"\n🔄 [ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] Đang cập nhật danh sách các cặp giao dịch...")
    try:
        six_months_ago = datetime.now() - timedelta(days=180)
        exchange_info = client.futures_exchange_info()
        all_symbols = [s['symbol'] for s in exchange_info['symbols'] if s['quoteAsset'] == 'USDT' and s['contractType'] == 'PERPETUAL']

        updated_list = []
        for symbol in all_symbols:
            klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, limit=1, startTime=0)
            if klines:
                listing_time = datetime.fromtimestamp(klines[0][0] / 1000)
                if listing_time < six_months_ago:
                    updated_list.append(symbol)
        
        LONG_LISTED_SYMBOLS = updated_list
        print(f"✅ Đã cập nhật xong! Hiện có {len(LONG_LISTED_SYMBOLS)} cặp đủ điều kiện.\n")

    except Exception as e:
        print(f"Lỗi khi cập nhật danh sách cặp giao dịch: {e}")


def scan_bollinger_bands():
    """
    Bước 2 & 3: Quét dải Bollinger trên các cặp đã được lọc.
    Hàm này sẽ chạy mỗi 5 phút.
    """
    if not LONG_LISTED_SYMBOLS:
        print("Danh sách cặp giao dịch đang trống, vui lòng chờ cập nhật...")
        return

    try:
        print(f"--- Scanning lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

        # 2. LỌC CÁC CẶP CÓ NẾN 4H NẰM NGOÀI DẢI BOLLINGER
        symbols_outside_4h_boll = []
        for symbol in LONG_LISTED_SYMBOLS:
            klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_4HOUR, limit=21)
            if len(klines) < 21: continue

            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            df['close'] = pd.to_numeric(df['close'])

            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['std_20'] = df['close'].rolling(window=20).std()
            df['upper_band'] = df['sma_20'] + (df['std_20'] * 2)
            df['lower_band'] = df['sma_20'] - (df['std_20'] * 2)

            last_candle = df.iloc[-1]
            if last_candle['close'] > last_candle['upper_band'] or last_candle['close'] < last_candle['lower_band']:
                symbols_outside_4h_boll.append(symbol)
                # print(f"  - 📈 Khung 4H: {symbol} có nến nằm ngoài dải Bollinger.")

        if not symbols_outside_4h_boll:
            print("Không tìm thấy cặp nào có nến 4H nằm ngoài dải Bollinger trong lần quét này.")
            return

        # 3. TỪ KẾT QUẢ BƯỚC 2, LỌC TIẾP VỚI KHUNG 15 PHÚT
        print("\n--- 🎯 KẾT QUẢ CUỐI CÙNG (Thỏa mãn 4H & 15M) ---")
        final_symbols = []
        for symbol in symbols_outside_4h_boll:
            klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=21)
            if len(klines) < 21: continue

            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            df['close'] = pd.to_numeric(df['close'])

            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['std_20'] = df['close'].rolling(window=20).std()
            df['upper_band'] = df['sma_20'] + (df['std_20'] * 2)
            df['lower_band'] = df['sma_20'] - (df['std_20'] * 2)

            last_candle = df.iloc[-1]
            if last_candle['close'] > last_candle['upper_band'] or last_candle['close'] < last_candle['lower_band']:
                final_symbols.append(symbol)
                print(f"  ✅ {symbol}")

        if not final_symbols:
            print("Không có cặp nào thỏa mãn điều kiện ở cả hai khung thời gian.")

    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình quét: {e}")

# --- LẬP LỊCH CHẠY ---
if __name__ == "__main__":
    # 1. Chạy cập nhật danh sách cặp giao dịch ngay lần đầu
    update_symbol_list()
    # Chạy quét lần đầu tiên ngay lập tức
    scan_bollinger_bands()

    # 2. Lập lịch cho các lần chạy tiếp theo
    schedule.every(24).hours.do(update_symbol_list)
    schedule.every(0.5).minutes.do(scan_bollinger_bands)

    print("\n🚀 Chương trình đã bắt đầu. Quét BB mỗi 5 phút và cập nhật danh sách cặp mỗi 24 giờ.")
    
    # 3. Vòng lặp chính để duy trì chương trình
    while True:
        schedule.run_pending()
        time.sleep(1)