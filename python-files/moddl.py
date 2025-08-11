import requests

# Workshop mod ID for Gold's Interior Asset Pack 1
MOD_ID = "3537050324"

# Workshop downloader API endpoint (mirror)
DOWNLOAD_URL = f"https://backend-01-prd.steamworkshopdownloader.io/api/download/item/{MOD_ID}"

# Output filename
OUTPUT_FILE = f"{MOD_ID}.zip"

print(f"Downloading mod {MOD_ID}...")

# Request the file
response = requests.get(DOWNLOAD_URL, stream=True)

if response.status_code == 200:
    with open(OUTPUT_FILE, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"✅ Download complete! Saved as {OUTPUT_FILE}")
else:
    print(f"❌ Failed to download mod. Status code: {response.status_code}")
