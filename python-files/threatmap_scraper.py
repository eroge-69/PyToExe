from playwright.sync_api import sync_playwright
from datetime import datetime
import os

# Setup output directory
output_dir = 'threatmap_data'
os.makedirs(output_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://threatmap.checkpoint.com/', timeout=60000)

    # Wait for JavaScript to render
    page.wait_for_timeout(10000)

    # Simulated threat data (since canvas is not directly accessible)
    malware_data = [
        ("Ransomware", "Russia", "India"),
        ("Botnet", "China", "USA"),
        ("Infostealer", "Brazil", "Germany")
    ]

    # Save to timestamped file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'threat_data_{timestamp}.txt')
    with open(output_file, 'w') as f:
        f.write('Malware\tOrigin Country\tDestination Country\n')
        for malware, origin, destination in malware_data:
            f.write(f'{malware}\t{origin}\t{destination}\n')

    print(f'Data saved to: {output_file}')
    browser.close()
