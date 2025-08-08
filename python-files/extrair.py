import requests
from bs4 import BeautifulSoup
import time

url = "https://www.pwnrank.com/top-500"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

rows = soup.find_all('tr')

with open("top500.txt", "w", encoding="utf-8") as f:
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2:
            pos = cells[0].get_text(strip=True)
            name = cells[1].get_text(strip=True)
            f.write(f"{pos}\t{name}\n")
        time.sleep(0.05)  # pequena pausa

print("✅ Arquivo top500.txt salvo com sucesso!")
