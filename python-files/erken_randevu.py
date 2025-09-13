import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
from dateutil.relativedelta import relativedelta
import threading
import asyncio
import random
import time
import subprocess
import os
import requests
import json

from playwright.async_api import async_playwright

# Telegram Ayarları
TELEGRAM_TOKEN = "8495675499:AAG6amhk5gyTVm6sMe1cFgO-Jk-SOzC8WBQ"
TELEGRAM_CHAT_ID = "6588175890"

def telegram_notify(token, chat_id, text, kullanici_adi=""):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    try:
        # Kullanıcı adı varsa mesaja ekle
        if kullanici_adi:
            text = f"[{kullanici_adi}] {text}"
        
        response = requests.post(url, data={'chat_id': chat_id, 'text': text})
        print('Telegram bildirimi gönderildi!' if response.status_code == 200 else f'Telegram bildirimi başarısız: {response.text}')
    except Exception as e:
        print('Telegram bildirimi hatası:', e)

def chrome_baslat_kullanici_icin(kullanici, log_func=None):
    """Belirli bir kullanıcı için Chrome'u başlatır"""
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        profil_yolu = kullanici["profil_yolu"]
        port = kullanici["port"]
        
        # Dosya yolu boşluk içeriyorsa tırnak içine al
        chrome_path = f'"{chrome_path}"' if " " in chrome_path else chrome_path
        profil_yolu = f'"{profil_yolu}"' if " " in profil_yolu else profil_yolu
        
        command = f'{chrome_path} --remote-debugging-port={port} --user-data-dir={profil_yolu}'
        
        subprocess.Popen(command, shell=True)
        
        if log_func:
            log_func(f"Chrome başlatıldı: {kullanici['ad']} (Port: {port})")
        
        return True
    except Exception as e:
        if log_func:
            log_func(f"Chrome başlatma hatası ({kullanici['ad']}): {e}")
        return False

def tum_kullanicilar_icin_chrome_baslat(log_func=None):
    """Tüm kullanıcılar için Chrome'u başlatır"""
    basarili = 0
    for kullanici in KULLANICILAR:
        if chrome_baslat_kullanici_icin(kullanici, log_func):
            basarili += 1
            # Her Chrome başlatma arasında kısa bekleme
            time.sleep(2)
    
    if log_func:
        log_func(f"Toplam {basarili}/{len(KULLANICILAR)} kullanıcı için Chrome başlatıldı")
    
    return basarili

async def human_delay(min_ms=300, max_ms=1200):
    await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

# Yardımcı: Ayı int'ten (0-11) İngilizce kısa isme çevirir
MONTH_IDX_TO_NAME = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Şehir ID'leri
SEHIRLER = {
    'İSTANBUL': '84cf7716-ccb5-ef11-b8e9-001dd80637a9',
    'ANKARA':   '5eb31865-cbb5-ef11-b8e9-001dd80637a9'
}

# Çoklu Kullanıcı Tanımları - JSON dosyasından yüklenecek
KULLANICILAR = []

def kullanicilar_yukle():
    """Kullanıcıları JSON dosyasından yükler"""
    global KULLANICILAR
    try:
        with open("kullanicilar.json", "r", encoding="utf-8") as f:
            KULLANICILAR = json.load(f)
        print(f"{len(KULLANICILAR)} kullanıcı yüklendi")
    except FileNotFoundError:
        # Dosya yoksa varsayılan kullanıcıları oluştur
        KULLANICILAR = [
            {
                "ad": "Ahmet",
                "profil_yolu": r"C:\Users\Mustafa Ali Taş\AppData\Local\Google\Chrome\User Data\Profil1",
                "port": 9222,
                "sehir": "İSTANBUL",
                "baslangic": "2025-09-01",
                "bitis": "2025-09-20",
                "telegram_chat_id": "6588175890"
            },
            {
                "ad": "Mehmet",
                "profil_yolu": r"C:\Users\Mustafa Ali Taş\AppData\Local\Google\Chrome\User Data\Profil2",
                "port": 9223,
                "sehir": "ANKARA",
                "baslangic": "2025-09-10",
                "bitis": "2025-10-10",
                "telegram_chat_id": "6588175890"
            }
        ]
        kullanicilar_kaydet()
        print("Varsayılan kullanıcılar oluşturuldu ve kaydedildi")

