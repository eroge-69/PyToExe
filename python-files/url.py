import sys
import time
import requests
from bs4 import BeautifulSoup
import re
import os
import cv2
import numpy as np
import logging
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Inisialisasi colorama
init(autoreset=True)

# Mengatur logging level Selenium
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
seleniumLogger.setLevel(logging.WARNING)

def fetch_and_save_pins(url, limit, filename, add_play, image_mode, keyword, replace_images):
    options = Options()
    options.add_argument('--headless')  # Jalankan Chrome tanpa tampilan GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')  # Minimalkan log Selenium

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    collected_urls = set()
    existing_pins = load_pin_log()  # Memuat log pin yang sudah ada

    try:
        with open(filename, 'w') as file:
            urls_to_scrape = [url]
            while len(collected_urls) < limit and urls_to_scrape:
                current_url = urls_to_scrape.pop(0)
                driver.get(current_url)
                last_height = driver.execute_script("return document.body.scrollHeight")

                while len(collected_urls) < limit:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Menunggu halaman ter-load
                    new_height = driver.execute_script("return document.body.scrollHeight")

                    elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/pin/")]')
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            pin_id = href.split("/pin/")[1].split("/")[0]
                            
                            # Jika replace_images = True, abaikan log. Jika False, cek log
                            if replace_images or not check_pin_log(pin_id):
                                if href not in collected_urls:
                                    collected_urls.add(href)
                                    urls_to_scrape.append(href)
                                    file.write(href + '\n')
                                    save_pin_log(pin_id, existing_pins)  # Perbarui log
                                    print(f"{len(collected_urls)} {href}")
                                    if len(collected_urls) >= limit:
                                        break
                        except Exception as e:
                            print(f"Error processing element: {e}")
                            continue

                    if new_height == last_height or len(collected_urls) >= limit:
                        break
                    last_height = new_height
    except KeyboardInterrupt:
        print(Fore.RED + "Proses dibatalkan" + Style.RESET_ALL)
        driver.quit()
        sys.exit()
    finally:
        driver.quit()

    print("--------------------------------------")
    print(f"{Fore.YELLOW}Menemukan {len(collected_urls)} URL{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Lanjut proses gambar..{Style.RESET_ALL}")
    print("--------------------------------------")

    # Lanjutkan ke proses download/unduh gambar setelah mengumpulkan URL
    main(filename, add_play, image_mode, keyword)

def transform_image_url(img_url):
    # Mengubah URL gambar thumbnail jadi versi full
    return re.sub(r"pinimg\.com/[^/]+/", "pinimg.com/originals/", img_url)

def create_unique_folder(base_name, keyword):
    highest_counter = 0
    for folder_name in os.listdir():
        if os.path.isdir(folder_name) and folder_name.startswith(base_name):
            try:
                folder_counter = int(re.findall(r'\d+', folder_name.split('-')[0].strip())[0])
                highest_counter = max(highest_counter, folder_counter)
            except (IndexError, ValueError):
                continue
    counter = highest_counter + 1
    folder_name = f"{base_name} {counter} - {keyword}"
    os.mkdir(folder_name)
    return folder_name

def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    x1, x2 = x, x + img_overlay.shape[1]
    y1, y2 = y, y + img_overlay.shape[0]
    alpha = alpha_mask / 255.0
    alpha_inv = 1.0 - alpha
    for c in range(3):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[:, :, c] +
                               alpha_inv * img[y1:y2, x1:x2, c])

def process_image(image, mode):
    h, w = image.shape[:2]
    if mode == 'S':  # Scale to 1:1 (ditambahkan canvas putih)
        size = max(h, w)
        canvas = np.ones((size, size, 3), dtype=np.uint8) * 255
        top = (size - h) // 2
        left = (size - w) // 2
        canvas[top:top+h, left:left+w] = image
        image = canvas
    elif mode == 'C':  # Crop to 1:1 (memotong sisi lebih)
        size = min(h, w)
        start_x = (w - size) // 2
        start_y = (h - size) // 2
        image = image[start_y:start_y+size, start_x:start_x+size]
    # Mode 'O' (Original): tidak diubah
    return image

