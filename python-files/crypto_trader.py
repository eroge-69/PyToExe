import pandas as pd
import requests

def calcular_rsi(precos, periodo=14):
    delta = precos.diff()
    ganho = delta.where(delta > 0, 0)
    perda = -delta.where(delta < 0, 0)
    media_ganho = ganho.rolling(periodo).mean()
    media_perda = perda.rolling(periodo).mean()
    rs = media_ganho / media_perda
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def buscar_binance(symbol="BTCUSDT", interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    resp = requests.get(url)
    dados = resp.json()
    precos_fechamento = [float(candle[4]) for candle in dados]
    return pd.Series(precos_fechamento)

def buscar_coinbase(symbol="BTC-USD", granularity=300):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={granularity}"
    resp = requests.get(url)
    dados = resp.json()
    precos_fechamento = [float(candle[4]) for candle in reversed(dados)]
    return pd.Series(precos_fechamento)

def analisar_tendencia(precos):
    rsi = calcular_rsi(precos)
    media_curta = precos.rolling(5).mean().iloc[-1]
    media_longa = precos.rolling(15).mean().iloc[-1]
    if rsi > 50 and media_curta > media_longa:
        return f"Tendência de ALTA detectada! (RSI={rsi:.2f})"
    elif rsi < 50 and media_curta < media_longa:
        return f"Tendência de BAIXA detectada! (RSI={rsi:.2f})"
    else:
        return f"Sem reversão clara. (RSI={rsi:.2f})"

def main():
    print("=== Analisador de Criptomoedas (Binance / Coinbase) ===")
    exchange = input("Escolha a exchange (binance/coinbase): ").strip().lower()
    if exchange == "binance":
        symbol = input("Digite o par (ex.: BTCUSDT): ").strip().upper()
        precos = buscar_binance(symbol)
    elif exchange == "coinbase":
        symbol = input("Digite o par (ex.: BTC-USD): ").strip().upper()
        precos = buscar_coinbase(symbol)
    else:
        print("Exchange inválida.")
        return
    
    if precos.empty:
        print("Erro: não foi possível obter dados.")
        return
    
    resultado = analisar_tendencia(precos)
    print("\nResultado:", resultado)

if __name__ == "__main__":
    main()
