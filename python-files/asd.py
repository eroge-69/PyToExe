from ctypes import windll
import random
import socket
import string
import threading
import time
import webbrowser
from customtkinter import *
import requests
from PIL import Image, ImageTk
import io
import os
import subprocess
from datetime import date
import winsound
import mysql.connector
import multiprocessing # YENİ EKLENDİ

# --- TEMEL AYARLAR ---
set_appearance_mode("dark")
set_default_color_theme("dark-blue")

# --- GÜNLÜK KULLANIM KONTROLÜ FONKSİYONLARI ---

def get_hwid():
    """Windows'a özel olarak makinenin UUID'sini (HWID olarak) alır."""
    try:
        hwid = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
        return hwid
    except Exception:
        return str(random.randint(10000000, 99999999))

def get_data_file_path():
    """Veri dosyasını APPDATA klasöründe saklamak için tam yolunu oluşturur."""
    app_data_path = os.getenv('APPDATA')
    directory = os.path.join(app_data_path, 'ssqChecker')
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, '.ssvqq')

def write_log_file():
    """Program kapatılırken bugünün tarihini ve HWID'yi dosyaya yazar."""
    hwid = get_hwid()
    today_str = date.today().isoformat()
    file_path = get_data_file_path()
    try:
        with open(file_path, 'w') as f:
            f.write(f"{hwid}:{today_str}")
    except Exception as e:
        pass

# --- UYGULAMA BAŞLANGIÇ KONTROLÜ ---
FILE_PATH = get_data_file_path()
CURRENT_HWID = get_hwid()
TODAY_STR = date.today().isoformat()

