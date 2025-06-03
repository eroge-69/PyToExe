Python 3.13.4 (tags/v3.13.4:8a526ec, Jun  3 2025, 17:46:04) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import requests
... import matplotlib.pyplot as plt
... import pandas as pd
... import datetime
... import time
... from playsound import playsound
... 
... # === Configurações ===
... MOEDA = 'BTC-USD'
... MMS_CURTA = 9
... MMS_LONGA = 21
... INTERVALO = 60  # em segundos
... 
... def buscar_dados():
...     url = f"https://api.coinbase.com/v2/prices/{MOEDA}/spot"
...     resposta = requests.get(url)
...     dados = resposta.json()
...     valor = float(dados['data']['amount'])
...     return valor
... 
... def calcular_sinais(precos):
...     df = pd.DataFrame(precos, columns=['timestamp', 'preco'])
...     df['mma_curta'] = df['preco'].rolling(window=MMS_CURTA).mean()
...     df['mma_longa'] = df['preco'].rolling(window=MMS_LONGA).mean()
...     df['sinal'] = ''
...     
...     for i in range(1, len(df)):
...         if df['mma_curta'][i-1] < df['mma_longa'][i-1] and df['mma_curta'][i] > df['mma_longa'][i]:
...             df.at[i, 'sinal'] = 'COMPRA'
...             playsound('alerta_compra.mp3', block=False)
...         elif df['mma_curta'][i-1] > df['mma_longa'][i-1] and df['mma_curta'][i] < df['mma_longa'][i]:
...             df.at[i, 'sinal'] = 'VENDA'
...             playsound('alerta_venda.mp3', block=False)
...     return df
... 
... def exportar_para_csv(df):
...     df.to_csv('sinais_cripto.csv', index=False)
...     print("🔽 Sinais exportados para 'sinais_cripto.csv'.")
... 
... # === Execução principal ===
... precos = []
... 
... print("🟢 CriptoAlerta360 iniciado. A monitorizar", MOEDA)
... try:
...     while True:
...         preco = buscar_dados()
...         timestamp = datetime.datetime.now()
...         precos.append([timestamp, preco])
        print(f"[{timestamp.strftime('%H:%M:%S')}] Preço: {preco:.2f} USD")

        if len(precos) >= MMS_LONGA:
            df_sinais = calcular_sinais(precos)
            exportar_para_csv(df_sinais)
            
            plt.clf()
            plt.plot(df_sinais['timestamp'], df_sinais['preco'], label='Preço')
            plt.plot(df_sinais['timestamp'], df_sinais['mma_curta'], label='Média Curta')
            plt.plot(df_sinais['timestamp'], df_sinais['mma_longa'], label='Média Longa')
            plt.legend()
            plt.pause(0.1)

        time.sleep(INTERVALO)
except KeyboardInterrupt:
    print("⛔ Monitorização terminada.")
    exportar_para_csv(calcular_sinais(precos))