def kullanicilar_kaydet():
    """Kullanıcıları JSON dosyasına kaydeder"""
    try:
        with open("kullanicilar.json", "w", encoding="utf-8") as f:
            json.dump(KULLANICILAR, f, ensure_ascii=False, indent=2)
        print("Kullanıcılar kaydedildi")
    except Exception as e:
        print(f"Kullanıcı kaydetme hatası: {e}")

def kullanici_ekle(yeni_kullanici):
    """Yeni kullanıcı ekler ve dosyaya kaydeder"""
    KULLANICILAR.append(yeni_kullanici)
    kullanicilar_kaydet()
    print(f"Yeni kullanıcı eklendi: {yeni_kullanici['ad']}")

# Program başlangıcında kullanıcıları yükle
kullanicilar_yukle()

async def insan_gibi_hareket_et(page, log_func=None):
    scroll_y = random.randint(0, 1500)
    await page.evaluate(f'window.scrollTo(0, {scroll_y});')
    await asyncio.sleep(random.uniform(0.2, 1.0))
    width = await page.evaluate('() => document.body.clientWidth')
    height = await page.evaluate('() => document.body.clientHeight')
    mouse_x = random.randint(50, max(51, width-50))
    mouse_y = random.randint(80, max(81, height-80))
    await page.mouse.move(mouse_x, mouse_y)
    await asyncio.sleep(random.uniform(0.1, 0.7))
    try:
        if random.random() < 0.7:
            title_elem = await page.query_selector('.ui-datepicker-title')
            if title_elem:
                await title_elem.hover()
                await asyncio.sleep(random.uniform(0.1, 0.4))
        elif random.random() < 0.5:
            inputs = await page.query_selector_all('input, button, select')
            if inputs:
                elem = random.choice(inputs)
                await elem.hover()
                await asyncio.sleep(random.uniform(0.1, 0.3))
    except:
        pass
    if log_func:
        log_func('İnsani hareket (scroll, mouse, hover) yapıldı.')

async def takvimde_tarih_araliginda_kontrol_et(page, tarih_baslangic, tarih_bitis, log_func):
    # String to date obj
    if isinstance(tarih_baslangic, str):
        baslangic = datetime.datetime.strptime(tarih_baslangic, "%Y-%m-%d").date()
    else:
        baslangic = tarih_baslangic
    if isinstance(tarih_bitis, str):
        bitis = datetime.datetime.strptime(tarih_bitis, "%Y-%m-%d").date()
    else:
        bitis = tarih_bitis

    # Her ayı gez
    aktif_ay = baslangic.replace(day=1)
    bitis_ay = bitis.replace(day=1)

    while aktif_ay <= bitis_ay:
        try:
            # 1. Yıl select'ini ve Ay select'ini bul
            log_func(f"{aktif_ay.strftime('%B %Y')} takvimde seçiliyor...")

            # Takvim elementlerinin yüklenmesini bekle
            try:
                await page.wait_for_selector('.ui-datepicker-month', timeout=5000)
                await page.wait_for_selector('.ui-datepicker-year', timeout=5000)
            except Exception as e:
                log_func(f"Takvim elementleri bulunamadı: {e}")
                return None

            # Ay select'ini güncelle
            ay_idx = aktif_ay.month - 1  # 0-index!
            await page.select_option('.ui-datepicker-month', value=str(ay_idx))
            await asyncio.sleep(0.5)
            # Yıl select'ini güncelle
            await page.select_option('.ui-datepicker-year', value=str(aktif_ay.year))
            await asyncio.sleep(1)

            # O ayda tıklanabilir günler
            days = await page.query_selector_all('.ui-datepicker-calendar td:not(.ui-datepicker-unselectable) a.ui-state-default')
            for day_elem in days:
                day_number = int(await day_elem.inner_text())
                gun_tarih = aktif_ay.replace(day=day_number)
                if baslangic <= gun_tarih <= bitis:
                    log_func(f"{gun_tarih} tarihinde tıklanabilir uygun gün bulundu, tıklanıyor...")
                    await day_elem.hover()
                    await asyncio.sleep(0.5)
                    await day_elem.click()
                    return gun_tarih  # Uygun gün bulundu ve tıklandı!

            aktif_ay += relativedelta(months=1)
            
        except Exception as e:
            log_func(f"Takvim kontrolü sırasında hata: {e}")
            return None

    log_func("Tüm tarih aralığı gezildi, uygun gün bulunamadı.")
    return None

