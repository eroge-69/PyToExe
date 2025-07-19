
import requests
from bs4 import BeautifulSoup

def get_latest_epubs(url="https://epubbangla.in"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    print("\n🔍 Latest EPUB Books Found:\n" + "-"*40)

    for post in soup.find_all("h2", class_="post-title"):
        title = post.get_text(strip=True)
        link = post.find('a')['href']
        if ".epub" in title.lower() or "epub" in title.lower():
            print(f"📘 {title}\n🔗 {link}\n")

if __name__ == "__main__":
    get_latest_epubs()
    input("\nPress Enter to exit...")
