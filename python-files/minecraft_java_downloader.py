import requests
from bs4 import BeautifulSoup
import re

def get_game_links(game_name):
    query = f"{game_name} site:mediafire.com OR site:mega.nz OR site:drive.google.com"
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract links
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        match = re.search(r"(https?:\/\/(?:www\.)?(mediafire|mega|drive)\.com[^\s]*)", href)
        if match:
            clean_link = match.group(1)
            if clean_link not in links:
                links.append(clean_link)

    return links

# Example usage
game_name = "Minecraft Java Edition"
print(f"🔍 Searching download links for: {game_name}\n")
download_links = get_game_links(game_name)

if download_links:
    for idx, link in enumerate(download_links, 1):
        print(f"{idx}. {link}")
else:
    print("❌ No download links found. Try a different game name or check your internet.")
