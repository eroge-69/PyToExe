import ccxt
import time

# Inizializza connessioni agli exchange
kraken = ccxt.kraken()
kucoin = ccxt.kucoin()

# Coppia di trading da monitorare
symbol = 'DOT/USDT'  # Su Kraken può essere anche 'DOT/USD'

while True:
    try:
        # Prezzo su Kraken
        ticker_kraken = kraken.fetch_ticker(symbol)
        prezzo_kraken = ticker_kraken['last']

        # Prezzo su KuCoin
        ticker_kucoin = kucoin.fetch_ticker(symbol)
        prezzo_kucoin = ticker_kucoin['last']

        # Differenza di prezzo
        differenza = prezzo_kraken - prezzo_kucoin
        percentuale_diff = (differenza / prezzo_kucoin) * 100

        # Output
        print(f"\n--- Monitoraggio DOT ---")
        print(f"Kraken: {prezzo_kraken:.4f} USDT")
        print(f"KuCoin: {prezzo_kucoin:.4f} USDT")
        print(f"Differenza: {differenza:.4f} USDT ({percentuale_diff:.2f}%)")

        # Attendi qualche secondo
        time.sleep(5)

    except Exception as e:
        print(f"Errore: {e}")
        time.sleep(5)
