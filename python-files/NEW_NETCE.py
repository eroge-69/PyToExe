import os
import shutil
import threading
import time
import sys
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
import ctypes

# Inisialisasi Colorama
init(autoreset=True)

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT

CHROMEDRIVER_PATH = 'C:/tools/chromedriver/chromedriver.exe'
BASE_PROFILE_DIR = 'C:/temp/netflix_chat_terminal'
CHROME_SESSIONS = 10
URL = (
    'https://help.netflix.com/interface/chat?lobby=true&mobile=true&locale=en&country=&helpText=Because%20of%20unforeseen%20circumstances%2C%20I%20no%20longer%20have%20access%20to%20my%20primary%20email%20and%20urgently%20need%20to%20update%20my%20email%20address%20for%20my%20account'
)

MAX_GRID_COLS = 3
MAX_GRID_ROWS = 2
window_positions = []
positions_lock = threading.Lock()

session_counter = CHROME_SESSIONS
result = {"driver": None, "profile": None}
found_event = threading.Event()
all_sessions = []
all_sessions_lock = threading.Lock()

support_agent_names = []

support_keywords = []

def get_next_position(index):
    with positions_lock:
        for y in range(MAX_GRID_ROWS):
            for x in range(MAX_GRID_COLS):
                pos = (x, y)
                if pos not in window_positions:
                    window_positions.append(pos)
                    return pos
        pos = (index - 1) % MAX_GRID_COLS, ((index - 1) // MAX_GRID_COLS) % MAX_GRID_ROWS
        if pos not in window_positions:
            window_positions.append(pos)
        return pos

def free_position(pos):
    with positions_lock:
        if pos in window_positions:
            window_positions.remove(pos)

def clean_profile(profile_path):
    if os.path.exists(profile_path):
        try:
            shutil.rmtree(profile_path)
        except:
            pass

def detect_email_support(driver, index):
    global session_counter
    try:
        current_url = driver.current_url.lower()
        if "sprinklr" in current_url:
            print(f"{MAGENTA}🚨 TERDETEKSI CS GLOBAL{RESET}")
            return True

        chat_texts = driver.find_elements(By.XPATH, "//div[contains(@class,'bubble') or contains(@class,'message')]")
        for bubble in chat_texts:
            text = bubble.text.lower()
            print(f"[DEBUG] Bubble content: {text}")
            if any(keyword in text for keyword in support_keywords):
                print(f"{GREEN}🟢 Deteksi CS yang dapat membantu: {text}{RESET}")
                return True
            if any(keyword in text for keyword in [
                "i'm sorry", "cannot help you", "we are unable to",
                "not authorized", "please call", "submit a form",
                "outside of our scope", "security reasons",
                "i don’t have access", "i don’t see that option",
                "there’s nothing i can do", "you must log in"
            ]):
                print(f"{RED}🔴 CS tidak dapat membantu. Melewati sesi ini...{RESET}")
                session_counter += 1
                threading.Thread(target=thread_worker, args=(session_counter,)).start()
                if hasattr(driver, '_grid_pos'):
                    free_position(driver._grid_pos)
                return False
    except Exception as e:
        print(f"{YELLOW}⚠️ Kesalahan saat mendeteksi dukungan email: {str(e)}{RESET}")

    print(f"{YELLOW}🔴 CS ini tidak menyebut bantuan ganti email. Melewati...{RESET}")
    session_counter += 1
    threading.Thread(target=thread_worker, args=(session_counter,)).start()
    if hasattr(driver, '_grid_pos'):
        free_position(driver._grid_pos)
    return False

def thread_worker(index):
    driver, profile = start_chat_session(index)
    threading.Thread(target=monitor_driver_closure, args=(driver, profile), daemon=True).start()
    if not driver:
        return
    with all_sessions_lock:
        all_sessions.append((driver, profile))
    if found_event.is_set():
        driver.quit()
        clean_profile(profile)
        if hasattr(driver, '_grid_pos'):
            free_position(driver._grid_pos)
        return
    if wait_for_connection(driver):
        print(f"{CYAN}🟡 Terhubung dengan CS...{RESET}")
        return
        if not found_event.is_set():
            driver.set_window_position(0, 0)
            result["driver"] = driver
            result["profile"] = profile
            found_event.set()

def start_chat_session(index):
    profile_path = os.path.join(BASE_PROFILE_DIR, f"profile_{index}")
    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    user32 = ctypes.windll.user32
    screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    window_width, window_height = 500, 400
    grid_x, grid_y = get_next_position(index)
    pos_x = grid_x * (window_width + 20)
    pos_y = grid_y * (window_height + 20)
    options.add_argument(f"--window-size={window_width},{window_height}")
    options.add_argument(f"--window-position={pos_x},{pos_y}")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-features=OnDeviceModel")
    options.add_argument("--disable-speech-api")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-logging")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
    driver._grid_pos = (grid_x, grid_y)
    driver.get(URL)

    attempt = 0
    while True:
        try:
            WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'chat with an agent')]")
                )
            ).click()
            break
        except:
            print(f"{YELLOW}🔁 REFRESH DULU YAA.... (percobaan ke-{attempt+1}){RESET}")
            driver.refresh()
            attempt += 1
            time.sleep(3)
    

    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no')]")
            )
        ).click()
    except:
        pass

    return driver, profile_path

