import requests, re, time, os
from bs4 import BeautifulSoup
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

GREEN = '\033[38;2;123;255;0m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

# ------------------ Global Download Tracker ------------------ #
downloaded_episodes = []
total_downloaded_size = 0

# ------------------ Core Functions ------------------ #

def extract_episode_links(show_url, target_class="se-a"):
    soup = BeautifulSoup(requests.get(show_url).text, "html.parser")
    links = [a["href"] for e in soup.find_all(class_=target_class) for a in e.find_all("a", href=True)]
    grouped = defaultdict(list)
    for link in links:
        m = re.search(r"(\d+)x(\d+)", link)
        if m:
            season, ep = int(m.group(1)), int(m.group(2))
            grouped[season].append((ep, link))
    return {s: [u for _, u in sorted(grouped[s])] for s in grouped}

def get_real_mp4_url(page_url):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=opts)
    driver.get(page_url)
    try:
        driver.find_element("id", "clickfakeplayer").click()
        time.sleep(5)
    except:
        pass
    urls = []
    for v in driver.find_elements("tag name", "video"):
        if v.get_attribute("src") and v.get_attribute("src").endswith(".mp4"):
            urls.append(v.get_attribute("src"))
        for s in v.find_elements("tag name", "source"):
            if s.get_attribute("src") and s.get_attribute("src").endswith(".mp4"):
                urls.append(s.get_attribute("src"))
    driver.quit()
    return list(set(urls))

def download_video(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 KB

    # Bar format: thin green bar + colorful info
    bar_format = (
        f"{GREEN}{{l_bar}}{RESET}{{bar}}{GREEN}|{RESET} "
        f"{CYAN}{{n_fmt}}{RESET}/{YELLOW}{{total_fmt}}{RESET} "
        f"[{MAGENTA}{{elapsed}}{RESET}<{MAGENTA}{{remaining}}{RESET}, "
        f"{CYAN}{{rate_fmt}}{RESET}]"
    )

    progress = tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        desc=filename,
        ncols=80,
        bar_format=bar_format,
        colour="#7bff00"
    )

    with open(filename, "wb") as f:
        for data in response.iter_content(block_size):
            f.write(data)
            progress.update(len(data))
    progress.close()
    return total_size


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------ Terminal App ------------------ #

def display_menu():
    print("\n=== AOT Downloader ===")
    print("1. Download entire season")
    print("2. Download specific episode range")
    print("3. Download single episode")
    print("0. Exit")
    return input("Select option: ")

def get_user_choice(max_season, grouped):
    season = int(input(f"Enter season (1-{max_season}): "))
    if season not in grouped:
        print("❌ Season not found!")
        return None
    return season

def download_episodes(grouped, season, start_ep=1, end_ep=None):
    global downloaded_episodes, total_downloaded_size

    episodes = grouped[season]
    if end_ep is None:
        end_ep = len(episodes)

    for i, ep_url in enumerate(episodes, start=1):
        if i < start_ep or i > end_ep:
            continue

        print(f"\n⬇️  Downloading Season {season} Ep {i:02d}")
        links = get_real_mp4_url(ep_url)
        if links:
            mp4 = links[0]
            filename = f"Season{season}_Ep{i:02d}.mp4"
            size = download_video(mp4, filename)
            downloaded_episodes.append(filename)
            total_downloaded_size += size
            print(f"✅ Completed {filename}")
        else:
            print(f"❌ No link found for Season {season} Ep {i:02d}")

    # Clear terminal and show **full session summary**
    clear_terminal()
    print("=== Download Summary ===")
    for f in downloaded_episodes:
        print(f"  {f}")
    print(f"\n📊 Total episodes downloaded: {len(downloaded_episodes)}")
    print(f"📦 Total data downloaded: {total_downloaded_size / (1024*1024):.2f} MB")

# ------------------ Main App ------------------ #

def main():
    show_url = "https://slanimeclub.co/tvshows/attack-on-titan/"
    grouped = extract_episode_links(show_url)
    max_season = max(grouped.keys())

    while True:
        choice = display_menu()
        if choice == "0":
            print("Exiting...")
            break
        elif choice == "1":  # Entire season
            season = get_user_choice(max_season, grouped)
            if season:
                download_episodes(grouped, season)
        elif choice == "2":  # Episode range
            season = get_user_choice(max_season, grouped)
            if season:
                start_ep = int(input("Enter start episode: "))
                end_ep = int(input("Enter end episode: "))
                download_episodes(grouped, season, start_ep, end_ep)
        elif choice == "3":  # Single episode
            season = get_user_choice(max_season, grouped)
            if season:
                ep = int(input("Enter episode number: "))
                download_episodes(grouped, season, ep, ep)
        else:
            print("❌ Invalid choice, try again.")

if __name__ == "__main__":
    main()
