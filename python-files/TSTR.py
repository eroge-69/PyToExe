import time
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import concurrent.futures
import logging
import argparse
import sys

# --------------------------- Config ---------------------------------
DEFAULT_TOP_N = 500          # en çok işlem gören kaç hisseyi tarayalım
INTERVAL = "1m"              # 1 dakikalık mumlar
LOOKBACK = 20                # ortalama için bakılacak mum sayısı
SPIKE_FACTOR = 3.5           # hacim ortalamanın kaç katı olursa uyarı
FETCH_TIMEOUT = 15           # saniye (web isteği)
WORKERS = 8                  # aynı anda kaç hisseyi kontrol etsin
SLEEP_BETWEEN_CYCLES = 60    # her turdan sonra bekleme süresi
OUTPUT_CSV = "volume_spikes.csv"

# ------------------------ Logging setup -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("vol_spike_scanner")

# ------------------------ Helpers ----------------------------------
def fetch_most_active(top_n=DEFAULT_TOP_N):
    """Yahoo Finance 'most active' sayfasından en aktif hisseleri alır"""
    url = "https://finance.yahoo.com/most-active"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=FETCH_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    if not table:
        logger.error("Yahoo sayfasında tablo bulunamadı")
        return []

    tickers = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 2:
            sym = cols[0].get_text(strip=True)
            tickers.append(sym)
        if len(tickers) >= top_n:
            break
    logger.info(f"{len(tickers)} most-active hisse bulundu")
    return tickers


def check_volume_spike(symbol):
    """1 dakikalık verilerden hacim patlaması kontrolü yapar"""
    try:
        period_minutes = max(60, (LOOKBACK + 5) * 1)
        period = f"{period_minutes}m"
        df = yf.download(symbol, period=period, interval=INTERVAL, progress=False, threads=False)
        if df is None or df.empty or "Volume" not in df.columns:
            return None

        if len(df) < LOOKBACK + 1:
            return None

        avg_vol = df["Volume"].iloc[-(LOOKBACK+1):-1].mean()
        last_vol = df["Volume"].iloc[-1]
        last_close = df["Close"].iloc[-1]

        if avg_vol <= 0:
            return None

        spike_ratio = float(last_vol) / float(avg_vol)
        if spike_ratio >= SPIKE_FACTOR:
            return {
                "symbol": symbol,
                "last_close": float(last_close),
                "last_volume": int(last_vol),
                "avg_volume": float(avg_vol),
                "spike_ratio": spike_ratio,
                "time": df.index[-1].to_pydatetime()
            }
        return None
    except Exception as e:
        logger.debug(f"{symbol} için hata: {e}")
        return None

# ------------------------ Main loop --------------------------------
def main(args):
    top_n = args.top_n
    logger.info("Volume Spike Scanner başlatıldı")

    spikes_df = pd.DataFrame(columns=["time", "symbol", "last_close", "last_volume", "avg_volume", "spike_ratio"]) 

    while True:
        start = time.time()
        tickers = fetch_most_active(top_n=top_n)
        if not tickers:
            logger.error("Hisse bulunamadı — 60s bekleniyor")
            time.sleep(60)
            continue

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as exe:
            futures = {exe.submit(check_volume_spike, t): t for t in tickers}
            for fut in concurrent.futures.as_completed(futures):
                res = fut.result()
                if res:
                    results.append(res)

        if results:
            logger.info(f"Bu turda {len(results)} spike bulundu")
            for r in results:
                logger.info(
                    "🚨 {symbol} | Zaman={time} | Fiyat={last_close:.2f} | "
                    "Hacim={last_volume} | Ort={avg_volume:.0f} | x={spike_ratio:.2f}".format(**r)
                )
                spikes_df = spikes_df.append({
                    "time": r["time"],
                    "symbol": r["symbol"],
                    "last_close": r["last_close"],
                    "last_volume": r["last_volume"],
                    "avg_volume": r["avg_volume"],
                    "spike_ratio": r["spike_ratio"]
                }, ignore_index=True)

            try:
                spikes_df.to_csv(OUTPUT_CSV, index=False)
            except Exception:
                logger.exception("CSV yazılamadı")
        else:
            logger.info("Spike bulunamadı")

        took = time.time() - start
        sleep_for = max(1, SLEEP_BETWEEN_CYCLES - took)
        logger.info(f"Tur süresi {took:.1f}s — uyku {sleep_for:.1f}s")
        time.sleep(sleep_for)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Volume spike scanner (most-active subset)")
    parser.add_argument("--top_n", type=int, default=DEFAULT_TOP_N, help="Kaç most-active hisse taransın")
    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        logger.info("Scanner kullanıcı tarafından durduruldu")