def monitor_driver_closure(driver, profile_path):
    while True:
        try:
            driver.title  # akan memicu exception jika driver sudah ditutup
        except:
            print(f"{RED}🚫 Chrome ditutup oleh pengguna. Menghapus profil: {profile_path}{RESET}")
            clean_profile(profile_path)
            return
        time.sleep(2)

def wait_for_connection(driver):
    print(f"{CYAN}🔍 Menunggu koneksi CS...{RESET}")
    while True:
        try:
            bubbles = driver.find_elements(By.XPATH, "//div")
            for b in bubbles:
                text = b.text.strip().lower()
                if "chatting with" in text or "you are now chatting" in text:
                    print(f"{GREEN}✅ CS terdeteksi dengan teks: {text}{RESET}")
                    return True
        except:
            pass
        time.sleep(1)

def start_agent_search():
    threads = []
    for i in range(1, CHROME_SESSIONS + 1):
        t = threading.Thread(target=thread_worker, args=(i,))
        t.start()
        threads.append(t)

    while not found_event.is_set():
        time.sleep(1)

    print(f"\n{BOLD}{GREEN}✅ Menemukan CS yang bisa membantu!{RESET}")
    print(f"{CYAN}🧭 Profil tersimpan: {result['profile']}{RESET}")
    print(f"{YELLOW}🔔 Lanjutkan percakapan secara manual di jendela Chrome yang terbuka.{RESET}")
    print(f"{RED}❗ Jangan tutup browser ini sampai proses selesai.{RESET}")

def banner():
    global CHROME_SESSIONS, session_counter
    print(f"{CYAN}Masukkan jumlah sesi Chrome yang diinginkan:{RESET}")
    try:
        input_sessions = int(input(f"{YELLOW}Jumlah sesi: {RESET}"))
        if input_sessions > 0:
            CHROME_SESSIONS = input_sessions
            session_counter = CHROME_SESSIONS
    except ValueError:
        print(f"{RED}Input tidak valid. Menggunakan jumlah default: {CHROME_SESSIONS}{RESET}")

    print(f"""{BOLD}{MAGENTA}
 ███╗   ██╗███████╗████████╗ ██████╗███████╗
 ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝
 ██╔██╗ ██║█████╗     ██║   ██║     █████╗  
 ██║╚██╗██║██╔══╝     ██║   ██║     ██╔══╝  
 ██║ ╚████║███████╗   ██║   ╚██████╗███████╗
 ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝╚══════╝
     AUTO CHAT STARTER UNTUK CTP
     ███ DEVELOPED BY SINON ████
{RESET}""")
    print()
    print(f"{CYAN}Jumlah sesi Chrome: {CHROME_SESSIONS}{RESET}")
    input(f"{YELLOW}Tekan ENTER untuk memulai...{RESET}")

if __name__ == "__main__":
    banner()
    start_agent_search()
