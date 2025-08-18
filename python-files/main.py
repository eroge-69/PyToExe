
import requests
from bs4 import BeautifulSoup

url = "http://www.parrocchiemonta.it/defunti/"

try:
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
except requests.exceptions.RequestException as e:
    print(f"Errore durante il recupero della pagina: {e}")
    exit()

soup = BeautifulSoup(html_content, 'html.parser')

# Esempio: estrarre tutti i paragrafi con classe 'testo-importante'
paragrafi = soup.find_all('p', class_='testo-importante')

for paragrafo in paragrafi:
    print(paragrafo.text)