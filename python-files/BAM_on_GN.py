import os
import time
import random
import requests
from bs4 import BeautifulSoup

# (c) Stefanmo August 4, 2025 - for Business AM
# Get terminal size
try:
    columns, rows = os.get_terminal_size()
except OSError:
    columns, rows = 80, 24  # Default size if terminal size can't be retrieved

# Define unique characters from "stefanmo", "efficientica", and "maximus"
all_letters = "stefanmoefficienticamaximus".lower()
chars = list(set(all_letters))  # ['a', 'c', 'e', 'f', 'i', 'm', 'n', 'o', 's', 't', 'u', 'x']

# Initialize each column as a list of spaces
column_lists = [[' ' for _ in range(rows)] for _ in range(columns)]

for _ in range(45):
    # Clear screen and move cursor to top-left
    print("\033[H\033[J", end="")
    # Print current state with green color
    for i in range(rows):
        row_str = ''.join(column_lists[j][i] for j in range(columns))
        print("\033[32m" + row_str + "\033[0m")
    # Update columns
    for j in range(columns):
        # Shift characters down: remove top, add space at bottom
        column_lists[j] = column_lists[j][1:] + [' ']
        # With 5% probability, add a random character at the top
        if random.random() < 0.05:
            column_lists[j][0] = random.choice(chars)
        # Randomly change some characters (1% chance) for flickering effect
        for i in range(1, rows):
            if random.random() < 0.01:
                column_lists[j][i] = random.choice(chars)
    # Pause briefly to control animation speed
    time.sleep(0.1)

def extract_titles(url, text_phrases):
    """
    Fetches the webpages from Google News and extracts article titles that contain
    the specified text phrase in their aria-label attribute.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}. Status code: {response.status_code}")
        return set()

    soup = BeautifulSoup(response.text, 'html.parser')
    title_elements = soup.find_all('a', attrs={"aria-label": True})
    titles = set()

    for elem in title_elements:
        text = elem['aria-label'].strip()
        if any(phrase.lower() in text.lower() and text.lower() != phrase.lower() for phrase in text_phrases):
            titles.add(text)

    return titles

# List of sites with their details
sites = [
    {
        "name": "Google News België - Rubriek België",
        "url": "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNREUxTkdvU0FtNXNLQUFQAQ?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News België - Rubriek Wereld",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtNXNHZ0pDUlNnQVAB?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News België - Rubriek Locaal",
        "url": "https://news.google.com/topics/CAAqHAgKIhZDQklTQ2pvSWJHOWpZV3hmZGpJb0FBUAE/sections/CAQiUENCSVNOam9JYkc5allXeGZkakpDRUd4dlkyRnNYM1l5WDNObFkzUnBiMjV5Q3hJSkwyMHZNREUwTldZeGVnc0tDUzl0THpBeE5EVm1NU2dBKjEIACotCAoiJ0NCSVNGem9JYkc5allXeGZkako2Q3dvSkwyMHZNREUwTldZeEtBQVABUAE?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News België - Rubriek Zakelijk",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtNXNHZ0pDUlNnQVAB?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News België - Rubriek Wetenschap en techniek",
        "url": "https://news.google.com/topics/CAAqKAgKIiJDQkFTRXdvSkwyMHZNR1ptZHpWbUVnSnViQm9DUWtVb0FBUAE?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News België - Rubriek Amusement",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtNXNHZ0pDUlNnQVAB?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News België - Rubriek Sport",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtNXNHZ0pDUlNnQVAB?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News België - Rubriek Gezondheid",
        "url": "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtNXNLQUFQAQ?hl=nl&gl=BE&ceid=BE%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    # Nederland
    {
        "name": "Google News Nederland - Rubriek Nederland",
        "url": "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRFU1YWpJU0FtNXNLQUFQAQ?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News Nederland - Rubriek Wereld",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtNXNHZ0pPVENnQVAB?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News Nederland - Rubriek Locaal",
        "url": "https://news.google.com/topics/CAAqHAgKIhZDQklTQ2pvSWJHOWpZV3hmZGpJb0FBUAE/sections/CAQiUENCSVNOam9JYkc5allXeGZkakpDRUd4dlkyRnNYM1l5WDNObFkzUnBiMjV5Q3hJSkwyMHZNREUwTldZeGVnc0tDUzl0THpBeE5EVm1NU2dBKjEIACotCAoiJ0NCSVNGem9JYkc5allXeGZkako2Q3dvSkwyMHZNREUwTldZeEtBQVABUAE?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News Nederland - Rubriek Zakelijk",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtNXNHZ0pPVENnQVAB?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News Nederland - Rubriek Wetenschap en technologie",
        "url": "https://news.google.com/topics/CAAqKAgKIiJDQkFTRXdvSkwyMHZNR1ptZHpWbUVnSnViQm9DVGt3b0FBUAE?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News Nederland - Rubriek Amusement",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtNXNHZ0pPVENnQVAB?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News Nederland - Rubriek Sport",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtNXNHZ0pPVENnQVAB?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
    {
        "name": "Google News Nederland - Rubriek Gezondheid",
        "url": "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtNXNLQUFQAQ?hl=nl&gl=NL&ceid=NL%3Anl",
        "text_phrases": ("Business AM","Niels Saelens","Florian Callens","Jennifer Mertens")
    },
]

# Loop through each site and print the titles
for site in sites:
    print("-------------")
    print(f"Titles from {site['name']}:")
    print("-------------")
    print("")
    titles = extract_titles(site['url'], site['text_phrases'])
    if titles:
        for title in sorted(titles):  # Sort for consistent output
            print("--> ",title)
            print("")
    else:
        print("No recent Business AM articles.")
    print("")