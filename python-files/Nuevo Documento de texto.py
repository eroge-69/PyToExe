# Generate a Python script that uses Reddit's web interface to auto-subscribe to subreddits
# It will use Selenium to automate browser actions.

python_script_content = '''\
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep

# --- CONFIGURATION ---
USERNAME = "Nova-Foxet"
SUBREDDITS = [
    "anime", "anime_irl", "AskReddit", "Atlyss", "BBWHentai", "BlackMesa", "blueberrykink",
    "Boykisser3", "CartoonPorn", "CockVore", "cumflation_rp", "dbz", "DrStone", "fatfurs",
    "FatHentai", "FemboyHentai", "furry", "futanari", "HalfLife", "hammer", "HentaiAndRoleplayy",
    "hentairoleplay", "jerkbudsHentai", "JuJutsuKaisen", "learnprogramming", "loona_nsfw",
    "Needafriend", "Nipple_Fuck", "OKbuddyHalfLife", "pcmasterrace", "Portal", "programming",
    "Redteamtf2", "Steam", "StuffersNSFW", "TeamFortress2", "tf2", "thinkpad", "transfurs",
    "valve", "Vore", "wallpaperengine", "windowsxp"
]

# --- SETUP SELENIUM ---
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)

print("Launching browser...")
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.reddit.com/login/")

print("Please log in manually as user: " + USERNAME)
input("Press ENTER after you have logged in...")

# --- SUBSCRIBE TO SUBREDDITS ---
for sub in SUBREDDITS:
    url = f"https://www.reddit.com/r/{sub}/"
    print(f"Visiting r/{sub}...")
    driver.get(url)
    sleep(4)  # wait for page to load

    try:
        join_button = driver.find_element(By.XPATH, "//button[contains(text(),'Join')]")
        join_button.click()
        print(f"Joined r/{sub}")
    except:
        print(f"Already joined or could not find Join button on r/{sub}")

    sleep(2)

print("✅ Done subscribing to all subreddits.")
'''

path_py = "/mnt/data/reddit_auto_subscribe.py"
with open(path_py, "w", encoding="utf-8") as f:
    f.write(python_script_content)

path_py
