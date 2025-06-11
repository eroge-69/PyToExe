import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import requests
import json
from PIL import Image, ImageTk
import io
import threading # Arka planda arama yapmak için threading modülü
import time # Aramalar arasında kısa bir gecikme için

# ==============================================================================
# STARDOLL İLE İLGİLİ SABİT AYARLAR VE ÇEREZLER
# ==============================================================================

# Stardoll markaları için ID listesi
BRAND_IDS = {
    "Seçiniz (Tüm Markalar)": None,

    # DECOR LINK, BRAND NUMBERS
    "Tingeling": 18, "Golden Sands": 37, "Folk": 44, "Fallen Angel DECOR": 45,
    "Bling Bling": 46, "Kitsch": 47, "Glamour": 48, "Fashion Furniture": 49,
    "Budding Love": 51, "Minimalism": 52, "Roots": 53, "Seasonal": 54,
    "Pretty in Pink": 55, "Villa": 57, "Fusion Design": 78, "Evil Panda": 92,
    "An existing brand, with no name": 96, "LIMITED EDITION": 101, "ANTIDOTE": 117,
    "Tingeling Halloween COUTURE": 183, "Decade": 206, "Chanel (Decor)": 207,
    "DIY": 229, "Sunny Bunny (Decor)": 252, "Glow": 312, "Gamezone": 319,
    "Other Week": 343, "PopShop": 365, "Falling Angel": 379, "Windows on the World": 382,
    "LP Decor": 385, "Pet & Porter": 397, "Golden Sands (v2)": 410,
    "Fantasy Hotel": 413, "Sea of Stars": 437, "Museum Bits": 468, "Magic": 496,
    "Winter Peek": 527, "Apoca Ski": 530, "Wild West": 550, "Mellonair": 564,
    "Mellonair Mansion": 588, "Royalty (Decor)": 660, "Pretty n Love Decor": 712,
    "Callies Picks (Decor)": 727, "Furry Friends": 829, "Birds Eye": 888,
    "Pois (Decor)": 889, "Red Mod (Decor)": 920, "Callies Picks DECOR": 947,
    "Heritage Classic TRIBUTE": 963, "John Galliano TRIBUTE (Decor)": 990,

    # BEAUTY LINK, BRAND NUMBERS
    "Beauty": 12, "Girls (Beauty)": 17, "Tingeling (Beauty)": 18,
    "NO NAME BRAND (Beauty 1)": 21, "Golden Sands (Beauty)": 37, "Folk (Beauty)": 44,
    "NO NAME BRAND (Beauty 2)": 96, "Spectacular": 133, "Spectacutar!": 134,
    "Chanel (Beauty)": 257, "Sunny Bunny (Beauty)": 292, "Epiphany": 352,
    "Whip My Hair": 358, "Window on the World (Beauty)": 382, "Riviera (Beauty)": 412,
    "Young Hollywood (Beauty)": 417, "Film Theory": 423, "Jewelry Design": 473,
    "Glamdalls": 532, "Hot Buys (Beauty)": 679, "Callies Picks (Beauty)": 772,
    "Ms. TQ": 773, "SubCouture (Beauty)": 785, "INKD (Beauty)": 846,
    "Red Mod (Beauty)": 930, "FENDI": 979, "FY": 1009,

    # FASHION LINK, BRAND NUMBERS
    "Bonjour Bizou/Pretty n Love": 7, "Fudge (Fashion)": 8, "Voile": 10,
    "Rio (Fashion 1)": 12, "Girls (Fashion)": 13, "Fashion": 14, "Rio (Fashion 2)": 15,
    "Chanel (Fashion)": 16, "Fallen Angel": 17, "Tingeling (Fashion)": 18,
    "Fudge (Fashion v2)": 19, "NO NAME BRAND (Fashion 1)": 20, "NO NAME BRAND (Fashion 2)": 21,
    "Folk (Fashion)": 23, "DKNY": 26, "Mary Kate and Ashley Brand": 31,
    "Steff (and something scribble)": 32, "Fashion Design": 43,
    "Fallen Angel DECOR (Fashion)": 45, "Evil Panda": 51, "Gucci": 63,
    "By Jordache": 75, "Decades": 88, "Evil Panda (Fashion v2)": 92, "Philosophy": 93,
    "No name brand (Fashion)": 96, "Limited Edition": 101, "Elle": 102,
    "Antidote (Fashion)": 117, "13may": 131, "Archive": 134, "Miss Sixty": 146,
    "Kohl's": 150, "Missgirls": 159, "Baby Phat": 167,
    "Tingeling Couture (Fashion)": 183, "Holiday Boutique": 197, "Otto": 204,
    "Stylein": 223, "AmpClaire": 226, "Chanel (Fashion v2)": 257, "Hot Buys": 261,
    "MSW Store": 303, "Stardoll and the City": 308, "Mortel Kiss": 310,
    "Wild Candy": 323, "No name brand (Fashion 3)": 342, "Pretty n Pink Heart Shop": 354,
    "Riviera (Fashion)": 412, "Young Hollywood (Fashion)": 417, "Moschino": 440,
    "Museum Mile (Fashion)": 468, "No name brand (Fashion 4)": 496, "Velvet Orchid": 528,
    "Original Future": 566, "Anne Sui TRIBUTE": 573, "Dolce Gabbana TRIBUTE": 597,
    "Millionaire Mansion (Fashion)": 604, "Junior Gaultier": 637,
    "No name brand (Fashion 5)": 646, "John Galliano (Fashion)": 649,
    "Roberto Cavalli": 650, "Nelly": 655, "Denim Supply": 658, "Royalty (Fashion)": 660,
    "Hot Buys (Fashion v2)": 723, "Fever": 727,
    "Gloomiest Valli COUTURE Tribute": 732, "Loopbaute": 738, "Cheap Monday": 771,
    "Callies Picks (Fashion)": 772, "SubCouture (Fashion)": 781,
    "Saint Laurent Paris TRIBUTE": 788, "Strike & Pose": 814, "INKD (Fashion)": 846,
    "Versace": 876, "Dior": 881, "Pois (Fashion)": 889, "Red Mod (Fashion)": 930,
    "Wild Candy COUTURE": 953, "Minimum Millenium TRIBUTE": 959, "Balmain TRIBUTE": 961,
    "L&E - RE": 967, "Runaway": 974, "DeLaRenta TRIBUTE": 978, "Miu Miu": 983,
    "Marc Jacobs TRIBUTE": 993, "MCQUEEN TRIBUTE": 994, "Pearls": 1001,
    "Tom Ford TRIBUTE": 1023
}

