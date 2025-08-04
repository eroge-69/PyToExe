
import requests
import pandas as pd

# Klucz API BaseLinker
API_KEY = "7494-13865-V8581GW21FTNO0JKU3RT0MZE8WEGTIY9UFTQ8ADGSJWQTCV475WYD2KTA2LCAHIX"

# Wczytaj dane z formularza WordPress (CSV)
csv_filename = "wpforms-355-Kreator-Proporca-MDP-entry-152.csv"
df = pd.read_csv(csv_filename)
row = df.iloc[0]  # Przetwarza tylko pierwszy wpis

# Zbuduj payload JSON dla API BaseLinker
payload = {
    "method": "addOrder",
    "parameters": {
        "external_order_id": f"PROP-{row['Identyfikator wpisu']}",
        "email": row["Adres e-mail"],
        "phone": row["☎️Telefon"],
        "delivery_fullname": row["Imię Nazwisko"],
        "delivery_address": f"{row['Adres dostawy📦: Adres, wiersz 1']} {row['Adres dostawy📦: Adres, wiersz 2']}".strip(),
        "delivery_postcode": row["Adres dostawy📦: Kod pocztowy"],
        "delivery_city": row["Adres dostawy📦: Miejscowość"],
        "delivery_country_code": "PL",
        "invoice_nip": row["NIP jednostki 🚒"],
        "invoice_fullname": row["Imię Nazwisko"],
        "invoice_address": f"{row['Adres dostawy📦: Adres, wiersz 1']} {row['Adres dostawy📦: Adres, wiersz 2']}".strip(),
        "invoice_postcode": row["Adres dostawy📦: Kod pocztowy"],
        "invoice_city": row["Adres dostawy📦: Miejscowość"],
        "invoice_country_code": "PL",
        "products": [
            {
                "name": "Zamówienie proporca MDP",
                "quantity": 1,
                "price_brutto": 0
            }
        ]
    }
}

# Wywołanie API BaseLinkera
response = requests.post(
    "https://api.baselinker.com/connector.php",
    headers={"X-BLToken": API_KEY},
    json=payload
)

# Wynik odpowiedzi z API
print("Status:", response.status_code)
print("Odpowiedź:", response.json())
