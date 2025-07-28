
import requests
from bs4 import BeautifulSoup
import csv
import time
import itertools

BASE_URL = "https://usatranscar.com"
CALCULATOR_URL = f"{BASE_URL}/site/public-calculator"
PORT_LIST_URL = f"{BASE_URL}/ru/site/port-arrival-list"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_port_ids(country_id, country_tab):
    url = f"{PORT_LIST_URL}?id={country_id}&tab={country_tab}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    options = soup.select("select[name='port'] option")
    return [(opt["value"], opt.text.strip()) for opt in options if opt.get("value")]

auctions = [
    "copart", "iaai", "manheim", "canada", "sublot copart", "sublot iaai"
]
delivery_methods = ["container", "ro-ro", "consolidated"]
insurance_options = ["yes", "no"]
drobilka_options = ["yes", "no"]

car_type = "sedan"

countries = {
    "Georgia": {"id": 3, "tab": "Georgia"},
    "Lithuania": {"id": 5, "tab": "Lithuania"}
}

results = []
print("Сбор данных начат...")
for country, data in countries.items():
    ports = get_port_ids(data["id"], data["tab"])
    for port_id, port_name in ports:
        for auction, delivery, insurance, drobilka in itertools.product(
            auctions, delivery_methods, insurance_options, drobilka_options
        ):
            payload = {
                "auction": auction,
                "car_type": car_type,
                "delivery_method": delivery,
                "port_id": port_id,
                "insurance": insurance,
                "drobilka": drobilka,
            }

            try:
                r = requests.post(CALCULATOR_URL, headers=headers, data=payload, timeout=10)
                if r.status_code == 200 and r.text.strip():
                    try:
                        price = r.json()
                        results.append([
                            country, port_name, port_id, auction,
                            delivery, insurance, drobilka, price
                        ])
                        print(f"[✓] {country} {port_name} - {auction}: {price}")
                    except:
                        continue
            except Exception:
                continue
            time.sleep(0.5)

filename = "usatranscar_prices_sedan.csv"
with open(filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Country", "Port Name", "Port ID", "Auction", "Delivery", "Insurance", "Drobilka", "Price"])
    writer.writerows(results)

print(f"\n✅ Готово! Данные сохранены в файл: {filename}")
input("Нажмите Enter для выхода...")
