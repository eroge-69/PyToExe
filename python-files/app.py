import time
import os
import requests
import easyocr
import asyncio
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

from colorama import init, Fore
import time

def print_banner_animated(delay=0.01):
    """Statik banner metnini animasyonlu olarak yazdırır."""
    banner = """
███████╗ █████╗ ██████╗  █████╗         ██████╗  ██████╗ ████████╗
╚══███╔╝██╔══██╗██╔══██╗██╔══██╗        ██╔══██╗██╔═══██╗╚══██╔══╝
  ███╔╝ ███████║██████╔╝███████║        ██████╔╝██║   ██║   ██║   
 ███╔╝  ██╔══██║██╔══██╗██╔══██║        ██╔══██╗██║   ██║   ██║   
███████╗██║  ██║██║  ██║██║  ██║███████╗██████╔╝╚██████╔╝   ██║   
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝    ╚═╝   

Creator: Hüseyin Efe Omaç
"""
    for char in banner:
        print(char, end='', flush=True)
        time.sleep(delay)

print_banner_animated(0.005)  # İstersen delay değerini ayarlayabilirsin.

# Başlatmalar
init(autoreset=True)
load_dotenv()

# Ayarlar
URL = "https://www.zara.com/tr/tr/kruvaze-takim-blazer-p04788232.html?v1=443574966&utm_campaign=productShare&utm_medium=mobile_sharing_iOS&utm_source=red_social_movil"
GENAI_API_KEY = "AIzaSyClq30coZFJi_806Hm1tjvP3Ybf73TXX4w"
TELEGRAM_TOKEN = os.getenv("APIKey")
TELEGRAM_CHAT_ID = os.getenv("chatID1")

# GenAI import ve istemci (burada hata almıyorsan böyle kalabilir)
from google import genai
client = genai.Client(api_key=GENAI_API_KEY)

# EasyOCR Reader
reader = easyocr.Reader(['tr'])

def take_screenshot(url, save_path="screenshot.png"):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/114.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)
    driver.save_screenshot(save_path)
    driver.quit()
    print(Fore.CYAN + f"📸 Ekran görüntüsü alındı: {save_path}")
    
def ocr_easyocr(image_path):
    result = reader.readtext(image_path, detail=0)
    return "\n".join(result)

def check_stock_status(text, filename="zara_ocr_output.txt"):
    if "BENZER ÜRÜNLER TÜKENDİ" in text:
        status = "ürün stoğu yok"
    elif "EKLE" in text:
        status = "ürün stoğu var"
    else:
        status = "stok durumu bilinmiyor"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(status)
    return status

def pretty_print_ocr_text(text):
    print(Fore.MAGENTA + "📄 OCR'den çıkan metin:\n")
    lines = text.split('\n')
    for i, line in enumerate(filter(None, map(str.strip, lines)), 1):
        print(Fore.LIGHTBLUE_EX + f"{i}. {line}")

def ai_response(text, retries=3, wait_sec=180):
    prompt = f"""
Aşağıda bir ürün sayfasından OCR ile çıkarılmış metin var:

{text}

Lütfen bu metni incele ve şunları yap:

1. Eğer metinde "Benzer Ürünler Tükendi" ifadesi varsa, "[-] ÜRÜN STOĞU YOK" yaz.
2. Eğer metinde "Ekle" kelimesi geçiyorsa, "[+] ÜRÜN STOĞU VAR" yaz.
3. Eğer her ikisi de yoksa, "[--] STOK DURUMU BİLİNMİYOR" yaz.
4. Çıktı da ürün stok yoksa 
➖ ÜRÜN STOĞU YOK ❌
Üzgünüz, bu ürün şu anda tükendi.
bunu kullan

Ürün stok varsa

➕ ÜRÜN STOĞU VAR ✅
Harika! Bu ürün şu an stokta.

bunu kullan

stok durumu bilinmiyorsa

🔄 STOK DURUMU BİLİNMİYOR ❔
Ürün hakkında net bilgi alınamadı.

bunu

`` bunu falan da kullanma sadece metin olcak
"""
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Hata: {e} - {attempt}. deneme")
            if attempt < retries:
                print(f"{wait_sec} saniye bekleniyor ve tekrar deneniyor...")
                time.sleep(wait_sec)
            else:
                return "⚠️ API hatası: Model şu anda aşırı yüklü veya erişilemiyor."


async def send_telegram_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        print(Fore.GREEN + "📨 Telegram mesajı gönderildi.")
    except Exception as e:
        print(Fore.RED + f"Telegram mesaj gönderme hatası: {e}")

def send_photo_to_telegram(photo_path, caption="Ürün ekran görüntüsü"):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, "rb") as photo:
            files = {"photo": photo}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print(Fore.GREEN + "🖼️ Fotoğraf Telegram'a gönderildi.")
        else:
            print(Fore.RED + f"Fotoğraf gönderilemedi: {response.text}")
    except Exception as e:
        print(Fore.RED + f"Fotoğraf gönderme hatası: {e}")

async def process_and_notify(image_path):
    ocr_text = ocr_easyocr(image_path)
    pretty_print_ocr_text(ocr_text)

    stock_status = check_stock_status(ocr_text)
    print(Fore.CYAN + f"📦 Stok durumu: {stock_status}")

    ai_text = ai_response(ocr_text)
    print(Fore.LIGHTYELLOW_EX + f"\n🤖 GenAI cevabı:\n{ai_text}")

    with open("genai_response.txt", "w", encoding="utf-8") as f:
        f.write(ai_text)

    await send_telegram_message(ai_text)
    

def main_loop():
    screenshot_file = "zara_product.png"

    while True:
        start = time.perf_counter()

        try:
            take_screenshot(URL, screenshot_file)
            send_photo_to_telegram(screenshot_file, caption="🔁 5 dakika arayla güncel ürün ekran görüntüsü")
            asyncio.run(process_and_notify(screenshot_file))

            if os.path.exists(screenshot_file):
                os.remove(screenshot_file)

        except Exception as e:
            print(Fore.RED + f"HATA ❌ {e}")

        end = time.perf_counter()
        elapsed = round(end - start, 2)

        print(Fore.CYAN + f"⏱️ İşlem süresi: {elapsed} saniye")
        print(Fore.YELLOW + "⏳ 3 dakika bekleniyor...\n")
        time.sleep(180)

if __name__ == "__main__":
    main_loop()
