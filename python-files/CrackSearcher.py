from urllib.request import urlopen, Request
from urllib.parse import quote
import re
import time
from rich.progress import track
from rich import print, box
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
import os

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"

def fetch_html(url):
    """Fetch HTML content from the specified URL."""
    try:
        req = Request(url, headers={'User-Agent': user_agent})
        with urlopen(req) as response:
            html_bytes = response.read()
            return html_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"An error occurred while fetching HTML from {url}: {e}")
        return None

def fetch_html_content(query):
    """Fetch HTML content from the specified URLs based on the query."""
    encoded_url = quote(query)
    fit_url = "https://fitgirl-repacks.site/?s=" + encoded_url
    steamrip_url = "https://steamrip.com/?s=" + encoded_url
    gamebounty_url = "https://gamebounty.world/?s=" + encoded_url

    fit_html = fetch_html(fit_url)
    steamrip_html = fetch_html(steamrip_url)
    gamebounty_html = fetch_html(gamebounty_url)
    return fit_html, steamrip_html, gamebounty_html

def extract_links(html, base_url):
    """Extract links from the HTML content and prepend the base URL if necessary."""
    links = []
    if base_url == "https://fitgirl-repacks.site/":
        links = re.findall(r'<h1 class="entry-title"><a href="([^"]+)"', html)
    elif base_url == "https://steamrip.com/":
        links = re.findall(r'<a href="([^"]+)" class="all-over-thumb-link">', html)
        links = [f"{base_url}{link}" for link in links]
    elif base_url == "https://gamebounty.world/":
        links = re.findall(r'<a class="block h-full" href="([^"]+)">', html)
        links = [f"{base_url}{link}" for link in links]
    return links

def print_links(links, count):
    """Print the specified number of links in a panel."""
    if links:
        link_text = "\n".join(links[:count])
        panel = Panel.fit(Text(link_text, style="bold green"))
        print(panel)
    else:
        print("No links found.")

def main():
    """Main procedure to run the program."""
    panel = Panel.fit((Text("Scrivi cosa vuoi cercare", style="bold green")))
    print(panel)
    query = input(": ")
    panel = Panel.fit(Text("quanti link vuoi?", style="bold green"))
    print(panel)
    count = int(Prompt.ask(default="5"))
    print("\n")
    for i in track(range(3), description="Sto prendendo i link..."):
        fit_html, steamrip_html, gamebounty_html = fetch_html_content(query)
    if fit_html and steamrip_html and gamebounty_html:
        fitgirl_links = extract_links(fit_html, "https://fitgirl-repacks.site/")
        steamrip_links = extract_links(steamrip_html, "https://steamrip.com/")
        gamebounty_links = extract_links(gamebounty_html, "https://gamebounty.world/")

        print("\nFitgirl Links:")
        print_links(fitgirl_links, count)
        print("Steamrip Links:")
        print_links(steamrip_links, count)
        print("Gamebounty Links:")
        print_links(gamebounty_links, count)
    else:
        print("Failed to fetch URLs content.")
    input("premi invio per chiudere il programma\n")

if __name__ == "__main__":
    main()
