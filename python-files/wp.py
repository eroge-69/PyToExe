import os
import platform
import random
import requests
import schedule
import time
from datetime import datetime
from pathlib import Path

# ========== CONFIGURATION ==========
PEXELS_API_KEY = "gSbGxaq82X9cOezwAO5Da3aHZl2ANdtvWPH7WI9ZBOgbcpJhReBvnwJT"
IMAGE_TOPICS = ["nature", "space", "animals", "technology", "abstract", "landscape"]
DOWNLOAD_DIR = Path.home() / "Wallpapers"
CHANGE_INTERVAL_MINUTES = 1
# ===================================

HEADERS = {
    "Authorization": PEXELS_API_KEY
}
PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

def fetch_random_image():
    query = random.choice(IMAGE_TOPICS)
    params = {
        "query": query,
        "per_page": 15,
        "page": random.randint(1, 10)
    }

    print(f"[{datetime.now()}] Searching for: {query}")
    response = requests.get(PEXELS_SEARCH_URL, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch image: {response.status_code}")
        return None

    data = response.json()
    photos = data.get("photos")
    if not photos:
        print("No images found.")
        return None

    photo = random.choice(photos)
    image_url = photo["src"]["original"]
    return image_url

def download_image(image_url):
    if not DOWNLOAD_DIR.exists():
        DOWNLOAD_DIR.mkdir(parents=True)
    
    response = requests.get(image_url)
    if response.status_code == 200:
        filename = DOWNLOAD_DIR / f"wallpaper_{int(time.time())}.jpg"
        with open(filename, "wb") as f:
            f.write(response.content)
        return str(filename)
    return None

def set_wallpaper(image_path):
    os_type = platform.system()

    if os_type == "Windows":
        import ctypes
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

    elif os_type == "Darwin":  # macOS
        script = f'''
        osascript -e 'tell application "System Events" to set picture of every desktop to "{image_path}"'
        '''
        os.system(script)

    elif os_type == "Linux":
        # This is for GNOME
        os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{image_path}")

    else:
        print(f"Unsupported OS: {os_type}")

def change_wallpaper():
    print(f"[{datetime.now()}] Changing wallpaper...")
    image_url = fetch_random_image()
    if image_url:
        image_path = download_image(image_url)
        if image_path:
            set_wallpaper(image_path)
            print(f"Wallpaper changed: {image_path}")
        else:
            print("Failed to download image.")
    else:
        print("No image URL fetched.")

# Schedule the job
schedule.every(CHANGE_INTERVAL_MINUTES).minutes.do(change_wallpaper)

# Initial call
change_wallpaper()

# Loop
print("Wallpaper changer is running. Press Ctrl+C to stop.")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting.")
