import subprocess
import sys

# ---------------- Install required libraries ----------------
required = ["selenium", "pandas"]
for package in required:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# ---------------- Import after installation ----------------
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, filedialog

# ---------------- GUI ----------------
def start_scraping():
    query = search_query.get()
    num_channels = int(channel_count.get())
    output_file = output_name.get()

    if not query or not output_file:
        messagebox.showerror("Error", "Please fill all fields")
        return

    scrape_youtube(query, num_channels, output_file)

def scrape_youtube(SEARCH_QUERY, NUM_CHANNELS, OUTPUT_FILE):
    WAIT_TIME = 3
    INACTIVE_MONTHS = 6

    # ---------------- Setup Selenium ----------------
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)

    # ---------------- Open Search ----------------
    driver.get(f"https://www.youtube.com/results?search_query={SEARCH_QUERY.replace(' ', '+')}")
    time.sleep(WAIT_TIME)

    # ---------------- Scroll to Load More ----------------
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(WAIT_TIME)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height or len(driver.find_elements(By.XPATH, '//a[contains(@href, "/channel/")]')) >= NUM_CHANNELS:
            break
        last_height = new_height

    # ---------------- Collect Channel Links ----------------
    channel_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/channel/")]')
    channel_links = []
    for c in channel_elements:
        link = c.get_attribute("href")
        if link not in channel_links:
            channel_links.append(link)
        if len(channel_links) >= NUM_CHANNELS:
            break

    data = []

    # ---------------- Scrape Channel Info ----------------
    for idx, link in enumerate(channel_links):
        try:
            driver.get(link + "/about")
            time.sleep(WAIT_TIME)
            
            # Channel Name
            try:
                name_elem = driver.find_element(By.XPATH, '//yt-formatted-string[@id="text" or @class="style-scope ytd-channel-name"]')
                channel_name = name_elem.text
            except:
                channel_name = ""
            
            # Business Email
            try:
                email_elem = driver.find_element(By.XPATH, '//a[contains(@href, "mailto:")]')
                business_email = email_elem.get_attribute("href").replace("mailto:", "")
            except:
                business_email = ""
            
            # Subscribers
            try:
                subs_elem = driver.find_element(By.XPATH, '//yt-formatted-string[contains(@id,"subscriber-count")]')
                subs_count = subs_elem.text
            except:
                subs_count = ""
            
            # Last Upload
            driver.get(link + "/videos")
            time.sleep(WAIT_TIME)
            try:
                last_video_elem = driver.find_element(By.XPATH, '(//ytd-grid-video-renderer//span[@class="style-scope ytd-grid-video-renderer"])[1]')
                last_upload_text = last_video_elem.text
                if "month" in last_upload_text:
                    months = int(last_upload_text.split()[0])
                    last_upload_date = datetime.today() - timedelta(days=30*months)
                elif "year" in last_upload_text:
                    years = int(last_upload_text.split()[0])
                    last_upload_date = datetime.today() - timedelta(days=365*years)
                elif "week" in last_upload_text:
                    weeks = int(last_upload_text.split()[0])
                    last_upload_date = datetime.today() - timedelta(weeks=weeks)
                else:
                    last_upload_date = datetime.today()
            except:
                last_upload_text = ""
                last_upload_date = datetime.today() - timedelta(days=365*10)

            # Filter inactive channels
            if last_upload_date < datetime.today() - timedelta(days=30*INACTIVE_MONTHS):
                continue

            # Personalized outreach
            outreach_line = f"Hey {channel_name}, love your content! I can make a custom thumbnail for your next video to help increase clicks. Reply 'TEST' if you want a free sample."

            data.append({
                "Channel Name": channel_name,
                "Subscribers": subs_count,
                "Last Upload": last_upload_text,
                "Business Email": business_email,
                "Channel Link": link,
                "Outreach Line": outreach_line
            })

            print(f"[{idx+1}/{len(channel_links)}] {channel_name} scraped.")
        except:
            continue

    # ---------------- Save CSV ----------------
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)
    messagebox.showinfo("Done", f"Scraping complete! Saved {OUTPUT_FILE} with {len(data)} channels.")
    driver.quit()


# ---------------- GUI Layout ----------------
root = tk.Tk()
root.title("YouTube Channel Scraper & Outreach")
root.geometry("500x300")

tk.Label(root, text="Search Query / Niche:").pack()
search_query = tk.Entry(root, width=50)
search_query.pack()

tk.Label(root, text="Number of Channels:").pack()
channel_count = tk.Entry(root, width=50)
channel_count.insert(0, "50")
channel_count.pack()

tk.Label(root, text="Output CSV File Name:").pack()
output_name = tk.Entry(root, width=50)
output_name.insert(0, "youtube_outreach.csv")
output_name.pack()

tk.Button(root, text="Start Scraping", command=start_scraping).pack(pady=20)

root.mainloop()
