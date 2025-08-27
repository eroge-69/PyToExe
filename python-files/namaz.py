# Libraries
from bs4 import BeautifulSoup
import requests

scraped_Page = requests.get('https://namazvakitleri.diyanet.gov.tr/tr-TR/9541/istanbul-icin-namaz-vakti')
if scraped_Page == None:
    input("İnternet bağlantısı yok, çıkmak için ENTER'a basınız.")
    exit()

soup = BeautifulSoup(scraped_Page.text, 'html.parser')

header = soup.find_all(lambda tag: tag.name == 'div' and tag.has_attr('data-vakit-name'))

for i in header:
    print(i['data-vakit-name'], end=' ')
    print(i.find('div', {'class': 'tpt-time'}).text.strip())