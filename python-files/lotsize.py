Python 3.12.1 (tags/v3.12.1:2305ca5, Dec  7 2023, 22:03:25) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> def calcola_lotsize(handles, rischio_euro, cambio_eur_usd):
...     rischio_usd = rischio_euro / cambio_eur_usd
...     lotsize = rischio_usd / handles
...     return round(lotsize, 2)
... 
... def main():
...     print("Calcolo LotSize per US100.cash")
... 
...     # Inserimento dati
...     handles = float(input("Inserisci gli handles di stop loss (es. 30): "))
...     cambio = float(input("Inserisci il cambio EUR/USD attuale (es. 1.09): "))
... 
...     rischio_100 = calcola_lotsize(handles, 100, cambio)
...     rischio_50 = calcola_lotsize(handles, 50, cambio)
... 
...     print(f"\n📊 Per {handles} handles di stop:")
...     print(f"🔹 Lot size per rischiare 100€: {rischio_100} lotti")
...     print(f"🔹 Lot size per rischiare 50€:  {rischio_50} lotti")
... 
... if __name__ == "__main__":
...     main()