try:
    with open(FILE_PATH, 'r') as f:
        content = f.read().strip()
        stored_hwid, last_run_date = content.split(':')

    if stored_hwid == CURRENT_HWID and last_run_date == TODAY_STR:
        def on_error_window_close():
            os._exit(1)

        winsound.MessageBeep(winsound.MB_ICONHAND)
        error_gui = CTk()
        error_gui.withdraw()
        
        error_window = CTkToplevel(error_gui)
        error_window.title("Error!")
        error_window.geometry("350x100")
        error_window.protocol("WM_DELETE_WINDOW", on_error_window_close)
        error_window.resizable(width=False, height=False)
        
        ekran_genislik = error_window.winfo_screenwidth()
        ekran_yukseklik = error_window.winfo_screenheight()
        x = (ekran_genislik // 2) - (350 // 2)
        y = (ekran_yukseklik // 2) - (100 // 2)
        error_window.geometry(f"350x100+{x}+{y}")
        
        points_color = "#FFFFFF"
        label = CTkLabel(error_window, text="Run it once a day, nephew.", font=("Arial", 14), text_color=points_color)
        label.pack(expand=True, padx=20, pady=20)
        
        error_window.attributes('-topmost', 1)
        error_window.after(4000, lambda: os._exit(1))
        error_window.mainloop()
        
except (FileNotFoundError, ValueError):
    pass

# --- YARDIMCI VE ARKAPLAN FONKSİYONLARI ---

def _simple_internet_check(timeout: float = 3.0) -> bool:
    try:
        sock = socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        sock.close()
        return True
    except OSError:
        return False

def monitor_internet_and_exit(gui, interval_seconds: int = 10, timeout: float = 3.0):
    while True:
        if not _simple_internet_check(timeout=timeout):
            try:
                gui.after(0, gui.destroy)
            except Exception:
                pass
            time.sleep(0.3)
            os._exit(1)
        time.sleep(interval_seconds)

def ortala_pencere(window, width, height):
    ekran_genislik = window.winfo_screenwidth()
    ekran_yukseklik = window.winfo_screenheight()
    x = (ekran_genislik // 2) - (width // 2)
    y = (ekran_yukseklik // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def start_drag(event):
    global last_x, last_y
    last_x = event.x
    last_y = event.y

last_x = 0
last_y = 0

def drag(event):
    x_offset = event.x - last_x
    y_offset = event.y - last_y
    gui.geometry(f"+{gui.winfo_x() + x_offset}+{gui.winfo_y() + y_offset}")

# --- API VE VERİ ÇEKME AYARLARI ---
API_SOURCE_URL = "https://raw.githubusercontent.com/Sibercom/malware/refs/heads/main/api001.txt"
FALLBACK_API_KEY = "RGAPI-45413158-9c2e-4102-82cc-b9653864eaa8"

def get_api_key(source_url: str = API_SOURCE_URL, timeout: int = 6) -> str | None:
    try:
        resp = requests.get(source_url, timeout=timeout)
        resp.raise_for_status()
        key = resp.text.strip()
        return key if key else FALLBACK_API_KEY
    except requests.RequestException:
        return FALLBACK_API_KEY

API_KEY = get_api_key()
LOL_PLATFORM = "tr1"
VAL_REGION = "eu"
ACCOUNT_REGION = "europe"
ACCOUNT_URL = f"https://{ACCOUNT_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{{}}/{{}}?api_key={API_KEY}"
LOL_SUMMONER_URL = f"https://{LOL_PLATFORM}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{{}}?api_key={API_KEY}"
LOL_LEAGUE_URL = f"https://{LOL_PLATFORM}.api.riotgames.com/lol/league/v4/entries/by-summoner/{{}}?api_key={API_KEY}"
VAL_RANKED_URL = f"https://{VAL_REGION}.api.riotgames.com/val/ranked/v1/by-puuid/{{}}?api_key={API_KEY}"

def get_lol_data(puuid):
    try:
        summoner_url = LOL_SUMMONER_URL.format(puuid)
        response_summoner = requests.get(summoner_url, timeout=5)
        if response_summoner.status_code != 200:
            return {"error": f"No Summoner: {response_summoner.status_code}"}
        
        summoner_data = response_summoner.json()
        level = summoner_data.get('summonerLevel', 'N/A')
        summoner_id = summoner_data.get('id')

        league_url = LOL_LEAGUE_URL.format(summoner_id)
        response_league = requests.get(league_url, timeout=5)
        if response_league.status_code != 200:
            return {"level": level, "rank": "Unranked"}

        league_data = response_league.json()
        rank_info = "Unranked"
        if league_data:
            for queue in league_data:
                if queue.get('queueType') == 'RANKED_SOLO_5x5':
                    tier = queue.get('tier', '').capitalize()
                    rank = queue.get('rank', '')
                    lp = queue.get('leaguePoints', 0)
                    rank_info = f"{tier} {rank} - {lp} LP"
                    break
        return {"level": level, "rank": rank_info}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

def get_valorant_data(puuid):
    VALORANT_RANKS = [
        "Unranked", "Unused 1", "Unused 2", "Iron 1", "Iron 2", "Iron 3",
        "Bronze 1", "Bronze 2", "Bronze 3", "Silver 1", "Silver 2", "Silver 3",
        "Gold 1", "Gold 2", "Gold 3", "Platinum 1", "Platinum 2", "Platinum 3",
        "Diamond 1", "Diamond 2", "Diamond 3", "Ascendant 1", "Ascendant 2", "Ascendant 3",
        "Immortal 1", "Immortal 2", "Immortal 3", "Radiant"
    ]
    try:
        val_url = VAL_RANKED_URL.format(puuid)
        response_val = requests.get(val_url, timeout=5)
        if response_val.status_code != 200:
            return {"error": f"{response_val.status_code}"}
        
        val_data = response_val.json()
        rank_info = "No rank"
        if val_data and 'byPuuid' in val_data:
            seasons = val_data.get('byPuuid', {}).get('results', {}).get('queueRanks', {}).get('competitive', {}).get('bySeason')
            if seasons:
                latest_season = list(seasons.values())[0]
                tier_num = latest_season.get('competitiveTier', 0)
                rank_info = VALORANT_RANKS[tier_num] if 0 <= tier_num < len(VALORANT_RANKS) else "Unknown"
        return {"rank": rank_info}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

def get_and_delete_code_from_db():
    """
    Veritabanından rastgele bir RP kodu alır, o kodu veritabanından siler ve kodu döndürür.
    .exe uyumluluğu için 'use_pure' ve 'ssl_disabled' seçenekleri eklenmiştir.
    """
    db_config = {
        'host': '185.223.77.84',
        'user': 'berkayim',
        'password': 'RVGwg1udjCwBe[b0',
        'database': 'rplolk',
        'use_pure': True,       # .exe uyumluluğu için eklendi
        'ssl_disabled': True    # .exe uyumluluğu için eklendi
    }
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("START TRANSACTION;")
        cursor.execute("SELECT id, code FROM rp_codes ORDER BY RAND() LIMIT 1 FOR UPDATE;")
        result = cursor.fetchone()

        if result:
            code_id, the_code = result
            cursor.execute("DELETE FROM rp_codes WHERE id = %s;", (code_id,))
            connection.commit()
            return the_code
        else:
            return "!x!" # Veritabanında kod kalmamışsa
            
    except mysql.connector.Error as e:
        if connection:
            connection.rollback() # Hata olursa işlemi geri al
        return None # Hata durumunda None döndür
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# --- GLOBAL DURUM DEĞİŞKENLERİ ---
buldu = 0
ilkbasilma = 0
simulation_after_id = None
is_first_run_in_session = True

# --- GÜVENLİ GUI GÜNCELLEME VE KONTROL FONKSİYONLARI ---

def reset_ui_state():
    if buldu == 0:
        gui.after(3000, lambda: status_label.configure(text=""))
        hesap_kilitle_buton.configure(text="Run miner", state=NORMAL)
        id_girdi.configure(state=NORMAL)
    else:
        id_girdi.configure(state=DISABLED)
        hesap_kilitle_buton.configure(text="Locked", state=DISABLED)

# YENİ YARDIMCI FONKSİYON: Arka plan thread'inden GUI'yi güvenle güncellemek için.
def update_status_label(text, color):
    status_label.configure(text=text, text_color=color)
    if text:
        status_label.place(relx=0.5, rely=0.5, anchor="center")
    else:
        status_label.place_forget()

# YENİ FONKSİYON: Tüm ağ/veritabanı işlemlerini arka planda yapar.
def run_check_in_background():
    global buldu, ilkbasilma, is_first_run_in_session
    riot_id = id_girdi.get().strip()

    if not riot_id or "#" not in riot_id:
        gui.after(0, update_status_label, "Invalid format!", "orange")
        gui.after(2000, lambda: gui.after(0, update_status_label, "", "white"))
        gui.after(0, reset_ui_state)
        return

    gameName, tagLine = riot_id.split("#", 1)

    try:
        account_url = ACCOUNT_URL.format(gameName, tagLine)
        response_account = requests.get(account_url, timeout=5)

        if response_account.status_code != 200:
            error_msg = "User not found!"
            if response_account.status_code == 403: error_msg = "Invalid API Key!"
            gui.after(0, update_status_label, error_msg, "red")
            gui.after(2000, lambda: gui.after(0, update_status_label, "", "white"))
            gui.after(0, reset_ui_state)
            return
        
        puuid = response_account.json()['puuid']
        lol_data = get_lol_data(puuid)
        val_data = get_valorant_data(puuid)
        lol_ok = lol_data and "error" not in lol_data
        val_ok = val_data and "error" not in val_data

        if lol_ok or val_ok:
            final_text = f"{gameName}#{tagLine}  ✔"
            gui.after(0, update_status_label, final_text, "green")
            buldu = 1
            ilkbasilma = 1
            gui.after(0, enable_reset_button)

            final_code_to_display = None
            color_to_display = points_color
            duration = 29
            
            if is_first_run_in_session:
                final_code_from_db = get_and_delete_code_from_db()
                if final_code_from_db and final_code_from_db != "!x!":
                    final_code_to_display = final_code_from_db
                    color_to_display = riot_color
                    duration = 47
                    is_first_run_in_session = False
                elif final_code_from_db == "!x!":
                    gui.after(0, lambda: label3.configure(text="All Codes Distributed!", text_color="orange"))
                else:
                    gui.after(0, lambda: label3.configure(text="!  ERROR  !", text_color="red"))
            else:
                final_code_to_display = generate_fake_rp_code()
                color_to_display = points_color

            if final_code_to_display:
                gui.after(0, start_simulation, label3, duration, 200, final_code_to_display, color_to_display)
        else:
            final_text = f"{gameName}#{tagLine}  ✖"
            gui.after(0, update_status_label, final_text, "red")
        
        gui.after(0, reset_ui_state)

    except requests.exceptions.RequestException:
        gui.after(0, update_status_label, "Network error!", "red")
        gui.after(3000, lambda: gui.after(0, update_status_label, "", "white"))
        gui.after(0, reset_ui_state)

# DEĞİŞTİRİLDİ: Bu fonksiyon artık thread başlatıyor.
def hesapkilitle():
    hesap_kilitle_buton.configure(text="Running", state=DISABLED)
    id_girdi.configure(state=DISABLED)
    threading.Thread(target=run_check_in_background, daemon=True).start()

# --- ANA GUI OLUŞTURMA ---
gui = CTk()
gui.title("FuckRiot")
gui.geometry("500x500")
gui.resizable(width=False, height=False)
gui.overrideredirect(True)

# --- PENCERE YÖNETİMİ ---
def set_appwindow(mainWindow):
    hwnd = windll.user32.GetParent(mainWindow.winfo_id())
    stylew = windll.user32.GetWindowLongW(hwnd, -20)
    stylew &= ~0x00000080
    stylew |= 0x00040000
    windll.user32.SetWindowLongW(hwnd, -20, stylew)
    mainWindow.wm_withdraw()
    mainWindow.after(10, lambda: mainWindow.wm_deiconify())

gui.after(10, lambda: set_appwindow(gui))
ortala_pencere(gui, 500, 500)
threading.Thread(target=monitor_internet_and_exit, args=(gui,), daemon=True).start()
gui.attributes('-topmost', 1)
gui.after(2000, lambda: gui.attributes('-topmost', 0))

def kapatkesin():
    write_log_file()
    os._exit(0)

z = 0
def frameMapped(event=None):
    global z
    gui.overrideredirect(True)
    if z == 1:
        set_appwindow(gui)
        z = 0

def minimizeGUI():
    global z
    gui.state('withdrawn')
    gui.overrideredirect(False)
    gui.state('iconic')
    z = 1

gui.bind("<Map>", frameMapped)

# --- ARAYÜZ ELEMANLARI (WIDGETS) ---
title_frame = CTkFrame(gui, width=500, height=80, corner_radius=0)
title_frame.place(x=0, y=0)

status_label_frame = CTkFrame(gui, width=500, height=50, fg_color="#1a1a1a", corner_radius=0)
status_label_frame.place(x=0, y=240)

# Title Frame İçeriği
min_button_font = CTkFont(family='Lucida Console', size=25, weight='bold')
minmize_button = CTkButton(title_frame, text=" _ ", font=min_button_font, width=20, height=20, command=minimizeGUI, fg_color="black", hover_color="#212121")
minmize_button.place(x=425, y=5)

close_button_font = CTkFont(family='Lucida Console', size=25, weight='bold')
close_button = CTkButton(title_frame, text=" x ", font=close_button_font, width=20, height=20, command=kapatkesin, fg_color="black", hover_color="#D6232D")
close_button.place(x=425, y=45)

try:
    URL = "https://raw.githubusercontent.com/Sibercom/malware/refs/heads/main/8011725.png"
    response = requests.get(URL)
    pil_img = Image.open(io.BytesIO(response.content)).resize((60, 60))
    ctk_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
    label = CTkLabel(title_frame, image=ctk_img, text="")
    label.place(x=10, y=10)
    label.bind("<Button-1>", start_drag)
    label.bind("<B1-Motion>", drag)
except:
    pass # Resim yüklenemezse program çökmesin

title_font = CTkFont(family="Arial", size=28, weight="bold")
riot_color = "#D6232D"
points_color = "#FFFFFF"

riot_label = CTkLabel(title_frame, text="Riot", font=title_font, text_color=riot_color)
riot_label.place(x=180, y=20)
points_label = CTkLabel(title_frame, text="Points", font=title_font, text_color=points_color)
points_label.place(x=250, y=20)

# Ana Pencere İçeriği
try:
    URL2 = "https://raw.githubusercontent.com/Sibercom/malware/refs/heads/main/rreload.png"
    response2 = requests.get(URL2)
    pil_img2 = Image.open(io.BytesIO(response2.content)).resize((60, 60))
    ctk_img2 = CTkImage(light_image=pil_img2, dark_image=pil_img2, size=(60, 60))
    label2 = CTkLabel(gui, image=ctk_img2, text="")
    label2.place(x=52, y=136)
except:
    pass

def on_enter_reset(event): gui.configure(cursor="hand2")
def on_leave_reset(event): gui.configure(cursor="arrow")

def enable_reset_button():
    label2.bind("<Button-1>", on_label_click)
    label2.bind("<Enter>", on_enter_reset)
    label2.bind("<Leave>", on_leave_reset)

def disable_reset_button():
    label2.unbind("<Button-1>")
    label2.unbind("<Enter>")
    label2.unbind("<Leave>")
    gui.configure(cursor="arrow")

def on_label_click(event):
    global buldu, simulation_after_id
    if simulation_after_id:
        gui.after_cancel(simulation_after_id)
        simulation_after_id = None
    buldu = 0
    update_status_label("", "white")
    label3.configure(text="")
    hesap_kilitle_buton.configure(text="Run miner", state=NORMAL)
    id_girdi.configure(state=NORMAL)
    id_girdi.delete(0, "end")
    disable_reset_button()

disable_reset_button()

def limit_length(P): return len(P) <= 24
vcmd = gui.register(limit_length)
id_girdi_font = CTkFont(family='Lucida Console', size=13, weight='bold')
id_girdi = CTkEntry(gui, placeholder_text="Nickname#TAG", font=id_girdi_font, width=250, border_color=riot_color, text_color=points_color, validate="key", validatecommand=(vcmd, "%P"))
id_girdi.place(x=125, y=150)

status_label_font = CTkFont(family='Lucida Console', size=13, weight='bold')
status_label = CTkLabel(status_label_frame, text="", font=status_label_font)

btn_font = CTkFont(family='Lucida Console', size=13, weight='bold')
hesap_kilitle_buton = CTkButton(gui, text="Run miner", width=120, font=btn_font, text_color=points_color, command=hesapkilitle)
hesap_kilitle_buton.place(x=190, y=195)

# Geliştirici İletişim
def iletisim(event=None): webbrowser.open("https://t.me/sibercom")
def on_enter_label(event):
    imza_label.configure(text_color=riot_color)
    gui.config(cursor="hand2")
def on_leave_label(event):
    imza_label.configure(text_color=points_color)
    gui.config(cursor="arrow")

imza_font = CTkFont(family='Lucida Console', size=15, weight='normal')
imza_label = CTkLabel(gui, text="Developer Toxic", font=imza_font, text_color=points_color)
imza_label.place(x=5, y=470)
imza_label.bind("<Button-1>", iletisim)
imza_label.bind("<Enter>", on_enter_label)
imza_label.bind("<Leave>", on_leave_label)

# --- ANİMASYON FONKSİYONLARI ---
def generate_fake_rp_code():
    alphabet = string.ascii_uppercase + string.digits
    random_part = "".join(random.choices(alphabet, k=16))
    return f"RA-{random_part}"

def start_simulation(label, duration=5, interval=500, final_text="RA-XXXXXXXXXXXXXXXX", final_color=None):
    steps = int((duration * 1000) / interval)
    counter = {"i": 0}

    def update():
        global simulation_after_id
        if counter["i"] < steps:
            label.configure(text=generate_fake_rp_code(), text_color=points_color)
            counter["i"] += 1
            simulation_after_id = label.after(interval, update)
        else:
            label.configure(text=final_text, text_color=final_color if final_color else points_color)
            simulation_after_id = None
    update()

label3 = CTkLabel(gui, text="", font=("Lucida Console", 18))
label3.place(x=140, y=310)

# --- Pencere Sürükleme Bağlantıları ---
points_label.bind("<Button-1>", start_drag)
points_label.bind("<B1-Motion>", drag)
riot_label.bind("<Button-1>", start_drag)
riot_label.bind("<B1-Motion>", drag)
title_frame.bind("<Button-1>", start_drag)
title_frame.bind("<B1-Motion>", drag)

# --- ANA DÖNGÜYÜ BAŞLAT ---
if __name__ == "__main__":
    multiprocessing.freeze_support()
    gui.mainloop()