def save_image(img_url, folder_name, counter, success_count, fail_count,
               pin_url, url_counter, add_play, image_mode, keyword):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(img_url, headers=headers, stream=True)
        if response.status_code == 200:
            img_array = np.asarray(bytearray(response.content), dtype="uint8")
            image = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
            image = process_image(image, image_mode)

            if add_play:
                play_img = cv2.imread('play.png', cv2.IMREAD_UNCHANGED)
                if play_img is not None:
                    play_size = int(min(image.shape[:2]) * 0.2)
                    resized_play_img = cv2.resize(play_img, (play_size, play_size), interpolation=cv2.INTER_LANCZOS4)
                    center_x = (image.shape[1] - play_size) // 2
                    center_y = (image.shape[0] - play_size) // 2
                    if resized_play_img.shape[2] == 4:
                        alpha_mask = resized_play_img[:, :, 3]
                    else:
                        alpha_mask = np.full((play_size, play_size), 255, dtype=np.uint8)
                    overlay_image_alpha(image, resized_play_img[:, :, :3], center_x, center_y, alpha_mask)

            file_name = f"{counter} - {keyword}.jpg"
            file_path = os.path.join(folder_name, file_name)
            cv2.imwrite(file_path, image)
            print(f"{url_counter} {pin_url} {Fore.GREEN}Done{Style.RESET_ALL}")
            success_count += 1
        else:
            print(f"{url_counter} {pin_url} {Fore.RED}Fail{Style.RESET_ALL}")
            fail_count += 1
    except Exception as e:
        print(f"{url_counter} {pin_url} {Fore.RED}Fail{Style.RESET_ALL}")
        print(f"Error: {e}")
        fail_count += 1
    return counter + 1, success_count, fail_count

def load_pin_log(log_file='pin_log.txt'):
    """Load daftar pin ID dari file log ke dalam set."""
    try:
        with open(log_file, 'r') as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        return set()

def save_pin_log(pin_id, pin_set, log_file='pin_log.txt'):
    """Simpan pin ID baru ke log_file jika belum ada."""
    if pin_id not in pin_set:
        with open(log_file, 'a') as file:
            file.write(pin_id + '\n')
        pin_set.add(pin_id)

def check_pin_log(pin_id, log_file='pin_log.txt'):
    """Cek apakah pin ID sudah ada di log_file."""
    try:
        with open(log_file, 'r') as file:
            existing_ids = set(file.read().strip().split())
            return pin_id in existing_ids
    except FileNotFoundError:
        return False

