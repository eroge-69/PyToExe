import requests as rq
from bs4 import BeautifulSoup as bs
import subprocess
import os
import concurrent.futures
import re

# Clear screen function
clear = lambda: subprocess.call('cls||clear', shell=True)

# UserAgent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

# Set domain url
base_url = 'https://www.kaotic.com'
category = '/category/accident' # Set category
page = '?paged='
beginpage = 1 # Set begin number page
lastpage = 10 # Set last number page

# Fetch total result pages
page_links = [f'{base_url}{category}{page}{i}' for i in range(int(beginpage), int(lastpage) + 1)]

# Create a folder to save the videos
folder_name = 'videos'
os.makedirs(folder_name, exist_ok=True)

# Fetch video links from all page links
video_links = []
for link in page_links:
    print(link)
    fetch = rq.get(link, headers=headers)
    soup = bs(fetch.content, "html.parser")
    data = soup.select(".video-title a")
    for item in data:
        url = item.get('href')
        print(url)
        if url:
            video_links.append(url)
print('Found total ' + str(len(video_links)) + ' url(s)')

# Function to sanitize the video name
def sanitize_name(name):
    # Remove invalid characters from the name
    sanitized_name = re.sub(r'[\/:*?"<>|]', '', name)
    return sanitized_name

# Function to download a video
def download_video(url, folder):
    fetch = rq.get(url, headers=headers)
    soup = bs(fetch.content, "html.parser")
    title = soup.find("title")
    name = title.get_text()
    sanitized_name = sanitize_name(name)  # Sanitize the video name
    raw = soup.select(".video-content")
    data = raw[0]

    for item in raw:
        vdotag = item.find('source')
        if vdotag:
            vdolink = vdotag.get('src')
            if vdolink:
                filename = os.path.join(folder, sanitized_name + '.mp4')
                if os.path.exists(filename):
                    print(f'Skipping: {sanitized_name} (already exists)')
                else:
                    vdores = rq.get(vdolink, stream=True)
                    with open(filename, "wb") as file:
                        total_size = int(vdores.headers.get('content-length', 0))
                        downloaded_size = 0
                        print('Downloading:', sanitized_name)
                        for chunk in vdores.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                                downloaded_size += len(chunk)
                                progress = (downloaded_size / total_size) * 100
                                print(f'Progress: {progress:.2f}%  ', end='\r')
                        print('\nDownload complete.')

# Download videos concurrently
count = 0
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for link in video_links:
        futures.append(executor.submit(download_video, link, folder_name))
    
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
            count += 1
        except Exception as e:
            print(f'Error occurred during download: {e}')

print(f'\nScraping total video(s) successful.; Collected total {count} video(s)')
