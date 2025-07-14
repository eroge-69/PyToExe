import os
import requests

# Folder to save images
save_folder = "propatria_images"
os.makedirs(save_folder, exist_ok=True)

# Range of years
start_year = 1923
end_year = 2025

# Base URL format
base_url = "https://propatria.ch/wp-content/uploads/{}.jpg"

# Download loop
for year in range(start_year, end_year + 1):
    url = base_url.format(year)
    filename = os.path.join(save_folder, f"{year}.jpg")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {year}.jpg")
        else:
            print(f"Not found: {year}.jpg (Status code: {response.status_code})")
    except requests.RequestException as e:
        print(f"Error downloading {year}.jpg: {e}")