# Otomasyon Fonksiyonu
async def run_playwright_otomasyon(kullanici, log_func, stop_event, completion_callback=None):
    """Belirli bir kullanıcı için otomasyon çalıştırır"""
    try:
        log_func(f"[{kullanici['ad']}] Mevcut Chrome'a bağlanılıyor (Port: {kullanici['port']})...")
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{kullanici['port']}")
            pages = browser.contexts[0].pages
            if pages:
                page = pages[-1]
            else:
                page = await browser.contexts[0].new_page()
            log_func(f"[{kullanici['ad']}] Otomasyon sayfası hazır, döngü başlıyor...")
            
            dongu_sayaci = 0
            
            while not stop_event.is_set():  # Durdurma flag'i kontrol edilerek döngü
                dongu_sayaci += 1
                # Şehir seçimi
                sehir = kullanici["sehir"]
                sehir_id = SEHIRLER[sehir]
                log_func(f"[{kullanici['ad']}] {sehir} seçiliyor, takvim kontrol ediliyor...")
                await page.select_option('#post_select', value=sehir_id)
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # İnsani hareket yap
                await insan_gibi_hareket_et(page, lambda msg: log_func(f"[{kullanici['ad']}] {msg}"))
                
                # Durdurma kontrolü
                if stop_event.is_set():
                    break
                
                # Durdurma kontrolü
                if stop_event.is_set():
                    break
                
                # Takvimde belirtilen tarih aralığında uygun günleri kontrol et
                tarih_bulundu = await takvimde_tarih_araliginda_kontrol_et(
                    page, kullanici["baslangic"], kullanici["bitis"], 
                    lambda msg: log_func(f"[{kullanici['ad']}] {msg}")
                )
                if tarih_bulundu:
                    # ... uygun gün seçildi
                    await asyncio.sleep(1)

                    # GÜN TIKLANDIKTAN SONRA SAAT TABLOSUNU KONTROL ET
                    try:
                        # 1) Saat tablosu kısa sürede geldi mi?
                        await page.wait_for_selector('#time_select', timeout=5000)
                        rows = await page.query_selector_all('#time_select tbody tr')
                        if rows is None or len(rows) == 0:
                            raise Exception("Saat tablosu boş")

                    except Exception as e:
                        log_func(f"[{kullanici['ad']}] UYARI: Saat seçenekleri görünmedi (başkası almış olabilir): {e}")

                        # (Opsiyonel değil) – bir sonraki deneme daha temiz başlasın
                        try:
                            await page.select_option('#post_select', value="")  # konsolosluğu tekrar boşalt
                        except:
                            pass

                        # Biraz insani davranış ve rate-limit uyumlu bekleme
                        await insan_gibi_hareket_et(page, log_func=log_func)

                        bekleme_suresi = random.randint(15, 20)  # sahadaki güvenli aralık
                        log_func(f"[{kullanici['ad']}] {bekleme_suresi} saniye bekleniyor (saat tablosu gelmedi)...")
                        for _ in range(bekleme_suresi):
                            if stop_event.is_set():
                                break
                            await asyncio.sleep(1)

                        # Bu günü boş kabul ederek döngünün başına dön
                        continue

                    # Saat tablosu kontrolü (daha önceki patch’in aynen kalsın)
                    await page.wait_for_selector('#time_select', timeout=5000)
                    rows = await page.query_selector_all('#time_select tbody tr')
                    if not rows or len(rows) == 0:
                        raise Exception("Saat tablosu boş")

                    log_func(f"[{kullanici['ad']}] {len(rows)} saat bulundu. Hepsi sırayla denenecek…")

                    # Satır sayısı kadar iterasyon yapacağız.
                    # DOM her tıklamada değişebildiği için her turda satırı tekrar buluyoruz.
                    for i in range(len(rows)):
                        if stop_event.is_set():
                            break

                        row_sel = f'#time_select tbody tr:nth-child({i+1})'
                        try:
                            # Satırdaki radio ve saat metnini al
                            radio = await page.query_selector(f'{row_sel} input[name="schedule-entries"]')
                            if not radio:
                                continue

                            saat_el = await page.query_selector(f'{row_sel} td:nth-child(2) div')
                            saat_text = (await saat_el.inner_text()).strip() if saat_el else "Saat?"

                            # Radio’yu seç
                            await radio.scroll_into_view_if_needed()
                            await radio.hover()
                            await asyncio.sleep(0.25)
                            await radio.click()

                            # Gönder
                            gonder_btn = await page.query_selector('#submitbtn')
                            if gonder_btn:
                                await gonder_btn.hover()
                                await asyncio.sleep(0.3)
                                await gonder_btn.click()

                                log_func(f"[{kullanici['ad']}] Gönder’e basıldı: {saat_text}. Tarama devam edecek.")
                                # Telegram bilgilendirmesi (durmadan)
                                telegram_chat_id = kullanici.get("telegram_chat_id", TELEGRAM_CHAT_ID)
                                if TELEGRAM_TOKEN and telegram_chat_id:
                                    try:
                                        telegram_notify(
                                            TELEGRAM_TOKEN,
                                            telegram_chat_id,
                                            f"🟢 [**{kullanici['ad']}**] Gönderildi: {tarih_bulundu} {saat_text} (Şehir: {sehir}). Tarama **devam ediyor**.",
                                            kullanici['ad']
                                        )
                                    except Exception as te:
                                        log_func(f"[{kullanici['ad']}] Telegram gönderilemedi: {te}")

                                # Sunucu yanıtına alan açmak için çok kısa nefes; rate-limit’i germeyelim
                                await asyncio.sleep(random.uniform(0.5, 1.0))

                            else:
                                log_func(f"[{kullanici['ad']}] Gönder butonu bulunamadı (saat: {saat_text}).")

                        except Exception as e:
                            log_func(f"[{kullanici['ad']}] {i+1}. saat seçimi sırasında hata: {e}")
                            # Çok kısa nefes al, sonraki saate geç
                            await asyncio.sleep(0.1)

                    # Burada **break/return yok** — tüm saatler denendikten sonra ana döngü bekleme/tarama ile devam eder.
                else:
                    # Hiçbir gün bulunamadı, döngüye devam et
                    log_func(f"[{kullanici['ad']}] Uygun tarih bulunamadı, Konsolosluk seçimi boşaltılıyor ve bekleniyor...")
                    await page.select_option('#post_select', value="")
                    await asyncio.sleep(random.uniform(1.0, 2.0))
                    
                    # İnsani hareket yap
                    await insan_gibi_hareket_et(page, lambda msg: log_func(f"[{kullanici['ad']}] {msg}"))

                # Durdurma kontrolü
                if stop_event.is_set():
                    break

                # (reload logic removed)

                # Döngüde insani aralıkla bekle (16-26 saniye)
                bekleme_suresi = random.randint(16, 26)
                log_func(f"{bekleme_suresi} saniye bekleniyor...")
                
                for i in range(bekleme_suresi):
                    if stop_event.is_set():
                        break
                    await asyncio.sleep(1)

    except Exception as e:
        error_msg = f"[{kullanici['ad']}] HATA: {str(e)}"
        log_func(error_msg)
        # Telegram hata bildirimi
        telegram_chat_id = kullanici.get("telegram_chat_id", TELEGRAM_CHAT_ID)
        if TELEGRAM_TOKEN and telegram_chat_id:
            telegram_notify(TELEGRAM_TOKEN, telegram_chat_id, f"❌ OTOMASYON HATASI: {str(e)}", kullanici['ad'])
    finally:
        # Otomasyon bittiğinde buton durumlarını güncelle
        log_func(f"[{kullanici['ad']}] Otomasyon tamamlandı.")
        # GUI thread'inde buton durumlarını güncelle
        if completion_callback:
            completion_callback(kullanici['ad'])