# Çerezler başlangıçta boş olacak, kullanıcıdan alınacak
YOUR_STARDOLL_COOKIES = {}

# Arama durumunu kontrol eden değişken
is_searching = False 

# ==============================================================================
# ANA BOT MANTIĞI VE API ETKİLEŞİMLERİ
# ==============================================================================

def get_stardoll_bazaar_items(item_type, currency_type, min_price, max_price, brand_id=None):
    global YOUR_STARDOLL_COOKIES 

    if not YOUR_STARDOLL_COOKIES:
        return []

    base_url = "https://www.stardoll.com/en/com/user/getStarBazaar.php?"
    params = {
        "search": "",
        "type": item_type,
        "currencyType": currency_type,
        "minPrice": min_price,
        "maxPrice": max_price
    }
    if brand_id and item_type != "hair": 
        params["brands"] = brand_id

    try:
        s = requests.Session()
        s.cookies.update(YOUR_STARDOLL_COOKIES)
        response = s.get(base_url, params=params)
        response.raise_for_status()

        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Uyarı: Geçerli bir JSON yanıtı alınamadı, boş liste döndürülüyor. URL: {response.url}")
            return []

        if "items" in data:
            return data["items"]
        else:
            print(f"Uyarı: JSON yanıtında 'items' anahtarı bulunamadı. URL: {response.url}, Yanıt: {data}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Uyarı: Ağ bağlantısı hatası oluştu: {e}. URL: {response.url}")
        return []
    except Exception as e:
        print(f"Uyarı: Beklenmedik bir hata oluştu: {e}. URL: {response.url}")
        return []

