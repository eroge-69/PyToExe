
import os
import requests
import sys

print("="*40)
print("      BSN Auto Updater By Invisible")
print("="*40)

update_list_url = "http://bdix.bsnbd.com/update.txt"
mod_folder = os.path.join(os.path.expanduser("~"), "Documents", "Euro Truck Simulator 2", "mod")

if not os.path.exists(mod_folder):
    print(f"Mod folder does not exist, creating: {mod_folder}")
    os.makedirs(mod_folder)

try:
    print(f"Fetching update list from {update_list_url} ...")
    response = requests.get(update_list_url)
    response.raise_for_status()
    urls = response.text.strip().split("\n")

    for url in urls:
        url = url.strip()
        if url:
            filename = url.split("/")[-1]
            destination = os.path.join(mod_folder, filename)
            print(f"Downloading {filename} ...")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(destination, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"{filename} downloaded and updated.")

    print("="*40)
    print("All mods updated successfully!")
except Exception as e:
    print(f"Error occurred: {e}")

input("Press Enter to exit...")
