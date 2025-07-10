from iqoptionapi.stable_api import IQ_Option
import time
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO ---
EMAIL = "maquinaemerson@gmail.com"
SENHA = "1207aguia"
PAR = "EURUSD"
TIMEFRAME = 1  # minutos
VALOR_INICIAL = 2.0
SOROS_NIVEL = 3

# --- CONECTANDO ---
print("Conectando à IQ Option...")
I_want_money = IQ_Option(EMAIL, SENHA)
I_want_money.connect()
I_want_money.change_balance("practice")  # Modo demo

if I_want_money.check_connect():
    print("Conectado com sucesso!")
else:
    print("Erro ao conectar. Verifique seu login.")
    exit()

# --- FUNÇÕES DE INDICADORES ---
def get_candles():
    candles = I_want_money.get_candles(PAR, 60, 100, time.time())
    df = pd.DataFrame(candles)
    df['close'] = df['close'].astype(float)
    df['EMA5'] = df['close'].ewm(span=5).mean()
    df['EMA20'] = df['close'].ewm(span=20).mean()
    df['RSI'] = compute_rsi(df['close'])
    df['MACD'], df['MACD_signal'] = compute_macd(df['close'])
    return df

def compute_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(data, short=12, long=26, signal=9):
    ema_short = data.ewm(span=short).mean()
    ema_long = data.ewm(span=long).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line

# --- ESTRATÉGIA ---
def analisar(df):
    ultima = df.iloc[-1]
    penultima = df.iloc[-2]

    call = (penultima['EMA5'] < penultima['EMA20'] and
            ultima['EMA5'] > ultima['EMA20'] and
            ultima['RSI'] < 70 and
            penultima['MACD'] < penultima['MACD_signal'] and
            ultima['MACD'] > ultima['MACD_signal'])

    put = (penultima['EMA5'] > penultima['EMA20'] and
           ultima['EMA5'] < ultima['EMA20'] and
           ultima['RSI'] > 30 and
           penultima['MACD'] > penultima['MACD_signal'] and
           ultima['MACD'] < ultima['MACD_signal'])

    if call:
        return "call"
    elif put:
        return "put"
    else:
        return None

# --- EXECUÇÃO DE ORDENS ---
def entrar_digital(direcao, valor):
    status, id = I_want_money.buy_digital_spot(PAR, valor, direcao, TIMEFRAME)
    if status:
        print(f"Entrada: {direcao.upper()} | Valor: {valor}")
        while True:
            status, lucro = I_want_money.check_win_digital_v2(id)
            if status:
                print(f"Resultado: {'WIN' if lucro > 0 else 'LOSS'} | Lucro: {lucro}")
                return lucro
            time.sleep(1)
    else:
        print("Erro ao enviar ordem.")
        return 0

# --- LOOP PRINCIPAL COM SOROS ---
nivel = 1
valor = VALOR_INICIAL

while True:
    print(f"\nAnalisando mercado... (Nível Soros: {nivel})")
    df = get_candles()
    direcao = analisar(df)

    if direcao:
        lucro = entrar_digital(direcao, round(valor, 2))
        if lucro > 0:
            nivel += 1
            valor = lucro
            if nivel > SOROS_NIVEL:
                print("Ciclo Soros concluído. Reiniciando valor.")
                nivel = 1
                valor = VALOR_INICIAL
        else:
            print("Perda. Reiniciando Soros.")
            nivel = 1
            valor = VALOR_INICIAL
    else:
        print("Sem sinal válido.")

    time.sleep(60)  # Espera novo candle
