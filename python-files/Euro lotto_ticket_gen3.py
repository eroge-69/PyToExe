import requests
from bs4 import BeautifulSoup
import random

URL = "https://www.euro-millions.com/statistics"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

# Get all tables
tables = soup.find_all("table")
main_table = tables[0]
star_table = tables[1]

# Extract main numbers
main_numbers = []
for row in main_table.find_all("tr")[1:]:  # skip header
    cols = row.find_all("td")
    if cols:
        number = cols[0].text.strip()
        if number.isdigit():
            main_numbers.append(int(number))

# Extract Lucky Stars
star_numbers = []
for row in star_table.find_all("tr")[1:]:
    cols = row.find_all("td")
    if cols:
        number = cols[0].text.strip()
        if number.isdigit():
            star_numbers.append(int(number))

def generate_ticket():
    main_pick = random.sample(main_numbers, 5)
    stars_pick = random.sample(star_numbers, 2)
    return sorted(main_pick), sorted(stars_pick)

# Generate 5 tickets
if __name__ == "__main__":
    for i in range(15):
        main, stars = generate_ticket()
        print(f"Ticket {i+1}: Main numbers {main} + Stars {stars}")