def filter_items_by_name(items, keyword):
    if not keyword:
        return items
    return [item for item in items if keyword.lower() in item.get("name", "").lower()]

# ==============================================================================
# TKINTER UYGULAMA MANTIĞI
# ==============================================================================

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg=APP_BG_COLOR) 
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style="Pink.TFrame") 

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

def copy_to_clipboard(text_to_copy):
    root.clipboard_clear()
    root.clipboard_append(text_to_copy)
    messagebox.showinfo("Kopyalandı", f"'{text_to_copy}' panoya kopyalandı!")

def load_image_from_url(url, size=(100, 100)):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image_data = io.BytesIO(response.content)
        img = Image.open(image_data)
        img = img.resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        return photo
    except Exception as e:
        print(f"Görsel yüklenirken hata oluştu {url}: {e}")
        return None

def display_items(items_to_display, currency_type, item_type):
    # Önceki sonuçları temizle
    for widget in results_frame.scrollable_frame.winfo_children():
        widget.destroy()

    if items_to_display:
        tk.Label(results_frame.scrollable_frame, text=f"Bulunan {len(items_to_display)} öğe:", font=("Arial", 12, "bold"), bg=ITEM_BG_COLOR).pack(pady=5)
        
        for item in items_to_display:
            item_name = item.get("name", "Bilinmeyen İsim")
            item_cost = item.get("sellPrice", "Bilinmeyen Fiyat")
            seller_id = item.get("sellerId", "Bilinmeyen Satıcı ID")
            
            full_image_url = None
            if item_type == "hair":
                custom_item_id = item.get("customItemId")
                if custom_item_id and len(str(custom_item_id)) >= 3:
                    first_three_digits = str(custom_item_id)[:3]
                    full_image_url = f"http://www.sdcdn.com/customitems/130/{first_three_digits}/435/{custom_item_id}.png"
            else: 
                item_id = item.get("itemId")
                if item_id:
                    full_image_url = f"http://cdn.stardoll.com/itemimages/130/0/66/{item_id}.png"
            

            item_frame = tk.Frame(results_frame.scrollable_frame, bd=2, relief="groove", padx=10, pady=10, bg=ITEM_BG_COLOR)
            item_frame.pack(fill="x", padx=5, pady=5)

            if full_image_url:
                photo = load_image_from_url(full_image_url, size=(100, 100))
                if photo:
                    img_label = tk.Label(item_frame, image=photo, bg=ITEM_BG_COLOR)
                    img_label.image = photo 
                    img_label.pack(side="left", padx=10)
                else:
                    tk.Label(item_frame, text="Görsel Yüklenemedi", fg="red", width=12, height=5, bg=ITEM_BG_COLOR).pack(side="left", padx=10)
            else:
                tk.Label(item_frame, text="Görsel Yok", fg="gray", width=12, height=5, bg=ITEM_BG_COLOR).pack(side="left", padx=10)

            info_frame = tk.Frame(item_frame, bg=ITEM_BG_COLOR)
            info_frame.pack(side="left", anchor="n")

            tk.Label(info_frame, text=f"Adı: {item_name}", font=("Arial", 10, "bold"), anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")
            tk.Label(info_frame, text=f"Fiyat: {item_cost} {'Stardollars' if currency_type == 1 else 'Starcoins'}", anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")
            
            if item_type == "hair":
                tk.Label(info_frame, text=f"Custom Item ID: {item.get('customItemId', 'Bilinmiyor')}", anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")
            else:
                tk.Label(info_frame, text=f"Item ID: {item.get('itemId', 'Bilinmiyor')}", anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")

            seller_id_frame = tk.Frame(info_frame, bg=ITEM_BG_COLOR)
            seller_id_frame.pack(fill="x", anchor="w")
            tk.Label(seller_id_frame, text=f"Satıcı ID: {seller_id}", anchor="w", bg=ITEM_BG_COLOR).pack(side="left")
            copy_button = tk.Button(seller_id_frame, text="Kopyala", command=lambda s_id=seller_id: copy_to_clipboard(str(s_id)), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
            copy_button.pack(side="left", padx=5)

            tk.Label(info_frame, text=f"Satıcı Profili: https://www.stardoll.com/en/user/sellItems.php?id={seller_id}", fg="blue", cursor="hand2", anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")
            
            if item_type == "hair":
                creator_user_id = item.get("creatorUserID", "Bilinmiyor")
                designer_name = item.get("name", "Bilinmiyor").replace("Designed by ", "") 
                alprice = item.get("alprice", "Bilinmiyor")
                original_price_hair = item.get("originalPrice", "Bilinmiyor")
                original_price_currency_hair = "Stardollars" if item.get("originalPriceCurrencyType") == 1 else \
                                               "Starcoins" if item.get("originalPriceCurrencyType") == 2 else \
                                               "Bilinmiyor"
                tk.Label(info_frame, text=f"Tasarımcı: {designer_name} (ID: {creator_user_id})", anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")
                tk.Label(info_frame, text=f"Parça Sayısı (alprice): {alprice}", anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")
                tk.Label(info_frame, text=f"Orijinal Fiyat: {original_price_hair} {original_price_currency_hair}", anchor="w", bg=ITEM_BG_COLOR).pack(fill="x")
    else:
        tk.Label(results_frame.scrollable_frame, text="Belirtilen filtreleme kriterlerine uyan öğe bulunamadı.", fg="blue", font=("Arial", 12), bg=APP_BG_COLOR).pack(pady=20)


def start_search_thread(is_guarantee_search):
    """Aramayı ayrı bir thread'de başlatan fonksiyon."""
    global is_searching
    if is_searching:
        messagebox.showwarning("Uyarı", "Zaten bir arama devam ediyor.")
        return

    # Durumları sıfırla ve butonları ayarla
    is_searching = True
    toggle_search_buttons(True) # Arama başladığında butonları devre dışı bırak

    # Sonuçları temizle
    for widget in results_frame.scrollable_frame.winfo_children():
        widget.destroy()

    # Çerez kontrolü
    if not YOUR_STARDOLL_COOKIES:
        messagebox.showwarning("Çerez Hatası", "Lütfen önce çerez bilgilerinizi girin ve kaydedin.")
        is_searching = False
        toggle_search_buttons(False) # Arama başlamadıysa butonları tekrar etkinleştir
        return

    # Arama parametrelerini al
    try:
        min_price_input = int(min_price_entry.get())
        max_price_input = int(max_price_entry.get())
    except ValueError:
        messagebox.showerror("Hata", "Fiyat alanlarına geçerli bir sayı girin.")
        is_searching = False
        toggle_search_buttons(False) # Arama başlamadıysa butonları tekrar etkinleştir
        return

    if min_price_input < 2:
        messagebox.showerror("Hata", "Minimum fiyat 2'den az olamaz.")
        is_searching = False
        toggle_search_buttons(False)
        return
    if max_price_input < min_price_input:
        messagebox.showerror("Hata", "Maksimum fiyat, minimum fiyattan küçük olamaz.")
        is_searching = False
        toggle_search_buttons(False)
        return
    if max_price_input > 600:
        messagebox.showerror("Hata", "Maksimum fiyat 600'den fazla olamaz.")
        is_searching = False
        toggle_search_buttons(False)
        return

    item_type = item_type_var.get().lower()
    currency_type = int(currency_type_var.get().split(' ')[0])
    selected_brand_name = brand_name_var.get()
    search_keyword = keyword_entry.get().strip()
    guarantee_keyword = guarantee_keyword_entry.get().strip() if is_guarantee_search else ""
    brand_id = BRAND_IDS.get(selected_brand_name)

    # Arama işlemini arka planda çalıştır
    search_thread = threading.Thread(target=perform_search, args=(
        item_type, currency_type, min_price_input, max_price_input, brand_id, 
        search_keyword, guarantee_keyword, is_guarantee_search
    ))
    search_thread.start()

def perform_search(item_type, currency_type, min_price_input, max_price_input, brand_id, search_keyword, guarantee_keyword, is_guarantee_search_mode):
    global is_searching

    all_items = []
    step_size = 25 

    progress_label = tk.Label(results_frame.scrollable_frame, text="Arama yapılıyor...", font=("Arial", 12), bg=ITEM_BG_COLOR, fg="blue")
    progress_label.pack(pady=10)
    root.update_idletasks()

    current_min_price = min_price_input
    found_guarantee_item = False

    while current_min_price <= max_price_input and is_searching: # is_searching kontrolü eklendi
        current_max_price = min(current_min_price + step_size -1, max_price_input)
        
        items_from_range = get_stardoll_bazaar_items(item_type, currency_type, current_min_price, current_max_price, brand_id)
        
        # Deduplication ve garanti arama kontrolü
        for item in items_from_range:
            item_identifier = item.get("customItemId") if item_type == "hair" else item.get("itemId")
            price = item.get("sellPrice")
            
            if item_identifier is not None and (item_identifier, price) not in [(x.get("customItemId") if item_type=="hair" else x.get("itemId"), x.get("sellPrice")) for x in all_items]:
                all_items.append(item)

                if is_guarantee_search_mode and guarantee_keyword.lower() in item.get("name", "").lower():
                    found_guarantee_item = True
                    break # Garanti ürün bulundu, döngüyü kır

        if found_guarantee_item:
            break # Dış döngüyü de kır

        current_min_price = current_max_price + 1
        
        progress_label.config(text=f"Arama yapılıyor: {current_min_price - step_size} - {current_max_price} SD aralığı tamamlandı. Toplam {len(all_items)} benzersiz öğe bulundu...")
        root.update_idletasks()
        
        # API'ye yük bindirmemek için kısa bir gecikme
        time.sleep(0.5) 

    progress_label.destroy()

    if all_items:
        if item_type == "hair":
            all_items.sort(key=lambda x: int(x.get("customItemId", "999999999")))
        else:
            all_items.sort(key=lambda x: int(x.get("itemId", "999999999")))

        # Garanti arama modundaysa sadece bulunan ürünü göster
        if is_guarantee_search_mode and found_guarantee_item:
            final_display_items = [item for item in all_items if guarantee_keyword.lower() in item.get("name", "").lower()]
            if not final_display_items: # Eğer dedup sonrası kaybolduysa (nadiren)
                final_display_items = [item for item in items_from_range if guarantee_keyword.lower() in item.get("name", "").lower()]
            messagebox.showinfo("Ürün Bulundu!", f"'{guarantee_keyword}' anahtar kelimesine sahip ürün bulundu!")
        else:
            final_display_items = filter_items_by_name(all_items, search_keyword)

        display_items(final_display_items, currency_type, item_type)
    else:
        tk.Label(results_frame.scrollable_frame, text="Öğe çekilemedi veya herhangi bir öğe bulunamadı.\nLütfen giriş bilgilerinizi (çerezleri) kontrol edin.", fg="red", font=("Arial", 12), bg=APP_BG_COLOR).pack(pady=20)
    
    is_searching = False
    toggle_search_buttons(False) # Arama bitince butonları tekrar etkinleştir

def toggle_search_buttons(is_running):
    """Arama butonlarını ve durdur butonunu etkinleştirir/devre dışı bırakır."""
    search_button.config(state="disabled" if is_running else "normal")
    guarantee_search_button.config(state="disabled" if is_running else "normal")
    pause_resume_button.config(state="normal" if is_running else "disabled")
    if is_running:
        pause_resume_button.config(text="Durdur")
    else:
        pause_resume_button.config(text="Başlat") # Durdurulmuşsa tekrar başlatmak için

def pause_resume_search():
    """Aramayı duraklatma/devam ettirme işlevi."""
    global is_searching
    if is_searching:
        is_searching = False
        pause_resume_button.config(text="Devam Et")
        status_label.config(text="Arama Duraklatıldı.", fg="orange")
    else:
        # Devam ettirme için yeni bir thread başlatmak gerekir
        # Not: Bu basit bir pause/resume değil, duraklatıp yeni bir arama başlatma gibi çalışır.
        # Gerçek bir pause/resume için daha karmaşık thread yönetimi gerekir.
        # Şimdilik sadece durdurma işlevi yeterli olacaktır, devam ettirme için yeniden başlatmak daha kolay.
        messagebox.showinfo("Bilgi", "Aramaya devam etmek için 'Ara' veya 'Garanti Ara' butonuna tekrar basın.")
        # Duraklatıldıysa ve kullanıcı devam et butonuna basarsa, aslında yeni bir arama başlatılmalı.
        # Bu senaryo için 'Devam Et' butonu kaldırılabilir veya işlevi basitleştirilebilir.
        # Şimdilik, sadece durdurma işlevi üzerine odaklanalım.
        # pause_resume_button.config(text="Durdur") # Bu kısmı kaldırdım, manuel yeniden başlatma için
        # status_label.config(text="Arama Devam Ediyor...", fg="blue")
        # start_search_thread(is_guarantee_search_mode_global) # Global değişken gerekli
        pass # Bu kısım şimdilik işlem yapmasın

# ==============================================================================
# TKINTER ARAYÜZ KURULUMU VE RENK PALETİ
# ==============================================================================

root = tk.Tk()
root.title("Stardoll Starbazaar Filtreleyici")
root.geometry("900x750")

# Renk paleti tanımlamaları
APP_BG_COLOR = "#FFD1DC"  # LightPink
FRAME_BG_COLOR = "#FFC0CB" # Pink
BUTTON_BG_COLOR = "#FF69B4" # HotPink
BUTTON_FG_COLOR = "white"   # Beyaz yazı
ITEM_BG_COLOR = "#FFE4E1"   # MistyRose (Ürün kutucukları için daha açık bir pembe)
LABEL_TEXT_COLOR = "#8B0000" # DarkRed (Koyu pembe tonlarına uyumlu bir yazı rengi)

root.configure(bg=APP_BG_COLOR) 

# ttk stilleri
style = ttk.Style()
style.theme_use('clam') 
style.configure("Pink.TFrame", background=FRAME_BG_COLOR)
style.configure("Pink.TLabelframe", background=FRAME_BG_COLOR, foreground=LABEL_TEXT_COLOR)
style.configure("Pink.TLabelframe.Label", background=FRAME_BG_COLOR, foreground=LABEL_TEXT_COLOR)
style.configure("Pink.TButton", background=BUTTON_BG_COLOR, foreground=BUTTON_FG_COLOR, font=('Arial', 10, 'bold'))
style.map("Pink.TButton", background=[('active', '#FF1493')]) 
style.configure("Pink.TOptionMenu", background=FRAME_BG_COLOR, foreground="black", arrowcolor="black")

# ----- Çerez Giriş Ekranı -----
cookie_input_frame = tk.Frame(root, bg=FRAME_BG_COLOR, bd=2, relief="groove")
cookie_input_frame.pack(fill="both", expand=True, padx=20, pady=20)

tk.Label(cookie_input_frame, text="Stardoll Oturum Çerezlerinizi Buraya Girin", font=("Arial", 14, "bold"), bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).pack(pady=10)
tk.Label(cookie_input_frame, text="Tarayıcınızdan F12 (Geliştirici Araçları) > Uygulama/Depolama > Çerezler bölümünden Stardoll.com için aşağıdaki çerezleri kopyalayıp yapıştırın.", wraplength=700, justify="left", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).pack(pady=5)
tk.Label(cookie_input_frame, text="Bu çerezler hesabınıza giriş yapmanızı sağlar ve Stardoll ile iletişim kurmak için gereklidir.", wraplength=700, justify="left", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).pack(pady=5)


# Çerez giriş kutucukları ve açıklamaları
cookie_entries = {}
required_cookie_names = ["OAID", "pdhUser", "SDIT", "SESSID", "vc"] 

for i, cookie_name in enumerate(required_cookie_names):
    cookie_row_frame = tk.Frame(cookie_input_frame, bg=FRAME_BG_COLOR)
    cookie_row_frame.pack(fill="x", padx=50, pady=2)
    
    tk.Label(cookie_row_frame, text=f"{cookie_name}:", width=10, anchor="e", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).pack(side="left")
    entry = tk.Entry(cookie_row_frame, width=60, bg="white", fg="black")
    entry.pack(side="left", fill="x", expand=True, padx=5)
    cookie_entries[cookie_name] = entry

tk.Label(cookie_input_frame, text="\nNot: 'SESSID' yerine tarayıcınızda 'PHPSESSID' veya benzeri bir ad görebilirsiniz. Doğru değeri yapıştırdığınızdan emin olun.", wraplength=700, justify="left", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).pack(pady=10)


def save_cookies_and_show_main_app_single_entries():
    global YOUR_STARDOLL_COOKIES
    entered_cookies = {}
    missing_cookies = []

    for name, entry_widget in cookie_entries.items():
        value = entry_widget.get().strip()
        if not value:
            missing_cookies.append(name)
        entered_cookies[name] = value
    
    if missing_cookies:
        response = messagebox.askyesno("Çerez Eksikliği", 
                                      f"Aşağıdaki önemli çerezler eksik veya boş:\n{', '.join(missing_cookies)}\n\n"
                                      "Uygulama düzgün çalışmayabilir. Yine de devam etmek ister misiniz?")
        if not response:
            return

    YOUR_STARDOLL_COOKIES = entered_cookies
    messagebox.showinfo("Başarılı", "Çerezler başarıyla kaydedildi!")
    
    cookie_input_frame.pack_forget()
    main_app_frame.pack(padx=10, pady=10, fill="both", expand=True)

save_cookie_button = tk.Button(cookie_input_frame, text="Çerezleri Kaydet ve Devam Et", command=save_cookies_and_show_main_app_single_entries, bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=('Arial', 10, 'bold'))
save_cookie_button.pack(pady=10)

# ----- Ana Uygulama Ekranı (Başlangıçta gizli) -----
main_app_frame = tk.Frame(root, bg=APP_BG_COLOR) 

# Girdiler (main_app_frame içindeki input_frame içinde)
input_frame = tk.LabelFrame(main_app_frame, text="Filtreleme Kriterleri", padx=10, pady=10, bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR)
input_frame.pack(padx=10, pady=10, fill="x")

# Öğe Türü
tk.Label(input_frame, text="Öğe Türü:", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=2)
item_type_options = ["Fashion", "Interior", "Jewelry", "Hair"]
item_type_var = tk.StringVar(root)
item_type_var.set(item_type_options[0])
item_type_menu = tk.OptionMenu(input_frame, item_type_var, *item_type_options)
item_type_menu.config(bg="white", fg="black") 
item_type_menu.grid(row=0, column=1, sticky="ew", pady=2)

# Para Birimi
tk.Label(input_frame, text="Para Birimi:", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).grid(row=1, column=0, sticky="w", pady=2)
currency_type_options = ["1 (Stardollars)", "2 (Starcoins)"]
currency_type_var = tk.StringVar(root)
currency_type_var.set(currency_type_options[0])
currency_type_menu = tk.OptionMenu(input_frame, currency_type_var, *currency_type_options)
currency_type_menu.config(bg="white", fg="black") 
currency_type_menu.grid(row=1, column=1, sticky="ew", pady=2)

# Minimum Fiyat
tk.Label(input_frame, text="Minimum Fiyat (min 2):", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).grid(row=2, column=0, sticky="w", pady=2)
min_price_entry = tk.Entry(input_frame, bg="white", fg="black")
min_price_entry.insert(0, "2")
min_price_entry.grid(row=2, column=1, sticky="ew", pady=2)

# Maksimum Fiyat
tk.Label(input_frame, text="Maksimum Fiyat (max 600):", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).grid(row=3, column=0, sticky="w", pady=2)
max_price_entry = tk.Entry(input_frame, bg="white", fg="black")
max_price_entry.insert(0, "600")
max_price_entry.grid(row=3, column=1, sticky="ew", pady=2)

# Marka Adı
tk.Label(input_frame, text="Marka Adı:", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).grid(row=4, column=0, sticky="w", pady=2)
sorted_brand_names = sorted([name for name in BRAND_IDS.keys() if name is not None and name != "Seçiniz (Tüm Markalar)"])
display_brand_options = ["Seçiniz (Tüm Markalar)"] + sorted_brand_names
brand_name_var = tk.StringVar(root)
brand_name_var.set(display_brand_options[0])
brand_name_menu = tk.OptionMenu(input_frame, brand_name_var, *display_brand_options)
brand_name_menu.config(bg="white", fg="black") 
brand_name_menu.grid(row=4, column=1, sticky="ew", pady=2)

# Anahtar Kelime (Normal Arama İçin)
tk.Label(input_frame, text="Anahtar Kelime (Normal):", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).grid(row=5, column=0, sticky="w", pady=2)
keyword_entry = tk.Entry(input_frame, bg="white", fg="black")
keyword_entry.grid(row=5, column=1, sticky="ew", pady=2)

# Garanti Arama Anahtar Kelimesi
tk.Label(input_frame, text="Anahtar Kelime (Garanti Arama):", bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR).grid(row=6, column=0, sticky="w", pady=2)
guarantee_keyword_entry = tk.Entry(input_frame, bg="white", fg="black")
guarantee_keyword_entry.grid(row=6, column=1, sticky="ew", pady=2)


input_frame.grid_columnconfigure(1, weight=1)

# Arama Butonları ve Durum
button_frame = tk.Frame(input_frame, bg=FRAME_BG_COLOR)
button_frame.grid(row=7, column=0, columnspan=2, pady=10)

search_button = tk.Button(button_frame, text="Normal Ara", command=lambda: start_search_thread(False), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=('Arial', 10, 'bold'))
search_button.pack(side="left", padx=5)

guarantee_search_button = tk.Button(button_frame, text="Garanti Ara", command=lambda: start_search_thread(True), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=('Arial', 10, 'bold'))
guarantee_search_button.pack(side="left", padx=5)

pause_resume_button = tk.Button(button_frame, text="Durdur", command=pause_resume_search, bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=('Arial', 10, 'bold'), state="disabled")
pause_resume_button.pack(side="left", padx=5)

status_label = tk.Label(input_frame, text="Hazır.", bg=FRAME_BG_COLOR, fg="green", font=("Arial", 10, "italic"))
status_label.grid(row=8, column=0, columnspan=2, pady=5)


# Sonuçlar
output_main_frame = tk.LabelFrame(main_app_frame, text="Sonuçlar", padx=10, pady=10, bg=FRAME_BG_COLOR, fg=LABEL_TEXT_COLOR)
output_main_frame.pack(padx=10, pady=10, fill="both", expand=True)

results_frame = ScrollableFrame(output_main_frame)
results_frame.pack(fill="both", expand=True)


root.mainloop()