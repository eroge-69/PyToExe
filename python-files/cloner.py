import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
from queue import Queue
import sys
import time

class AdvancedWebsiteDownloader:
    def __init__(self):
        self.clear_screen()
        self.show_banner()
        self.base_url = self.get_valid_url()
        self.output_dir = "downloaded_site"
        self.visited_urls = set()
        self.queue = Queue()
        self.domain = urlparse(self.base_url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.total_files = 0
        self.downloaded_files = 0
        os.makedirs(self.output_dir, exist_ok=True)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        banner = r"""

 ________      ___    ___ _____ ______   _______   ________           ________  _______   ___      ___ 
|\   __  \    |\  \  /  /|\   _ \  _   \|\  ___ \ |\   ___  \        |\   ___ \|\  ___ \ |\  \    /  /|
\ \  \|\  \   \ \  \/  / | \  \\\__\ \  \ \   __/|\ \  \\ \  \       \ \  \_|\ \ \   __/|\ \  \  /  / /
 \ \   __  \   \ \    / / \ \  \\|__| \  \ \  \_|/_\ \  \\ \  \       \ \  \ \\ \ \  \_|/_\ \  \/  / / 
  \ \  \ \  \   \/  /  /   \ \  \    \ \  \ \  \_|\ \ \  \\ \  \       \ \  \_\\ \ \  \_|\ \ \    / /  
   \ \__\ \__\__/  / /      \ \__\    \ \__\ \_______\ \__\\ \__\       \ \_______\ \_______\ \__/ /   
    \|__|\|__|\___/ /        \|__|     \|__|\|_______|\|__| \|__|        \|_______|\|_______|\|__|/    
             \|___|/                                                                                   
                                                                                                       
                                                                                                        

                    Advanced Website Downloader                    
                     Created by: Aymen Dev                        
        """
        print(banner)

    def get_valid_url(self):
        while True:
            url = input("\n\n >> Enter website URL to download (include http:// or https://): ").strip()
            if url.startswith(('http://', 'https://')):
                return url
            print("Invalid URL! Please include http:// or https://")

    def show_progress(self):
        while self.downloaded_files < self.total_files:
            percent = (self.downloaded_files / self.total_files) * 100
            bar = '=' * int(percent / 2) + ' ' * (50 - int(percent / 2))
            sys.stdout.write(f"\rProgress: [{bar}] {percent:.1f}% | Downloaded: {self.downloaded_files}/{self.total_files} files")
            sys.stdout.flush()
            time.sleep(0.1)

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.netloc == self.domain or not parsed.netloc

    def download_file(self, url, filepath):
        try:
            response = self.session.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.downloaded_files += 1
            return True
        except Exception as e:
            print(f"\nFailed to download {url}: {str(e)}")
            return False

    def process_url(self, url):
        if url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        print(f"\nProcessing: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            path = urlparse(url).path.lstrip('/')
            if not path:
                path = "index.html"
            elif '.' not in os.path.basename(path):
                path = os.path.join(path, "index.html")
                
            filepath = os.path.join(self.output_dir, path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            if not response.headers.get('Content-Type', '').startswith('text/html'):
                if self.download_file(url, filepath):
                    self.total_files += 1
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tag, attr in [('a', 'href'), ('link', 'href'), 
                            ('script', 'src'), ('img', 'src'),
                            ('source', 'srcset'), ('iframe', 'src')]:
                for element in soup.find_all(tag, **{attr: True}):
                    original_url = element[attr]
                    absolute_url = urljoin(url, original_url)
                    
                    if self.is_valid_url(absolute_url):
                        local_path = os.path.join(self.output_dir, urlparse(absolute_url).path.lstrip('/'))
                        element[attr] = os.path.relpath(local_path, os.path.dirname(filepath))
                        self.queue.put(absolute_url)
                        self.total_files += 1
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
                
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")

    def start_download(self, max_threads=5):
        print("\nInitializing download...")
        self.queue.put(self.base_url)
        self.total_files += 1
        
        progress_thread = threading.Thread(target=self.show_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        def worker():
            while not self.queue.empty():
                url = self.queue.get()
                self.process_url(url)
                self.queue.task_done()
        
        threads = []
        for _ in range(max_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        print(f"\n\nDownload complete! Website saved to: {os.path.abspath(self.output_dir)}")
        print(f"Total files downloaded: {self.downloaded_files}")

if __name__ == "__main__":
    try:
        downloader = AdvancedWebsiteDownloader()
        downloader.start_download()
    except KeyboardInterrupt:
        print("\nDownload interrupted by user!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")