def main(filename, add_play, image_mode, keyword):
    folder_name = create_unique_folder("Ad Img", keyword)
    counter = 1
    success_count = 0
    fail_count = 0
    url_counter = 1

    try:
        with open(filename, 'r') as file:
            pin_urls = file.readlines()

        for pin_url in pin_urls:
            pin_url = pin_url.strip()
            try:
                response = requests.get(pin_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    image_tag = soup.find('img', {'elementtiming': 'closeupImage'})
                    if image_tag and 'src' in image_tag.attrs:
                        image_url = image_tag['src']
                        new_image_url = transform_image_url(image_url)
                        counter, success_count, fail_count = save_image(
                            new_image_url,
                            folder_name,
                            counter,
                            success_count,
                            fail_count,
                            pin_url,
                            url_counter,
                            add_play,
                            image_mode,
                            keyword
                        )
                    else:
                        print(f"{url_counter} {pin_url} {Fore.RED}Fail{Style.RESET_ALL}")
                        fail_count += 1
                else:
                    print(f"{url_counter} {pin_url} {Fore.RED}Fail{Style.RESET_ALL}")
                    fail_count += 1
            except requests.RequestException as e:
                print(f"{url_counter} {pin_url} {Fore.RED}Fail{Style.RESET_ALL}")
                print(f"Error fetching {pin_url}: {e}")
                fail_count += 1
            url_counter += 1

        print(f"{Fore.CYAN}---------------{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Proses selesai!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}---------------{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Berhasil ({success_count}){Style.RESET_ALL}")
        print(f"{Fore.RED}Gagal ({fail_count}){Style.RESET_ALL}")
        print("-----------")
        print(r"""
    ___ _       ______ _____    ____  ____  ____      ____________________
   /   | |     / / __ / ___/   / __ \/ __ \/ __ \    / / ____/ ____/_  __/
  / /| | | /| / / __  \__ \   / /_/ / /_/ / / / __  / / __/ / /     / /   
 / ___ | |/ |/ / /_/ ___/ /  / ____/ _, _/ /_/ / /_/ / /___/ /___  / /    
/_/  |_|__/|__/_____/____/  /_/   /_/ |_|\____/\____/_____/\____/ /_/     
                                                                          """)
    except KeyboardInterrupt:
        print(Fore.RED + "Proses dibatalkan" + Style.RESET_ALL)
        sys.exit()

if __name__ == "__main__":
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(r"""
    _    _ _               _     _   _                            _
   / \  | | |__   ___ _ __| |_  | | | | _____      ____ _ _ __ __| |
  / _ \ | | '_ \ / _ \ '__| __| | |_| |/ _ \ \ /\ / / _` | '__/ _` |
 / ___ \| | |_) |  __/ |  | |_  |  _  | (_) \ V  V / (_| | | | (_| |
/_/   \_\_|_.__/ \___|_|   \__| |_| |_|\___/ \_/\_/ \__,_|_|  \__,_|""")
        print("")
        print(f"{Fore.YELLOW} ------------------{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}| Scraperkeun v1.3 |{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} ------------------{Style.RESET_ALL}")
        print("")
        print("With play.png: Apakah akan menempelkan logo play ke gambar?")
        print("Scale (S)    : Membuat gambar 1:1 dengan padding putih (tanpa pemotongan).")
        print("Crop (C)     : Memotong gambar agar 1:1.")
        print("Original (O) : Tanpa mengubah dimensi gambar.")
        print("Ctrl + C     : Batalkan proses.")
        print("")
        print(f"{Fore.YELLOW}NB:*{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}- Pastikan play.png ada pada folder yang sama jika ingin memakai play.png{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}- Anda bisa mengganti play.png dengan gambar lain, nama filenya tetap (play.png){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}- Jika ada error, abaikan atau {Fore.RED}lapor ke https://t.me/albrthwrd{Style.RESET_ALL}")
        print("")
        print(f"{Fore.GREEN}Isi data di bawah ini:{Style.RESET_ALL}")
        print("\033[94mKeyword Pinterest:\033[0m ", end='')  # Teks biru
        keyword = input().strip()
        print("\033[94mLimit:\033[0m ", end='')
        limit = int(input())
        print("\033[94mWith play.png (Y/N):\033[0m ", end='')
        add_play_input = input().strip().upper()
        add_play = (add_play_input == 'Y')
        print("\033[94mScale (S) Crop (C) Original (O):\033[0m ", end='')
        image_mode = input().strip().upper()
        print("\033[94mReplace existing images? (Y/N):\033[0m ", end='')
        replace_input = input().strip().upper()
        # Perbaikan: Jika user jawab 'Y', berarti kita *mau* replace image (tidak pakai log)
        replace_images = (replace_input == 'Y')

        filename = 'pin_url.txt'
        search_url = f"https://id.pinterest.com/search/pins/?q={keyword}"
        print("----------------------------")
        print("Proses scrape url dimulai...")
        print("----------------------------")
        fetch_and_save_pins(search_url, limit, filename, add_play, image_mode, keyword, replace_images)
    except KeyboardInterrupt:
        print(Fore.RED + "\nProses dibatalkan" + Style.RESET_ALL)
        sys.exit()
