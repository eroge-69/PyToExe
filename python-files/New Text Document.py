import requests
import os
from urllib.parse import urlparse
import threading
from tqdm import tqdm

class SimpleDownloadManager:
    def __init__(self):
        self.downloads = []
    
    def download_file(self, url, destination=None):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            if not destination:
                filename = os.path.basename(urlparse(url).path)
                destination = filename or "downloaded_file"
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(destination, 'wb') as file:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            pbar.update(len(chunk))
            
            print(f"Download completed: {destination}")
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def add_download(self, url, destination=None):
        thread = threading.Thread(
            target=self.download_file, 
            args=(url, destination)
        )
        self.downloads.append(thread)
        thread.start()

# Usage example
if __name__ == "__main__":
    dm = SimpleDownloadManager()
    
    # Example download
    url = "https://example.com/file.zip"
    dm.add_download(url, "myfile.zip")