# Tkinter GUI
class RandevuBotu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Amerika Erken Randevu Botu - Çoklu Kullanıcı")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Her kullanıcı için ayrı stop_event ve thread
        self.kullanici_threads = {}
        self.kullanici_stop_events = {}
        self.kullanici_buttons = {}

        self.notebook = ttk.Notebook(self)
        self.tab_chrome = ttk.Frame(self.notebook)
        self.tab_users = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)
        self.tab_add_user = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chrome, text="Chrome Yönetimi")
        self.notebook.add(self.tab_users, text="Kullanıcı Yönetimi")
        self.notebook.add(self.tab_logs, text="İşlem Kayıtları")
        self.notebook.add(self.tab_add_user, text="Kullanıcı Ekle")
        self.notebook.pack(expand=1, fill="both")

        # Her kullanıcı için ayrı log ekranları
        self.kullanici_log_ekranlari = {}
        self.kullanici_status_ikonlari = {}
        self.kullanici_progress_bars = {}

        self.create_chrome_tab()
        self.create_users_tab()
        self.create_logs_tab()
        self.create_add_user_tab()

    def create_chrome_tab(self):
        frame = ttk.Frame(self.tab_chrome)
        frame.pack(padx=20, pady=15, fill="both", expand=True)

        # Chrome Yönetimi Başlığı
        ttk.Label(frame, text="Chrome Yönetimi", font=("Arial", 14, "bold")).pack(pady=10)

        # Tüm Kullanıcılar için Chrome Başlat
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        self.btn_chrome_all = ttk.Button(btn_frame, text="Tüm Kullanıcılar için Chrome Başlat", 
                                        command=self.tum_kullanicilar_icin_chrome_baslat)
        self.btn_chrome_all.pack(pady=5)

        # Kullanıcı Listesi
        list_frame = ttk.LabelFrame(frame, text="Kullanıcı Listesi")
        list_frame.pack(fill="both", expand=True, pady=10)

        # Treeview ile kullanıcı listesi
        columns = ("Ad", "Port", "Şehir", "Başlangıç", "Bitiş", "Profil")
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        self.user_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Kullanıcıları listeye ekle
        self.refresh_user_list()

    def create_users_tab(self):
        frame = ttk.Frame(self.tab_users)
        frame.pack(padx=20, pady=15, fill="both", expand=True)

        # Kullanıcı Yönetimi Başlığı
        ttk.Label(frame, text="Kullanıcı Otomasyon Yönetimi", font=("Arial", 14, "bold")).pack(pady=10)

        # Scrollable frame için canvas
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Kullanıcı butonları için frame
        self.users_frame = scrollable_frame

        # Kullanıcı butonlarını oluştur
        self.create_user_buttons()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_user_buttons(self):
        # Mevcut butonları temizle
        for widget in self.users_frame.winfo_children():
            widget.destroy()

        # Her kullanıcı için buton oluştur
        for i, kullanici in enumerate(KULLANICILAR):
            user_frame = ttk.LabelFrame(self.users_frame, text=f"Kullanıcı: {kullanici['ad']}")
            user_frame.pack(fill="x", pady=5, padx=10)

            # Üst satır: Bilgiler ve durum
            top_frame = ttk.Frame(user_frame)
            top_frame.pack(fill="x", pady=5)
            
            # Kullanıcı bilgileri
            info_label = ttk.Label(top_frame, text=f"Port: {kullanici['port']} | Şehir: {kullanici['sehir']} | Tarih: {kullanici['baslangic']} - {kullanici['bitis']}")
            info_label.pack(side="left")

            # Status ikonu
            status_icon = ttk.Label(top_frame, text="🟡", font=("Arial", 16))
            status_icon.pack(side="right", padx=10)
            self.kullanici_status_ikonlari[kullanici['ad']] = status_icon

            # Progress bar
            progress_frame = ttk.Frame(user_frame)
            progress_frame.pack(fill="x", pady=2)
            
            progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=200, mode='determinate')
            progress_bar.pack(side="left", padx=5)
            self.kullanici_progress_bars[kullanici['ad']] = progress_bar

            # Progress yüzde etiketi
            progress_label = ttk.Label(progress_frame, text="0%")
            progress_label.pack(side="left", padx=5)
            self.kullanici_progress_labels = getattr(self, 'kullanici_progress_labels', {})
            self.kullanici_progress_labels[kullanici['ad']] = progress_label

            # Butonlar
            btn_frame = ttk.Frame(user_frame)
            btn_frame.pack(fill="x", pady=5)

            # Başlat butonu
            start_btn = ttk.Button(btn_frame, text="Başlat", 
                                  command=lambda k=kullanici: self.baslat_kullanici_otomasyon(k))
            start_btn.pack(side="left", padx=5)

            # Durdur butonu
            stop_btn = ttk.Button(btn_frame, text="Durdur", state="disabled",
                                 command=lambda k=kullanici: self.durdur_kullanici_otomasyon(k))
            stop_btn.pack(side="left", padx=5)

            # Chrome başlat butonu
            chrome_btn = ttk.Button(btn_frame, text="Chrome Başlat",
                                   command=lambda k=kullanici: self.chrome_baslat_kullanici(k))
            chrome_btn.pack(side="left", padx=5)

            # Butonları sakla
            self.kullanici_buttons[kullanici['ad']] = {
                'start': start_btn,
                'stop': stop_btn,
                'chrome': chrome_btn
            }

    def create_logs_tab(self):
        """Her kullanıcı için ayrı log ekranları oluşturur"""
        frame = ttk.Frame(self.tab_logs)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Scrollable frame için canvas
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Her kullanıcı için log ekranı oluştur
        for kullanici in KULLANICILAR:
            log_frame = ttk.LabelFrame(scrollable_frame, text=f"Log: {kullanici['ad']}")
            log_frame.pack(fill="x", pady=5, padx=5)

            # Log text widget
            log_text = tk.Text(log_frame, height=8, state="disabled", bg="#20232A", fg="#E0E0E0", font=("Consolas", 9))
            log_text.pack(fill="both", expand=True, padx=5, pady=5)

            # Log ekranını sakla
            self.kullanici_log_ekranlari[kullanici['ad']] = log_text

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_add_user_tab(self):
        """Kullanıcı ekleme formu oluşturur"""
        frame = ttk.Frame(self.tab_add_user)
        frame.pack(padx=20, pady=15, fill="both", expand=True)

        # Başlık
        ttk.Label(frame, text="Yeni Kullanıcı Ekle", font=("Arial", 14, "bold")).pack(pady=10)

        # Form frame
        form_frame = ttk.LabelFrame(frame, text="Kullanıcı Bilgileri")
        form_frame.pack(fill="x", pady=10, padx=10)

        # Form alanları
        fields = [
            ("Kullanıcı Adı:", "ad"),
            ("Chrome Profil Yolu:", "profil_yolu"),
            ("Port:", "port"),
            ("Şehir:", "sehir"),
            ("Başlangıç Tarihi:", "baslangic"),
            ("Bitiş Tarihi:", "bitis"),
            ("Telegram Chat ID (İsteğe bağlı):", "telegram_chat_id")
        ]

        self.add_user_entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            if field_name == "port":
                entry = ttk.Entry(form_frame, width=30)
                entry.insert(0, str(9222 + len(KULLANICILAR)))  # Otomatik port
            elif field_name == "sehir":
                entry = ttk.Combobox(form_frame, values=["İSTANBUL", "ANKARA"], width=27, state="readonly")
                entry.current(0)
            elif field_name in ["baslangic", "bitis"]:
                entry = DateEntry(form_frame, width=25, date_pattern="yyyy-mm-dd", mindate=datetime.date.today())
            else:
                entry = ttk.Entry(form_frame, width=30)
                if field_name == "profil_yolu":
                    entry.insert(0, r"C:\Users\Mustafa Ali Taş\AppData\Local\Google\Chrome\User Data\Profil" + str(len(KULLANICILAR) + 1))
                elif field_name == "telegram_chat_id":
                    entry.insert(0, TELEGRAM_CHAT_ID)
            
            entry.grid(row=i, column=1, sticky="w", pady=5, padx=5)
            self.add_user_entries[field_name] = entry

        # Butonlar
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Kullanıcı Ekle", command=self.add_new_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Formu Temizle", command=self.clear_add_user_form).pack(side="left", padx=5)

    def refresh_user_list(self):
        # Mevcut listeyi temizle
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        # Kullanıcıları listeye ekle
        for kullanici in KULLANICILAR:
            self.user_tree.insert("", "end", values=(
                kullanici['ad'],
                kullanici['port'],
                kullanici['sehir'],
                kullanici['baslangic'],
                kullanici['bitis'],
                kullanici['profil_yolu'].split('\\')[-1]  # Sadece profil adı
            ))

    def write_log(self, msg, kullanici_adi=None):
        """Genel log yazma fonksiyonu"""
        if kullanici_adi and kullanici_adi in self.kullanici_log_ekranlari:
            # Kullanıcıya özel log
            self.write_user_log(kullanici_adi, msg)
        else:
            # Genel log (eski davranış)
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

    def write_user_log(self, kullanici_adi, msg):
        """Belirli bir kullanıcının log ekranına yazar"""
        if kullanici_adi in self.kullanici_log_ekranlari:
            log_text = self.kullanici_log_ekranlari[kullanici_adi]
            log_text.config(state="normal")
            log_text.insert("end", f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
            log_text.see("end")
            log_text.config(state="disabled")

    def update_user_status(self, kullanici_adi, status):
        """Kullanıcının durum ikonunu günceller"""
        if kullanici_adi in self.kullanici_status_ikonlari:
            icon_map = {
                "hazir": "🟡",
                "calisiyor": "🟢", 
                "durduruldu": "🔴",
                "hata": "🔴"
            }
            icon = icon_map.get(status, "🟡")
            self.kullanici_status_ikonlari[kullanici_adi].config(text=icon)

    def update_user_progress(self, kullanici_adi, progress_percent):
        """Kullanıcının progress bar'ını günceller"""
        if kullanici_adi in self.kullanici_progress_bars:
            self.kullanici_progress_bars[kullanici_adi]['value'] = progress_percent
            if kullanici_adi in self.kullanici_progress_labels:
                self.kullanici_progress_labels[kullanici_adi].config(text=f"{progress_percent:.1f}%")

    def add_new_user(self):
        """Yeni kullanıcı ekler"""
        try:
            # Form verilerini al
            yeni_kullanici = {}
            for field_name, entry in self.add_user_entries.items():
                if field_name in ["baslangic", "bitis"]:
                    # DateEntry'den tarih al
                    yeni_kullanici[field_name] = entry.get_date().strftime("%Y-%m-%d")
                else:
                    yeni_kullanici[field_name] = entry.get()
            
            # Validasyon
            if not yeni_kullanici["ad"]:
                messagebox.showerror("Hata", "Kullanıcı adı boş olamaz!")
                return
            
            if not yeni_kullanici["profil_yolu"]:
                messagebox.showerror("Hata", "Profil yolu boş olamaz!")
                return
            
            try:
                port = int(yeni_kullanici["port"])
                if port < 1024 or port > 65535:
                    messagebox.showerror("Hata", "Port 1024-65535 arasında olmalıdır!")
                    return
            except ValueError:
                messagebox.showerror("Hata", "Port geçerli bir sayı olmalıdır!")
                return
            
            # Kullanıcı adı benzersiz mi kontrol et
            if any(k["ad"] == yeni_kullanici["ad"] for k in KULLANICILAR):
                messagebox.showerror("Hata", "Bu kullanıcı adı zaten kullanılıyor!")
                return
            
            # Port benzersiz mi kontrol et
            if any(k["port"] == port for k in KULLANICILAR):
                messagebox.showerror("Hata", "Bu port zaten kullanılıyor!")
                return
            
            # Kullanıcıyı ekle
            kullanici_ekle(yeni_kullanici)
            
            # GUI'yi güncelle
            self.refresh_user_list()
            self.create_user_buttons()
            self.create_logs_tab()
            
            messagebox.showinfo("Başarılı", f"Kullanıcı '{yeni_kullanici['ad']}' başarıyla eklendi!")
            
            # Formu temizle
            self.clear_add_user_form()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Kullanıcı eklenirken hata oluştu: {e}")

    def clear_add_user_form(self):
        """Kullanıcı ekleme formunu temizler"""
        for field_name, entry in self.add_user_entries.items():
            if field_name == "port":
                entry.delete(0, tk.END)
                entry.insert(0, str(9222 + len(KULLANICILAR)))
            elif field_name == "sehir":
                entry.current(0)
            elif field_name in ["baslangic", "bitis"]:
                # DateEntry'yi bugünün tarihine ayarla
                entry.set_date(datetime.date.today())
            elif field_name == "profil_yolu":
                entry.delete(0, tk.END)
                entry.insert(0, r"C:\Users\Mustafa Ali Taş\AppData\Local\Google\Chrome\User Data\Profil" + str(len(KULLANICILAR) + 1))
            elif field_name == "telegram_chat_id":
                entry.delete(0, tk.END)
                entry.insert(0, TELEGRAM_CHAT_ID)
            else:
                entry.delete(0, tk.END)

    def tum_kullanicilar_icin_chrome_baslat(self):
        """Tüm kullanıcılar için Chrome'u başlatır"""
        print("Tüm kullanıcılar için Chrome başlatılıyor...")
        basarili = tum_kullanicilar_icin_chrome_baslat(print)
        if basarili > 0:
            messagebox.showinfo("Başarılı", f"{basarili} kullanıcı için Chrome başlatıldı!\n\nHer pencerede giriş yapıp randevu sayfasına gelin.")
        else:
            messagebox.showerror("Hata", "Hiçbir Chrome başlatılamadı!")

    def chrome_baslat_kullanici(self, kullanici):
        """Belirli bir kullanıcı için Chrome'u başlatır"""
        kullanici_adi = kullanici['ad']
        print(f"{kullanici_adi} için Chrome başlatılıyor...")
        if chrome_baslat_kullanici_icin(kullanici, print):
            messagebox.showinfo("Başarılı", f"{kullanici_adi} için Chrome başlatıldı!\n\nAçılan pencerede giriş yapıp randevu sayfasına gelin.")
        else:
            messagebox.showerror("Hata", f"{kullanici_adi} için Chrome başlatılamadı!")

    def baslat_kullanici_otomasyon(self, kullanici):
        """Belirli bir kullanıcı için otomasyon başlatır"""
        kullanici_adi = kullanici['ad']
        
        # Eğer zaten çalışıyorsa başlatma
        if kullanici_adi in self.kullanici_threads and self.kullanici_threads[kullanici_adi].is_alive():
            self.write_user_log(kullanici_adi, "Otomasyon zaten çalışıyor!")
            return

        # Stop event oluştur
        self.kullanici_stop_events[kullanici_adi] = threading.Event()
        
        # Buton durumlarını güncelle
        self.kullanici_buttons[kullanici_adi]['start'].config(state="disabled")
        self.kullanici_buttons[kullanici_adi]['stop'].config(state="normal")
        
        # Durum güncelle
        self.update_user_status(kullanici_adi, "calisiyor")
        self.update_user_progress(kullanici_adi, 0)
        
        self.write_user_log(kullanici_adi, f"Otomasyon başlatılıyor: {kullanici['sehir']} | {kullanici['baslangic']} - {kullanici['bitis']}")
        
        # Thread başlat
        thread = threading.Thread(
            target=lambda: asyncio.run(
                run_playwright_otomasyon(kullanici, 
                                       lambda msg: self.write_user_log(kullanici_adi, msg),
                                       self.kullanici_stop_events[kullanici_adi], 
                                       lambda ad: self.otomasyon_tamamlandi(ad))
            ),
            daemon=True
        )
        self.kullanici_threads[kullanici_adi] = thread
        thread.start()

    def durdur_kullanici_otomasyon(self, kullanici):
        """Belirli bir kullanıcı için otomasyon durdurur"""
        kullanici_adi = kullanici['ad']
        
        if kullanici_adi in self.kullanici_stop_events:
            self.kullanici_stop_events[kullanici_adi].set()
            self.write_user_log(kullanici_adi, "Otomasyon durduruluyor...")
            
            # Durum güncelle
            self.update_user_status(kullanici_adi, "durduruldu")
            self.update_user_progress(kullanici_adi, 0)
            
            # Buton durumlarını güncelle
            self.kullanici_buttons[kullanici_adi]['start'].config(state="normal")
            self.kullanici_buttons[kullanici_adi]['stop'].config(state="disabled")

    def otomasyon_tamamlandi(self, kullanici_adi):
        """Otomasyon tamamlandığında GUI'yi güncelle"""
        # GUI thread'inde güvenli güncelleme
        self.after(0, lambda: self._update_buttons_after_completion(kullanici_adi))

    def _update_buttons_after_completion(self, kullanici_adi):
        """Otomasyon tamamlandıktan sonra butonları günceller"""
        if kullanici_adi in self.kullanici_buttons:
            self.kullanici_buttons[kullanici_adi]['start'].config(state="normal")
            self.kullanici_buttons[kullanici_adi]['stop'].config(state="disabled")
            
            # Durum güncelle
            self.update_user_status(kullanici_adi, "hazir")
            self.update_user_progress(kullanici_adi, 0)

if __name__ == "__main__":
    app = RandevuBotu()
    app.mainloop()
