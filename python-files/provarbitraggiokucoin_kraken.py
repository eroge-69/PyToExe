import ccxt
import time

# Inizializza connessioni agli exchange
kucoin = ccxt.kucoin()
kraken = ccxt.kraken()

# Coppia di trading da monitorare
symbol = 'DOT/USDT'  # Su Kraken potrebbe essere DOT/USD

while True:
    try:
        # Prezzo su KuCoin
        ticker_kucoin = kucoin.fetch_ticker(symbol)
        prezzo_kucoin = ticker_kucoin['last']
        # Prezzo su Kraken
        ticker_kraken = kraken.fetch_ticker(symbol)
        prezzo_kraken = ticker_kraken['last']
        # Differenza di prezzo
        differenza = prezzo_kucoin - prezzo_kraken
        percentuale_diff = (differenza / prezzo_kraken) * 100
        # Output
        print(f"\n--- Monitoraggio DOT ---")
        print(f"KuCoin: {prezzo_kucoin:.4f} USDT")
        print(f"Kraken: {prezzo_kraken:.4f} USDT")
        print(f"Differenza: {differenza:.4f} USDT ({percentuale_diff:.2f}%)")

        # Attendi qualche secondo
        time.sleep(5)
    except Exception as e:
        print(f"Errore: {e}")
        time.sleep(5)



