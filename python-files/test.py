import requests
from bs4 import BeautifulSoup
import os

# URL of the ROMs page
url = 'https://romsretro.com/roms/3ds-cia/'

# Create a directory to save the downloaded ROMs
if not os.path.exists('roms'):
    os.makedirs('roms')

# Send a request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all links to ROM files
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        # Check if the link ends with .cia (ROM file type)
        if href.endswith('.cia'):
            # Get the full URL
            full_url = href if href.startswith('http') else url + href
            print(f'Downloading {full_url}')
            # Download the ROM file
            rom_response = requests.get(full_url)
            rom_filename = os.path.join('roms', href.split('/')[-1])
            with open(rom_filename, 'wb') as rom_file:
                rom_file.write(rom_response.content)
                print(f'Saved {rom_filename}')
else:
    print('Failed to retrieve the webpage')